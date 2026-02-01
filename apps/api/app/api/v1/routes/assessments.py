"""
评估结果相关 API
包括 PDF 下载功能
"""

from fastapi import APIRouter, Path, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models import Assessment
from app.database import get_db
from app.services.report_builder import build_report_data
from app.services.pdf_report import generate_pdf
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_access(assessment: Assessment, user_id: Optional[str] = None) -> bool:
    """
    验证用户是否有权访问该评估
    
    Args:
        assessment: Assessment 实例
        user_id: 用户 ID（可选，从请求中获取）
    
    Returns:
        True 如果有权限，False 否则
    """
    # 如果提供了 user_id，检查是否匹配
    if user_id and assessment.user_id:
        return assessment.user_id == user_id
    
    # 如果没有 user_id，暂时允许访问（实际生产环境需要更严格的验证）
    # TODO: 添加 session 验证或其他安全机制
    return True


@router.get("/{assessment_id}/report.pdf")
async def download_pdf_report(
    assessment_id: str = Path(..., description="评估 ID"),
    user_id: Optional[str] = Query(None, description="用户 ID（用于权限验证）"),
    db: Session = Depends(get_db)
):
    """
    下载 PDF 报告
    
    正确的逻辑：
    1. 从数据库获取 Assessment（已经算好的）
    2. 直接用 assessment.result_data / decision_summary_data / input_data
    3. build_report_data() - 只组装数据，不重新计算
    4. generate_pdf() - 生成 PDF
    
    PDF = 展示层，不是计算层
    
    权限要求：
    - unlocked_tier != "none"
    - 用户必须有权访问该评估
    """
    # 1. 查询 Assessment（已经算好的）
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    # 2. 验证访问权限
    if not _verify_access(assessment, user_id):
        raise HTTPException(status_code=403, detail="无权访问该评估")
    
    # 3. 验证解锁状态
    unlocked_tier = (assessment.unlocked_tier or "none").strip().lower()
    if unlocked_tier == "none":
        raise HTTPException(
            status_code=403,
            detail="需要解锁后才能下载 PDF 报告。请先完成支付。"
        )
    
    # 4. 验证是否有评估结果数据
    if not assessment.result_data or not assessment.decision_summary_data:
        raise HTTPException(
            status_code=400,
            detail="评估结果数据不完整，无法生成 PDF。请重新进行评估。"
        )
    
    # 5. 组装报告数据（直接从数据库读取，不重新计算）
    try:
        report_data = build_report_data(assessment)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"组装报告数据失败：{str(e)}"
        )
    
    # 6. 生成 PDF（展示层）
    try:
        pdf_bytes = generate_pdf(report_data)
        # ✅ 最小化日志记录（PDF 生成成功）
        logger.info(f"[PDF_GENERATE] assessment_id={assessment_id}, unlocked_tier={unlocked_tier}, success=true")
    except Exception as e:
        # ✅ 最小化日志记录（PDF 生成失败）
        logger.error(f"[PDF_GENERATE] assessment_id={assessment_id}, unlocked_tier={unlocked_tier}, success=false, error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"生成 PDF 失败：{str(e)}"
        )
    
    # 7. 返回 PDF
    filename = f"IberComply_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

