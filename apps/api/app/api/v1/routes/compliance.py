from fastapi import APIRouter, Query, Depends, HTTPException, Path
from pydantic import BaseModel
from app.models import Assessment
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
from app.schemas.assessment import RiskAssessmentRequest, RiskAssessmentResponse, Finding, DecisionSummary
from app.schemas.compliance import AssessmentOut
from app.services.risk_engine import assess_risk_v2, assess_risk_v3
from app.services.decision_engine import compute_decision_summary
from app.services.decision_templates import normalize_tier
from app.services.stripe_service import verify_payment_session
from app.database import get_db

router = APIRouter()


def _filter_pro_findings(findings, unlocked_tier: str):
    if unlocked_tier != "none":
        return findings

    def _is_pro_only(item) -> bool:
        if isinstance(item, dict):
            return bool(item.get("pro_only"))
        if hasattr(item, "pro_only"):
            return bool(getattr(item, "pro_only"))
        return False

    return [f for f in findings if not _is_pro_only(f)]


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_compliance(
    request: RiskAssessmentRequest,
    session_id: Optional[str] = Query(None, description="Stripe Checkout Session ID for payment verification"),
    assessment_id: Optional[str] = Query(None, description="Assessment ID to get latest unlocked_tier"),
    db: Session = Depends(get_db)
):
    """
    合规风险评估接口 v3
    整合 Risk Engine 和 Decision Engine (按 stage 分支)
    返回: risk_score + risk_level + findings + decision_summary
    
    前端只渲染 decision_summary，不再写业务判断
    
    如果提供了 session_id，会根据支付状态自动解锁对应层级的内容
    """
    # 评估风险（Risk Engine v3 - 配置驱动版本，输出增强 meta）
    risk_score, risk_level, findings, meta = assess_risk_v3(request)
    
    # ✅ 核心修复：获取 unlocked_tier（必须以数据库为准）
    unlocked_tier_value = "none"
    
    # ✅ 优先：如果提供了 assessment_id，从数据库获取最新的 unlocked_tier（权威来源）
    if assessment_id:
        assessment_db = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
        if assessment_db:
            # ✅ 关键：即使 unlocked_tier 是 None 或空字符串，也要读取（可能 webhook 刚更新）
            unlocked_tier_value = normalize_tier(assessment_db.unlocked_tier)
            logger.info("[ASSESS] assessment found, unlocked_tier normalized=%s", unlocked_tier_value)
    
    # 其次：如果提供了 session_id 且还没有从 assessment_id 获取到，验证支付状态
    if session_id and unlocked_tier_value == "none":
        payment_session = verify_payment_session(session_id, db)
        if payment_session and payment_session.status == "paid":
            # 根据 tier 映射到 decision_engine 格式
            if payment_session.tier == "basic":
                unlocked_tier_value = "basic_15"
            elif payment_session.tier == "expert":
                unlocked_tier_value = "expert_39"
    
    # ✅ 核心修复：生成或获取 assessment_id（关键：确保贯穿整个支付流程）
    current_assessment_id = assessment_id  # 保存传入的 assessment_id
    
    # 如果提供了 session_id，尝试从 PaymentSession 获取关联的 assessment_id
    if session_id and not current_assessment_id:
        payment_session = verify_payment_session(session_id, db)
        if payment_session and payment_session.assessment_id:
            current_assessment_id = payment_session.assessment_id
    
    # 如果还没有 assessment_id，生成一个新的
    if not current_assessment_id:
        current_assessment_id = f"assessment_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"
    
    # ✅ 关键：如果 assessment_id 已存在，再次从数据库确认最新的 unlocked_tier（可能 webhook 刚更新）
    # ⚠️ 重要：必须在生成 decision_summary 之前，再次从数据库读取最新的 unlocked_tier
    if current_assessment_id:
        assessment_db_final = db.query(Assessment).filter(Assessment.assessment_id == current_assessment_id).first()
        if assessment_db_final:
            # ✅ 使用数据库中的最新值（webhook 可能刚更新）
            latest_unlocked_tier = normalize_tier(assessment_db_final.unlocked_tier)
            if latest_unlocked_tier != unlocked_tier_value:
                logger.warning(
                    "[ASSESS] unlocked_tier updated before decision: %s -> %s",
                    unlocked_tier_value,
                    latest_unlocked_tier,
                )
                unlocked_tier_value = latest_unlocked_tier
            else:
                logger.info("[ASSESS] using unlocked_tier=%s (from DB)", unlocked_tier_value)
    
    # ✅ 付费字段控制：未解锁时移除 pro_only findings
    findings = _filter_pro_findings(findings, unlocked_tier_value)

    # 转换 findings 为 dict 格式（用于 decision_engine）
    findings_dict = [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ if hasattr(f, "__dict__") else f for f in findings]

    # ✅ 生成决策建议（Decision Engine 按 stage 产出唯一结论）
    # 关键：使用最新的 unlocked_tier_value（从数据库读取的权威值）
    logger.info("[ASSESS] generating decision_summary with unlocked_tier=%s", unlocked_tier_value)
    decision_summary = compute_decision_summary(
        stage=request.stage,
        industry=request.industry,
        risk_score=risk_score,
        risk_level=risk_level,
        monthly_income=request.monthly_income,
        employee_count=request.employee_count,
        findings=findings_dict,
        meta=meta,
        unlocked_tier=unlocked_tier_value,  # ✅ 使用从数据库读取的最新值
    )
    
    # ✅ 验证付费内容是否正确生成（调试用）
    if unlocked_tier_value != "none":
        logger.info(
            "[ASSESS] decision_summary counts: reasons=%s actions=%s risks=%s",
            len(decision_summary.reasons),
            len(decision_summary.recommended_actions),
            len(decision_summary.risk_if_ignore),
        )
    
    # 确保 Assessment 记录存在（如果不存在则创建）
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == current_assessment_id
    ).first()
    
    # ✅ 准备保存到数据库的数据
    result_data = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "findings": [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ if hasattr(f, "__dict__") else f for f in findings],
        "meta": meta,
    }
    
    decision_summary_dict = decision_summary.model_dump() if hasattr(decision_summary, "model_dump") else decision_summary.__dict__
    
    input_data = {
        "stage": request.stage,
        "industry": request.industry,
        "monthly_income": request.monthly_income,
        "employee_count": request.employee_count,
        "has_pos": request.has_pos,
        "signals": request.signals,
    }
    
    if not assessment:
        # 从 request 中获取 user_id（如果有的话，前端可以通过 header 传递）
        user_id = None  # 可以从 request headers 或其他地方获取
        assessment = Assessment(
            assessment_id=current_assessment_id,
            user_id=user_id,
            unlocked_tier=unlocked_tier_value,
            result_data=result_data,
            decision_summary_data=decision_summary_dict,
            input_data=input_data,
        )
        db.add(assessment)
        db.commit()
    else:
        # ✅ 如果 assessment 已存在，更新 unlocked_tier 和结果数据
        assessment.unlocked_tier = unlocked_tier_value
        assessment.result_data = result_data
        assessment.decision_summary_data = decision_summary_dict
        assessment.input_data = input_data
        db.commit()
    
    return RiskAssessmentResponse(
        id=current_assessment_id,  # 返回 assessment_id（关键：前端必须使用这个）
        risk_score=risk_score,
        risk_level=risk_level,
        findings=findings,
        decision_summary=decision_summary,
        meta=meta  # ✅ 新增：返回 meta（包含 industry_key, tags, matched_triggers）
    )


@router.get("/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: str = Path(..., description="Assessment ID"),
    # 可选：原始请求数据（用于重新生成 decision_summary）
    stage: Optional[str] = Query(None, description="Stage (PRE_AUTONOMO/AUTONOMO/SL)"),
    industry: Optional[str] = Query(None, description="Industry key"),
    monthly_income: Optional[float] = Query(None, description="Monthly income"),
    employee_count: Optional[int] = Query(None, description="Employee count"),
    has_pos: Optional[bool] = Query(None, description="Has POS"),
    db: Session = Depends(get_db)
):
    """
    根据 assessment_id 获取评估的解锁状态（权威来源）
    
    如果提供了原始请求数据（stage, industry, etc.），会重新生成 decision_summary
    否则只返回基本信息（unlocked_tier）
    
    返回：assessment_id, user_id, unlocked_tier, stripe_session_id, decision_summary (可选)
    """
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # tier 标准化，避免 basic/basic_15/BASIC_15 比较失败
    unlocked = normalize_tier(getattr(assessment, "unlocked_tier", None))
    
    # 如果提供了原始请求数据，重新生成 decision_summary
    decision_summary = None
    if stage and industry and monthly_income is not None and employee_count is not None and has_pos is not None:
        # 构建请求对象（signals 可以为空，后端会兜底）
        from app.schemas.assessment import RiskAssessmentRequest
        request = RiskAssessmentRequest(
            stage=stage,
            industry=industry,
            monthly_income=monthly_income,
            employee_count=employee_count,
            has_pos=has_pos,
            signals={}  # 如果没有提供 signals，使用空字典（后端会兜底）
        )
        
        # 重新评估风险
        risk_score, risk_level, findings, meta = assess_risk_v3(request)
        
        # ✅ 付费字段控制：未解锁时移除 pro_only findings
        findings = _filter_pro_findings(findings, unlocked)

        # 转换 findings 为 dict 格式
        findings_dict = [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ if hasattr(f, "__dict__") else f for f in findings]
        
        # 重新生成决策建议（使用最新的 unlocked_tier）
        decision_summary = compute_decision_summary(
            stage=request.stage,
            industry=request.industry,
            risk_score=risk_score,
            risk_level=risk_level,
            monthly_income=request.monthly_income,
            employee_count=request.employee_count,
            findings=findings_dict,
            meta=meta,
            unlocked_tier=unlocked,
        )
    
    # 返回结果
    result = {
        "assessment_id": assessment.assessment_id,
        "user_id": getattr(assessment, "user_id", None),
        "unlocked_tier": unlocked,
        "stripe_session_id": getattr(assessment, "stripe_session_id", None),
    }
    
    # ✅ 返回创建时间（如果 naive 则假设 UTC，如果已经是 aware 则直接使用）
    dt = assessment.created_at
    if not dt:
        created_at = None
    elif dt.tzinfo is None:
        created_at = dt.replace(tzinfo=timezone.utc).isoformat()
    else:
        created_at = dt.isoformat()
    result["created_at"] = created_at
    
    if decision_summary:
        result["decision_summary"] = decision_summary
    
    # ✅ 最小化日志记录（不存个人信息）
    logger.info(f"[ASSESSMENT_GET] assessment_id={assessment.assessment_id}, unlocked_tier={unlocked}")
    
    return result
