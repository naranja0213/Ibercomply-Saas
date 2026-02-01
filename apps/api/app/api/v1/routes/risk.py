from fastapi import APIRouter
from app.schemas.assessment import RiskAssessmentRequest, RiskAssessmentResponse
from app.services.risk_engine import assess_risk_v2
from app.services.decision_engine import compute_decision_summary

router = APIRouter()


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk_endpoint(request: RiskAssessmentRequest):
    """
    风险评估接口（旧接口，保留以兼容）
    接收用户输入，返回风险评估结果
    """
    # 评估风险
    risk_score, risk_level, findings, meta = assess_risk_v2(request)

    # 未解锁时过滤 pro_only（v1 接口默认免费）
    def _is_pro_only(item) -> bool:
        if isinstance(item, dict):
            return bool(item.get("pro_only"))
        if hasattr(item, "pro_only"):
            return bool(getattr(item, "pro_only"))
        return False

    findings = [f for f in findings if not _is_pro_only(f)]

    # 转换 findings 为 dict 格式（用于 decision_engine）
    findings_dict = [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ if hasattr(f, "__dict__") else f for f in findings]
    
    # 生成决策建议（使用新的 compute_decision_summary）
    decision_summary = compute_decision_summary(
        stage=request.stage,
        industry=request.industry,
        risk_score=risk_score,
        risk_level=risk_level,
        monthly_income=request.monthly_income,
        employee_count=request.employee_count,
        findings=findings_dict,
        meta=meta,
        unlocked_tier="none",
    )
    
    # 生成 assessment_id（旧接口兼容）
    import uuid
    from datetime import datetime
    assessment_id = f"assessment_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"
    
    return RiskAssessmentResponse(
        id=assessment_id,  # 返回 assessment_id
        risk_score=risk_score,
        risk_level=risk_level,
        findings=findings,
        decision_summary=decision_summary
    )

