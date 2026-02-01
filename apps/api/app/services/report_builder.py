"""
PDF 报告数据组装器
从数据库读取已保存的评估结果，根据 unlocked_tier 组装报告数据
不关心权限判断（由调用方负责）
"""

from typing import Dict, Any, Literal
from app.models import Assessment

PaywallTier = Literal["none", "basic_15", "expert_39"]


def build_report_data(assessment: Assessment) -> Dict[str, Any]:
    """
    从数据库读取已保存的评估结果，组装 PDF 报告数据
    
    ⚠️ 重要：不在此函数中判断权限，只根据 unlocked_tier 组装数据
    权限校验必须在调用方完成
    
    Args:
        assessment: Assessment 模型实例（必须包含 result_data, decision_summary_data, input_data）
    
    Returns:
        报告数据字典，包含所有需要的内容
    """
    if not assessment.result_data or not assessment.decision_summary_data:
        raise ValueError("Assessment 缺少评估结果数据，无法生成 PDF")
    
    # 从数据库读取已保存的数据
    result_data = assessment.result_data or {}
    decision_summary_data = assessment.decision_summary_data or {}
    input_data = assessment.input_data or {}
    unlocked_tier = (assessment.unlocked_tier or "none").strip().lower()
    
    # 组装报告数据
    report_data = {
        "assessment_id": assessment.assessment_id,
        "unlocked_tier": unlocked_tier,
        "risk_score": result_data.get("risk_score", 0),
        "risk_level": result_data.get("risk_level", ""),
        "risk_band": result_data.get("meta", {}).get("risk_band"),
        "decision_summary": {
            "title": decision_summary_data.get("title", ""),
            "conclusion": decision_summary_data.get("conclusion", ""),
            "confidence_level": decision_summary_data.get("confidence_level", "low"),
            "confidence_reason": decision_summary_data.get("confidence_reason", ""),
            "next_review_window": decision_summary_data.get("next_review_window", ""),
        },
        "top_risks": decision_summary_data.get("top_risks", []),
        "dont_do": decision_summary_data.get("dont_do", []),
        "risk_explain": decision_summary_data.get("risk_explain", {}),
    }
    
    # basic_15 以上才包含
    if unlocked_tier in ("basic_15", "expert_39"):
        report_data["reasons"] = decision_summary_data.get("reasons", [])
        report_data["recommended_actions"] = decision_summary_data.get("recommended_actions", [])
        report_data["risk_if_ignore"] = decision_summary_data.get("risk_if_ignore", [])
    
    # expert_39 才包含（专家包内容）
    if unlocked_tier == "expert_39":
        expert_pack = decision_summary_data.get("expert_pack")
        if expert_pack and isinstance(expert_pack, dict):
            report_data["enforcement_path"] = expert_pack.get("enforcement_path")
            report_data["score_breakdown"] = expert_pack.get("score_breakdown")
            report_data["roadmap_30d"] = expert_pack.get("roadmap_30d")
            report_data["documents_pack"] = expert_pack.get("documents_pack")
            report_data["self_audit_checklist"] = expert_pack.get("self_audit_checklist")
            report_data["risk_groups"] = expert_pack.get("risk_groups")
            report_data["decision_guidance"] = expert_pack.get("decision_guidance")
            report_data["cadence_90d"] = expert_pack.get("cadence_90d")
    
    # 添加输入信息（用于显示）
    report_data["input"] = input_data
    
    # ✅ 添加 created_at（用于统一版本号时区）
    from datetime import timezone
    dt = assessment.created_at
    if not dt:
        created_at = None
    elif dt.tzinfo is None:
        created_at = dt.replace(tzinfo=timezone.utc).isoformat()
    else:
        created_at = dt.isoformat()
    report_data["created_at"] = created_at
    
    return report_data

