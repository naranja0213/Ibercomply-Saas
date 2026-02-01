from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any
from dataclasses import dataclass


class Finding(BaseModel):
    code: str
    title: str
    detail: str
    severity: Literal["info", "low", "medium", "high"]
    legal_ref: Optional[str] = None
    pro_only: bool = False  # 控制是否仅在付费层显示
    explain_difficulty: Optional[Literal["low", "medium", "high"]] = None
    trigger_sources: Optional[List[str]] = None


class RiskAssessmentRequest(BaseModel):
    stage: Literal["PRE_AUTONOMO", "AUTONOMO", "SL"]  # 经营身份阶段
    industry: str
    monthly_income: float
    employee_count: int
    has_pos: bool
    signals: Dict[str, bool] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "stage": "AUTONOMO",
                "industry": "restaurant",
                "monthly_income": 4800,
                "employee_count": 2,
                "has_pos": True,
                "signals": {
                    "bank_inquiry": True,
                    "iva_mismatch": False,
                },
            }
        }
    }


class DecisionGuidance(BaseModel):
    need_professional: Literal["no", "consider", "strongly_consider", "yes"] = Field(
        description="是否需要专业人士介入：no/consider/strongly_consider/yes"
    )
    suggested_roles: List[str] = Field(
        default_factory=list,
        description="建议咨询的角色列表（可为空）",
    )
    reason: str = Field(description="给出该建议强度的原因说明")

    model_config = {
        "json_schema_extra": {
            "example": {
                "need_professional": "strongly_consider",
                "suggested_roles": ["gestor/税务顾问"],
                "reason": "已出现较高“解释失败”风险，建议至少与 gestor 做一次材料链梳理。",
            }
        }
    }


class ExpertPack(BaseModel):
    """€39 决策版内容"""
    risk_groups: Dict[str, List[Dict[str, Any]]]  # 风险分组报告
    roadmap_30d: List[Dict[str, Any]]  # 30天路线图
    documents_pack: List[str]  # 材料清单
    self_audit_checklist: List[str]  # 自检表
    score_breakdown: Optional[Dict[str, Any]] = None  # ✅ 新增：分数构成解析
    enforcement_path: Optional[List[Dict[str, Any]]] = None  # ✅ 新增：执法路径（结构化）
    decision_guidance: Optional[DecisionGuidance] = Field(
        default=None,
        description="决策提示：是否需要专业人士介入",
    )
    cadence_90d: Optional[List[str]] = Field(
        default=None,
        description="30/90 天节奏要点",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "decision_guidance": {
                    "need_professional": "yes",
                    "suggested_roles": ["gestor/税务顾问", "律师"],
                    "reason": "当前风险阶段较高，建议由专业人士判断整改优先级与责任边界。",
                },
                "cadence_90d": [
                    "0–30 天：补齐最薄弱的材料链条（票据/对账/合同/用工）",
                    "31–60 天：固定月度对账与归档节奏，避免解释断层",
                    "61–90 天：复评一次并调整清单，确认风险是否下降",
                ],
            }
        }
    }


class ProBrief(BaseModel):
    """Gestoría B2B 接口输出（Coming soon）"""
    status: Literal["coming_soon", "available"] = "coming_soon"
    summary: Optional[Dict[str, Any]] = None
    top_issues: Optional[List[Dict[str, str]]] = None
    recommended_documents: Optional[List[str]] = None
    export: Optional[Dict[str, Optional[str]]] = None


class RiskExplain(BaseModel):
    """风险分数解释（咨询师风格）"""
    label: str  # 风险等级标签（如"可控"、"观察区"）
    one_liner: str  # 一句话解释
    stage_note: str  # 阶段特定解释
    main_drivers: List[str]  # 主要风险驱动因素（最多3个）
    risk_stage: Optional[Literal["A", "B", "C", "D"]] = None


class DecisionSummary(BaseModel):
    level: Literal[
        # PRE_AUTONOMO 阶段
        "OBSERVE_PRE", "REGISTER_AUTONOMO", "STRONG_REGISTER_AUTONOMO",
        # AUTONOMO 阶段
        "OK_AUTONOMO", "RISK_AUTONOMO", "CONSIDER_SL",
        # SL 阶段
        "OK_SL", "RISK_SL_LOW", "RISK_SL_HIGH"
    ]
    decision_intent: Literal["REGISTER", "FIX", "UPGRADE", "MONITOR"]  # 决策意图（用于邮件提醒、再营销、gestoria 对接等）
    title: str
    conclusion: str
    confidence_level: Literal["high", "medium", "low"]
    confidence_reason: str  # ✅ 新增：置信度原因
    next_review_window: str
    paywall: Literal["none", "basic_15", "expert_39"] = "none"  # 付费墙级别
    pay_reason: Optional[str] = None  # 付费原因说明
    top_risks: List[Finding] = Field(default_factory=list)  # Top 3 风险（免费展示）
    reasons: List[str]  # 付费墙控制
    recommended_actions: List[str]  # 付费墙控制（使用 action_templates 生成）
    risk_if_ignore: List[str]  # 付费墙控制
    expert_pack: Optional[ExpertPack] = None  # €39 决策版内容
    pro_brief: Optional[ProBrief] = None  # Gestoría B2B 摘要
    risk_explain: Optional[RiskExplain] = None  # ✅ 新增：风险分数解释（咨询师风格）
    dont_do: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "level": "RISK_AUTONOMO",
                "decision_intent": "FIX",
                "title": "需要尽快补齐材料链",
                "conclusion": "当前处于高可见性区间，建议先完善对账与材料闭环。",
                "confidence_level": "medium",
                "confidence_reason": "出现多个解释失败点，且触发信号接近。",
                "next_review_window": "30天",
                "paywall": "basic_15",
                "pay_reason": "完整行动清单与材料清单需解锁。",
                "top_risks": [],
                "reasons": ["收入与申报口径存在差异"],
                "recommended_actions": ["建立月度对账清单"],
                "risk_if_ignore": ["被要求补件的概率上升"],
                "expert_pack": None,
                "pro_brief": None,
                "risk_explain": {
                    "label": "高可见性",
                    "one_liner": "目前容易被对比核对",
                    "stage_note": "AUTONOMO 阶段常见",
                    "main_drivers": ["收入上升", "POS 使用"],
                    "risk_stage": "B",
                },
                "dont_do": ["不要临时补造资料"],
            }
        }
    }


class RiskAssessmentResponse(BaseModel):
    id: str  # assessment_id（关键：贯穿支付流程）
    risk_score: int
    risk_level: Literal["green", "yellow", "orange", "red"]
    findings: List[Finding]
    decision_summary: DecisionSummary
    meta: Optional[Dict[str, Any]] = None  # ✅ 新增：包含 industry_key, tags, matched_triggers

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "assessment_abc123_1700000000",
                "risk_score": 42,
                "risk_level": "orange",
                "findings": [],
                "decision_summary": {
                    "level": "RISK_AUTONOMO",
                    "decision_intent": "FIX",
                    "title": "需要尽快补齐材料链",
                    "conclusion": "当前处于高可见性区间，建议先完善对账与材料闭环。",
                    "confidence_level": "medium",
                    "confidence_reason": "出现多个解释失败点，且触发信号接近。",
                    "next_review_window": "30天",
                    "paywall": "basic_15",
                    "pay_reason": "完整行动清单与材料清单需解锁。",
                    "top_risks": [],
                    "reasons": ["收入与申报口径存在差异"],
                    "recommended_actions": ["建立月度对账清单"],
                    "risk_if_ignore": ["被要求补件的概率上升"],
                    "expert_pack": None,
                    "pro_brief": None,
                    "risk_explain": None,
                    "dont_do": [],
                },
                "meta": {
                    "industry_key": "restaurant",
                    "tags": ["pos", "income_high"],
                    "matched_triggers": ["bank_inquiry"],
                },
            }
        }
    }
