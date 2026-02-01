"""
Decision Engine - Stage 隔离的决策引擎
只做决策，不算分。它吃 stage + risk_score + meta.modules + critical_count + tags，吐出 decision_summary。
绝不输出跨阶段建议。
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from ..schemas.assessment import DecisionSummary as DecisionSummarySchema, ExpertPack, ProBrief, RiskExplain
from .decision_templates import (
    DECISION_DEFAULT_TEMPLATES,
    INDUSTRY_ACTION_TEMPLATES,
    merge_actions,
    apply_paywall,
    PaywallTier as PaywallTierType,
    normalize_tier,
)
from .risk.signals_catalog import SIGNAL_DEFS
from .decision.action_templates import (
    DEFAULT_ACTIONS_BY_INDUSTRY,
    DEFAULT_REASONS_BY_DECISION,
    DEFAULT_IGNORE_BY_DECISION,
)

# 按 stage 的"解释口径"补丁（与风险阶段阈值对齐）
RISK_EXPLAIN_BY_STAGE: Dict[str, Dict[int, str]] = {
    "PRE_AUTONOMO": {
        0: "你现在更像试水阶段，先把收入来源记录好就行。",
        25: "分数不低的原因多半是'结构还没建立'：没有固定记账/发票/对账路径。",
        50: "你已经接近常见注册阈值，建议开始准备注册与材料，不然一旦收入上来会很被动。",
        70: "你已经属于'明显经营状态'，建议尽快把身份/申报/票据链定下来。",
    },
    "AUTONOMO": {
        0: "你做得不错，继续保持对账一致就够了。",
        25: "问题不大，但'可追溯性'变强了（POS/平台/收入上升），建议固定对账。",
        50: "建议尽快规范：票据链、申报节奏、用工/外包材料要补齐。",
        70: "已经高暴露：任一环节断掉都可能触发补缴情形与罚款风险。",
    },
    "SL": {
        0: "公司结构稳定，重点是制度持续执行。",
        25: "薄弱点在制度执行：合同/票据/员工或数据流程需要更一致。",
        50: "业务复杂度上来了，需要制度化整改（合同模板、档案、权限、对账）。",
        70: "属于高暴露：建议专项审查（税务+劳动/数据/许可），按路线图整改。",
    },
}


def _get_risk_explain_stage_note(stage: Stage, score: int) -> str:
    """根据 stage 和分数获取阶段特定解释"""
    stage_notes = RISK_EXPLAIN_BY_STAGE.get(stage, {})
    if score < 25:
        return stage_notes.get(0, "")
    elif score < 50:
        return stage_notes.get(25, "")
    elif score < 70:
        return stage_notes.get(50, "")
    else:
        return stage_notes.get(70, "")


def _get_risk_stage(score: int) -> Literal["A", "B", "C", "D"]:
    """
    A：可解释但需注意
    B：高可见性（容易被注意）
    C：触发点临近
    D：需要专业介入
    """
    if score < 25:
        return "A"
    elif score < 50:
        return "B"
    elif score < 70:
        return "C"
    else:
        return "D"


def _risk_stage_profile(risk_stage: Literal["A", "B", "C", "D"]) -> Dict[str, str]:
    """
    统一的阶段解释口径（后端输出，前端只展示）
    注意：只做决策解释，不提供任何规避/操作细节。
    """
    profiles = {
        "A": {
            "label": "阶段 A：可解释但需注意",
            "one_liner": "整体风险可控，关键是把票据/对账习惯固化，避免未来变得难以解释。",
            "note": (
                "监管视角：你的特征更接近正常经营区间，短期不太像“异常样本”。\n"
                "你需要做的是：建立连续性记录（发票/对账/合同/用工材料），让“可解释性”长期保持。"
            ),
        },
        "B": {
            "label": "阶段 B：高可见性（容易被注意）",
            "one_liner": "不等于危险，但你的经营特征更容易被对比与提问，材料链要开始系统化。",
            "note": (
                "监管视角：你已处在“更容易被看到”的位置（例如规模、收款可追溯性、行业密度等）。\n"
                "你需要做的是：把关键链条补齐（对账、归档、合同/用工/许可），降低“解释失败”的概率。"
            ),
        },
        "C": {
            "label": "阶段 C：触发点临近",
            "one_liner": "风险正在靠近触发区；继续拖延会显著增加被要求补材料、补申报或沟通成本。",
            "note": (
                "监管视角：你的信号组合更像“会被问到”的类型，常见触发来自银行合规问询或行业抽查。\n"
                "你需要做的是：优先补齐最薄弱环节的材料链条，并把未来 30–90 天的合规节奏固定下来。"
            ),
        },
        "D": {
            "label": "阶段 D：需要专业介入",
            "one_liner": "当前暴露面较高，建议尽快让专业人士介入判断与整改优先级，避免风险升级。",
            "note": (
                "监管视角：你已接近或进入高暴露区间，“材料缺口 + 信号叠加”会显著放大后果成本。\n"
                "你需要做的是：尽快寻求专业协助（gestor/律师/税务顾问），同时按清单先做“可解释性”补强。"
            ),
        },
    }
    return profiles[risk_stage]


def _build_risk_explain(
    stage: Stage,
    risk_score: int,
    modules: Dict[str, Any],
    tags: List[str],
    matched_triggers: List[str],
) -> RiskExplain:
    """
    统一生成 RiskExplain：阶段解释（A/B/C/D）+ stage 补丁 + 主要驱动
    """
    risk_stage = _get_risk_stage(risk_score)
    p = _risk_stage_profile(risk_stage)
    stage_patch = _get_risk_explain_stage_note(stage, risk_score)
    if stage_patch:
        stage_note = f"{p['note']}\n\n阶段补充：{stage_patch}"
    else:
        stage_note = p["note"]

    return RiskExplain(
        label=p["label"],
        one_liner=p["one_liner"],
        stage_note=stage_note,
        main_drivers=_get_main_drivers(modules, tags, matched_triggers),
        risk_stage=risk_stage,
    )


def _get_main_drivers(modules: Dict[str, Any], tags: List[str], matched_triggers: List[str]) -> List[str]:
    """
    获取主要风险驱动因素（优先级：income > pos > employee > industry > signals）
    """
    drivers = []
    
    # 收入驱动
    income_score = int(modules.get("income", 0))
    if income_score >= 18:
        drivers.append("收入规模上升")
    elif income_score >= 10:
        drivers.append("收入可追溯性增强")
    
    # POS 驱动
    pos_score = int(modules.get("pos", 0))
    if pos_score > 0:
        drivers.append("POS 刷卡流水可追溯")
    
    # 雇员驱动
    emp_score = int(modules.get("employees", 0))
    if emp_score > 0:
        drivers.append("用工合规点")
    
    # 行业驱动
    if "tax" in tags:
        drivers.append("行业检查密度")
    if "consumer" in tags or "municipal" in tags:
        drivers.append("行业监管要求")
    
    # 信号驱动
    signals_score = int(modules.get("signals", 0))
    if signals_score >= 10:
        drivers.append("经营信号叠加")
    elif signals_score > 0:
        drivers.append("部分经营特征显现")
    
    # 如果没有驱动因素，返回默认
    if not drivers:
        drivers.append("结构尚未固定（记账/票据/对账）")
    
    return drivers[:3]  # 最多返回3个


Stage = Literal["PRE_AUTONOMO", "AUTONOMO", "SL"]
Confidence = Literal["high", "medium", "low"]

# 置信度原因模板（更详细、更专业的版本）
CONFIDENCE_REASON_MAP = {
    # ===== PRE_AUTONOMO =====
    "OBSERVE_PRE": (
        "当前输入显示经营信号尚不集中：收入规模、用工与可追溯收款特征均未明显进入高关注区间，"
        "因此建议先建立基础记录习惯并在 1–3 个月内复评。"
    ),

    # ===== PRE / GENERAL REGISTER =====
    "REGISTER_AUTONOMO": (
        "当前信号组合更接近持续经营特征：收入与收款可追溯性（或行业特征）已达到常见关注阈值附近，"
        "尽早完成注册并固定对账/票据流程能显著降低后续追溯处理风险。"
    ),

    "STRONG_REGISTER_AUTONOMO": (
        "多项高权重信号叠加（如收入、用工、可追溯收款或高关注行业特征），风险已处于较高区间。"
        "在这种情况下，完善注册与材料链条通常是降低风险最有效的动作。"
    ),

    # ===== AUTONOMO =====
    "OK_AUTONOMO": (
        "你已处于 Autónomo 合规框架内，且目前关键触发点较少或已被控制。"
        "在现有收入与规模下，维持对账与票据链完整即可保持风险可控。"
    ),

    "RISK_AUTONOMO": (
        "你已完成注册，但部分经营特征（如收入变化、收款可追溯性或材料一致性要求）使暴露面上升。"
        "因此结论倾向于'风险可控但需关注变化'，并建议通过对账与归档来降低波动风险。"
    ),

    "CONSIDER_SL": (
        "当前经营复杂度与责任边界需求上升（如多业务线、外包/雇佣或更高流水），"
        "用公司结构承载通常能更清晰地管理税务、劳动与责任风险，因此建议开始评估 SL 路径。"
    ),

    # ===== SL =====
    "OK_SL": (
        "公司化框架已建立，且当前风险点主要来自日常执行（账务、合同、档案与数据合规）。"
        "在制度稳定运行的前提下，风险保持在可控范围内。"
    ),

    "RISK_SL_LOW": (
        "公司结构方向正确，但从输入信号看部分链条（合同/票据/档案/数据）存在薄弱环节。"
        "这类问题通常通过补齐制度与留档即可显著改善，因此给出'存在风险点需补齐'的判断。"
    ),

    "RISK_SL_HIGH": (
        "出现多项高严重度触发点或关键组合风险，潜在后果成本上升明显。"
        "在这种情况下，优先级应转向'立即整改 + 专业协助'，以尽快降低整体暴露。"
    ),
}


def _confidence(critical_count: int, signals_points: int, has_signals: bool) -> Confidence:
    """计算置信度"""
    # 越多触发点/关键点，越"像稳定经营信号"
    if critical_count >= 2:
        return "high"
    if has_signals and signals_points >= 6:
        return "medium"
    return "low"


def _next_review(stage: Stage, decision_code: str) -> str:
    """计算下次复查窗口（规范要求：统一为30天）"""
    # ✅ 根据规范，标准节奏语言统一为"30天"
    return "30天"


def _top_risks(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """获取 Top 3 风险点（免费展示）"""
    # 优先 high/medium，保留原结构给前端
    priority = {"high": 0, "medium": 1, "low": 2, "info": 3}
    sorted_findings = sorted(findings, key=lambda f: priority.get(f.get("severity", "info"), 3))
    return sorted_findings[:3]


def _enrich_top_findings(
    top_findings: List[Dict[str, Any]],
    meta: Dict[str, Any],
    tags: List[str],
) -> List[Dict[str, Any]]:
    """补齐解释失败点字段（难度 + 触发来源）"""
    sev2diff = {"info": "low", "low": "low", "medium": "medium", "high": "high"}
    default_sources = ["申报一致性复核", "行业对比抽查"]
    finding_sources = (meta or {}).get("finding_sources", {})

    def _sources_from_signal_keys(keys: List[str]) -> List[str]:
        sources = []
        for key in keys:
            if key in ("pos_used_daily", "uses_delivery_platforms", "platform_sales", "platform_payments", "works_for_platforms"):
                sources.append("POS/平台数据比对")
            if "cash" in key:
                sources.append("银行合规问询")
            if "employee" in key or "contract" in key or "labor" in key:
                sources.append("劳动/社保材料核对")
            if "data" in key or "id" in key or "rgpd" in key:
                sources.append("数据合规抽查")
            if "license" in key or "permit" in key or "terrace" in key:
                sources.append("市政/许可核对")
            if "invoice" in key or "income" in key:
                sources.append("申报一致性复核")
        if "consumer" in tags:
            sources.append("消费者投诉/抽查")
        if "municipal" in tags:
            sources.append("市政检查")
        # 去重并保序
        out = []
        for s in sources:
            if s not in out:
                out.append(s)
        return out[:3]

    enriched: List[Dict[str, Any]] = []
    for f in top_findings or []:
        code = f.get("code", "")
        sev = f.get("severity", "low")
        item = dict(f)
        item["explain_difficulty"] = item.get("explain_difficulty") or sev2diff.get(sev, "medium")
        src = finding_sources.get(code, {})
        signal_keys = src.get("signal_keys", []) if isinstance(src, dict) else []
        combo_keys = src.get("combo_signals", []) if isinstance(src, dict) else []
        trigger_sources = _sources_from_signal_keys(signal_keys + combo_keys)
        item["trigger_sources"] = item.get("trigger_sources") or (trigger_sources or default_sources)
        enriched.append(item)
    return enriched


def _build_dont_do(
    stage: Stage,
    risk_score: int,
    top_findings: List[Dict[str, Any]],
    matched_triggers: List[str],
) -> List[str]:
    stage_code = _get_risk_stage(risk_score)
    items: List[str] = []

    items.append("不要尝试伪造、补造交易或凭证（这会把原本可控的合规问题升级为更严重的风险）。")
    items.append("不要进行与经营规模不匹配的异常资金操作（可能触发银行合规审查并要求解释）。")

    if stage_code in ["C", "D"]:
        items.append("不要在没有专业意见的情况下做重大结构变更（例如主体/角色/业务模式频繁变化会显著增加解释难度）。")
    else:
        items.append("不要让记录长期缺失（持续缺少对账与材料会使后续解释成本越来越高）。")

    if matched_triggers:
        items.append("不要忽视已出现的触发信号；应优先补齐与该信号相关的材料链条（以降低“解释失败”的概率）。")

    return items[:4]


def _expert_pack(stage: Stage, industry: str, decision_code: str, meta: Dict[str, Any]) -> Optional[ExpertPack]:
    """
    €39 专家包：不需要非常复杂，关键是"看起来像专业系统"
    """
    tags = (meta or {}).get("tags", [])
    triggers = (meta or {}).get("matched_triggers", [])
    modules = (meta or {}).get("modules", {})
    score_breakdown = (meta or {}).get("score_breakdown", {})  # ✅ 从 meta 获取分数构成
    risk_score = (meta or {}).get("risk_score", 0)
    top3_findings = (meta or {}).get("top3_findings", [])

    try:
        # 构建风险分组（按 tag 分组）
        risk_groups: Dict[str, List[Dict[str, Any]]] = {}
        for tag in tags[:5]:
            risk_groups[tag] = []  # 可以后续扩展添加具体风险项
        
        # ✅ 构建执法路径（结构化）
        enforcement_path = [
            {
                "step": 1,
                "title": "信号异常识别",
                "description": "税务局通过 POS / 平台数据比对、银行流水交叉验证，识别出收入与申报不一致或存在持续经营特征。"
            },
            {
                "step": 2,
                "title": "补申报与滞纳金",
                "description": "要求补缴过往税款（VAT/IRPF），并计算滞纳金。通常会给出材料补充期限（以通知为准）。"
            },
            {
                "step": 3,
                "title": "行政处罚或强制注册",
                "description": "如果解释不闭环或拒绝配合，可能产生补缴、利息与行政处罚；幅度取决于情形与主管机关认定。"
            }
        ]
        
        risk_stage = _get_risk_stage(risk_score)
        triggers = (meta or {}).get("matched_triggers", [])
        has_trigger = bool(triggers)
        has_high = any(
            f.get("severity") == "high" or f.get("explain_difficulty") == "high"
            for f in (top3_findings or [])
        )
        sources: List[str] = []
        for f in (top3_findings or []):
            sources += (f.get("trigger_sources") or [])
        has_bank = "银行合规问询" in sources
        has_labor = "劳动/社保材料核对" in sources
        has_data = "数据合规抽查" in sources
        has_municipal = "市政/许可核对" in sources

        need_professional = "no"
        roles: List[str] = []
        reason = "当前风险阶段较低，可先按清单自查并在后续变化时复评。"

        if risk_stage in ["C", "D"]:
            need_professional = "yes"
            roles = ["gestor/税务顾问", "律师"]
            reason = "当前风险阶段较高，建议由专业人士判断整改优先级与责任边界。"
        elif risk_stage == "B":
            if has_bank:
                need_professional = "yes"
                roles = ["gestor/税务顾问", "律师"]
                reason = "已出现外部触发信号（如银行合规问询/资料要求），建议尽快由专业人士协助梳理材料缺口与优先级。"
            elif has_trigger or has_high or has_labor:
                need_professional = "strongly_consider"
                roles = ["gestor/税务顾问"]
                reason = "已出现较高“解释失败”风险，建议至少与 gestor 做一次材料链梳理，以降低后续沟通成本。"
            else:
                need_professional = "consider"
                roles = ["gestor/税务顾问"]
                reason = "处于“高可见性”区间，建议先把对账与材料链系统化；若出现银行问询或正式通知，再升级为专业介入。"

        if stage == "SL" and need_professional in ["strongly_consider", "yes"] and (has_data or has_municipal):
            roles.append("数据保护顾问")

        # 去重并保序
        uniq_roles = []
        for r in roles:
            if r not in uniq_roles:
                uniq_roles.append(r)

        decision_guidance = {
            "need_professional": need_professional,
            "suggested_roles": uniq_roles,
            "reason": reason,
        }

        cadence_90d = [
            "0–30 天：补齐最薄弱的材料链条（票据/对账/合同/用工）",
            "31–60 天：固定月度对账与归档节奏，避免解释断层",
            "61–90 天：复评一次并调整清单，确认风险是否下降",
        ]

        return ExpertPack(
            risk_groups=risk_groups,
            roadmap_30d=[
                {"week": "第1周", "tasks": ["建立资料归档与对账体系（收入/成本/合同/用工）"]},
                {"week": "第2周", "tasks": ["按行业高频检查点做一次自检并补齐缺口"]},
                {"week": "第3周", "tasks": ["把流程固化（谁负责、文件在哪、如何对账）"]},
                {"week": "第4周", "tasks": ["复评一次，确认风险是否下降"]},
            ],
            documents_pack=[
                "收款流水（POS/转账/平台）与对账表",
                "主要合同/订单记录（只保留必要信息）",
                "成本票据（进货/租金/水电/平台费用等）",
                "用工材料（如有）：合同/社保/工时/PRL/保险",
            ],
            self_audit_checklist=[
                f"□ 收入与成本对账表完整（{industry} 行业）",
                "□ 主要合同/订单记录可追溯",
                "□ 成本票据归档（至少3个月）",
                "□ 用工材料（如有）齐全",
                "□ 数据保护流程（如涉及）",
            ],
            score_breakdown=score_breakdown,  # ✅ 新增：分数构成
            enforcement_path=enforcement_path,  # ✅ 新增：执法路径
            decision_guidance=decision_guidance,  # ✅ 决策提示
            cadence_90d=cadence_90d,  # ✅ 30/90 天节奏
        )
    except Exception:
        # 如果构建失败，返回 None
        return None


def compute_decision_summary(
    stage: Stage,
    industry: str,
    risk_score: int,
    risk_level: str,
    monthly_income: float,
    employee_count: int,
    findings: List[Dict[str, Any]],
    meta: Dict[str, Any],
    unlocked_tier: Literal["none", "basic_15", "expert_39"] = "none",
) -> DecisionSummarySchema:
    """
    输出一个不会打架的 decision_summary。
    - stage 隔离：不同 stage 只能产出各自的 decision_code 集合
    - paywall：默认按 decision_code 提示要不要解锁
    """
    modules = (meta or {}).get("modules", {})
    income_pts = int(modules.get("income", 0))
    emp_pts = int(modules.get("employees", 0))
    signals_pts = int(modules.get("signals", 0))
    critical_count = int((meta or {}).get("critical_count", 0))
    tags = (meta or {}).get("tags", [])
    matched_triggers = (meta or {}).get("matched_triggers", [])
    has_signals = bool(matched_triggers) or signals_pts != 0

    conf = _confidence(critical_count=critical_count, signals_points=signals_pts, has_signals=has_signals)
    top3_findings = _enrich_top_findings(_top_risks(findings), meta, tags)

    # ---------- 决策：PRE_AUTONOMO ----------
    if stage == "PRE_AUTONOMO":
        if risk_score < 25:
            decision_level = "OBSERVE_PRE"
            title = "当前阶段暂无明显注册压力"
            conclusion = "基于当前填写信息，你的风险信号较弱。建议先建立基础记录与对账习惯。"
            decision_intent = "MONITOR"
        elif risk_score < 60:
            decision_level = "REGISTER_AUTONOMO"
            title = "建议注册 Autónomo"
            conclusion = "你已接近稳定经营特征，继续未登记可能增加被检查/被罚概率。"
            decision_intent = "REGISTER"
        else:
            decision_level = "STRONG_REGISTER_AUTONOMO"
            title = "强烈建议尽快注册 Autónomo"
            conclusion = "当前风险信号较强（收入/用工/POS/行业触发等），建议尽快建立更规范的经营结构与凭证体系。"
            decision_intent = "REGISTER"

        next_review = _next_review(stage, decision_level)

        # 计算 paywall（根据 decision_level）
        if decision_level in ["REGISTER_AUTONOMO", "STRONG_REGISTER_AUTONOMO"]:
            required_tier: PaywallTierType = "basic_15"
            pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
        else:
            required_tier = "none"
            pay_reason = None

        # ✅ 使用新的模板系统：从 action_templates 获取
        industry_key = (industry or "other").lower()
        base_template = DECISION_DEFAULT_TEMPLATES.get(decision_level) or DECISION_DEFAULT_TEMPLATES["RISK_AUTONOMO"]
        
        # 获取行业默认行动清单（至少6条）
        industry_actions = DEFAULT_ACTIONS_BY_INDUSTRY.get(industry_key, DEFAULT_ACTIONS_BY_INDUSTRY["other"])
        
        # 获取行业特定的额外行动清单（从旧的模板系统）
        industry_map = INDUSTRY_ACTION_TEMPLATES.get(industry_key, {})
        industry_extra = industry_map.get("common", [])
        
        # 合并行动清单并去重，确保最小长度 >= 5
        merged_actions = merge_actions(industry_actions, industry_extra, min_len=5)
        merged_actions = merged_actions[:12]  # 限制最多12条
        
        # ✅ 从模板系统获取原因和忽视后果
        reasons = DEFAULT_REASONS_BY_DECISION.get(decision_level, [
            "基于你当前填写信息的综合判断",
            "建议用同一口径持续复查"
        ])
        ignore = DEFAULT_IGNORE_BY_DECISION.get(decision_level, [
            "可能出现补税与罚款风险",
            "一旦触发检查沟通成本会显著上升"
        ])
        
        # ✅ 生成风险阶段解释（A/B/C/D）
        risk_explain = _build_risk_explain(stage, risk_score, modules, tags, matched_triggers)
        
        # 构建完整的 decision 字典（解锁前）
        decision_dict = {
            "level": decision_level,
            "decision_intent": decision_intent,
            "title": base_template["title"],
            "conclusion": base_template["conclusion"],
            "confidence_level": conf,
            "confidence_reason": CONFIDENCE_REASON_MAP.get(decision_level, "基于当前输入信号组合与常见合规阈值生成该判断，建议结合实际材料与专业意见确认。"),  # ✅ 新增：置信度原因
            "next_review_window": next_review,
            "paywall": required_tier,
            "pay_reason": pay_reason,
            "top_risks": top3_findings,
            "reasons": reasons[:3],  # 限制最多3条，但保证至少2条
            "recommended_actions": merged_actions,  # 保证至少5条
            "risk_if_ignore": ignore[:3],  # 限制最多3条，但保证至少2条
            "expert_pack": None,
            "pro_brief": ProBrief(status="coming_soon", summary=None, top_issues=None, recommended_documents=None, export=None),
            "risk_explain": risk_explain,  # ✅ 新增：风险分数解释
            "dont_do": _build_dont_do(stage, risk_score, top3_findings, matched_triggers),
        }
        
        # 根据 unlocked_tier 决定是否生成 expert_pack
        if unlocked_tier == "expert_39":
            meta_with_top = dict(meta or {})
            meta_with_top["top3_findings"] = top3_findings
            decision_dict["expert_pack"] = _expert_pack(stage, industry, decision_level, meta_with_top)
        
        # 按 unlocked_tier 裁剪付费字段
        decision_dict = apply_paywall(decision_dict, required_tier, unlocked_tier)
        
        # 开发环境：验证字段长度（断言）
        if unlocked_tier != "none" and required_tier != "none":
            tier_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(unlocked_tier, 0)
            required_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(required_tier, 0)
            if tier_rank >= required_rank:
                assert len(decision_dict["reasons"]) >= 2, f"reasons length {len(decision_dict['reasons'])} < 2 for {decision_level}"
                assert len(decision_dict["recommended_actions"]) >= 5, f"recommended_actions length {len(decision_dict['recommended_actions'])} < 5 for {decision_level}"
                assert len(decision_dict["risk_if_ignore"]) >= 2, f"risk_if_ignore length {len(decision_dict['risk_if_ignore'])} < 2 for {decision_level}"
        
        return DecisionSummarySchema(**decision_dict)

    # ---------- 决策：AUTONOMO ----------
    if stage == "AUTONOMO":
        # SL 评估条件（启发式）：员工较多或收入模块高 + 风险高
        consider_sl = (risk_score >= 65) and (emp_pts >= 12 or income_pts >= 18)

        if risk_score < 30:
            decision_level = "OK_AUTONOMO"
            decision_intent = "MONITOR"
        elif consider_sl:
            decision_level = "CONSIDER_SL"
            decision_intent = "UPGRADE"
        else:
            decision_level = "RISK_AUTONOMO"
            decision_intent = "FIX"

        next_review = _next_review(stage, decision_level)

        # 计算 paywall（根据 decision_level）
        if decision_level in ["CONSIDER_SL", "RISK_AUTONOMO"]:
            required_tier: PaywallTierType = "basic_15"
            pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
        else:
            required_tier = "none"
            pay_reason = None

        # 从模板系统获取完整内容（保证永远不为空）
        base_template = DECISION_DEFAULT_TEMPLATES.get(decision_level) or DECISION_DEFAULT_TEMPLATES["RISK_AUTONOMO"]
        
        # ✅ 使用新的模板系统：从 action_templates 获取
        industry_key = (industry or "other").lower()
        
        # 获取行业默认行动清单（至少6条）
        industry_actions = DEFAULT_ACTIONS_BY_INDUSTRY.get(industry_key, DEFAULT_ACTIONS_BY_INDUSTRY["other"])
        
        # 获取行业特定的额外行动清单（从旧的模板系统）
        industry_map = INDUSTRY_ACTION_TEMPLATES.get(industry_key, {})
        industry_extra = industry_map.get("common", [])
        
        # 合并行动清单并去重，确保最小长度 >= 5
        merged_actions = merge_actions(industry_actions, industry_extra, min_len=5)
        merged_actions = merged_actions[:12]  # 限制最多12条
        
        # ✅ 从模板系统获取原因和忽视后果
        reasons = DEFAULT_REASONS_BY_DECISION.get(decision_level, [
            "基于你当前填写信息的综合判断",
            "建议用同一口径持续复查"
        ])
        ignore = DEFAULT_IGNORE_BY_DECISION.get(decision_level, [
            "可能出现补税与罚款风险",
            "一旦触发检查沟通成本会显著上升"
        ])
        
        # ✅ 生成风险阶段解释（A/B/C/D）
        risk_explain = _build_risk_explain(stage, risk_score, modules, tags, matched_triggers)

        # 构建完整的 decision 字典（解锁前）
        decision_dict = {
            "level": decision_level,
            "decision_intent": decision_intent,
            "title": base_template["title"],
            "conclusion": base_template["conclusion"],
            "confidence_level": conf,
            "confidence_reason": CONFIDENCE_REASON_MAP.get(decision_level, "基于当前输入信号组合与常见合规阈值生成该判断，建议结合实际材料与专业意见确认。"),  # ✅ 新增：置信度原因
            "next_review_window": next_review,
            "paywall": required_tier,
            "pay_reason": pay_reason,
            "top_risks": top3_findings,
            "reasons": reasons[:3],  # 限制最多3条，但保证至少2条
            "recommended_actions": merged_actions,  # 保证至少5条
            "risk_if_ignore": ignore[:3],  # 限制最多3条，但保证至少2条
            "expert_pack": None,
            "pro_brief": ProBrief(status="coming_soon", summary=None, top_issues=None, recommended_documents=None, export=None),
            "risk_explain": risk_explain,
            "dont_do": _build_dont_do(stage, risk_score, top3_findings, matched_triggers),
        }
        
        # 根据 unlocked_tier 决定是否生成 expert_pack
        if unlocked_tier == "expert_39":
            meta_with_top = dict(meta or {})
            meta_with_top["top3_findings"] = top3_findings
            decision_dict["expert_pack"] = _expert_pack(stage, industry, decision_level, meta_with_top)
        
        # 按 unlocked_tier 裁剪付费字段
        decision_dict = apply_paywall(decision_dict, required_tier, unlocked_tier)
        
        # 开发环境：验证字段长度（断言）
        if unlocked_tier != "none" and required_tier != "none":
            tier_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(unlocked_tier, 0)
            required_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(required_tier, 0)
            if tier_rank >= required_rank:
                assert len(decision_dict["reasons"]) >= 2, f"reasons length {len(decision_dict['reasons'])} < 2 for {decision_level}"
                assert len(decision_dict["recommended_actions"]) >= 5, f"recommended_actions length {len(decision_dict['recommended_actions'])} < 5 for {decision_level}"
                assert len(decision_dict["risk_if_ignore"]) >= 2, f"risk_if_ignore length {len(decision_dict['risk_if_ignore'])} < 2 for {decision_level}"
        
        return DecisionSummarySchema(**decision_dict)

    # ---------- 决策：SL ----------
    # 只谈公司风险，绝不提"注册Autónomo"
    if stage == "SL":
        if risk_score < 35:
            decision_level = "OK_SL"
            decision_intent = "MONITOR"
        elif risk_score < 70:
            decision_level = "RISK_SL_LOW"
            decision_intent = "FIX"
        else:
            decision_level = "RISK_SL_HIGH"
            decision_intent = "FIX"

        next_review = _next_review(stage, decision_level)

        # 计算 paywall（根据 decision_level）
        if decision_level in ["RISK_SL_LOW", "RISK_SL_HIGH"]:
            required_tier: PaywallTierType = "basic_15"
            pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
        else:
            required_tier = "none"
            pay_reason = None

        # ✅ 使用新的模板系统：从 action_templates 获取
        industry_key = (industry or "other").lower()
        base_template = DECISION_DEFAULT_TEMPLATES.get(decision_level) or DECISION_DEFAULT_TEMPLATES["RISK_SL_LOW"]
        
        # 获取行业默认行动清单（至少6条）
        industry_actions = DEFAULT_ACTIONS_BY_INDUSTRY.get(industry_key, DEFAULT_ACTIONS_BY_INDUSTRY["other"])
        
        # 获取行业特定的额外行动清单（从旧的模板系统）
        industry_map = INDUSTRY_ACTION_TEMPLATES.get(industry_key, {})
        industry_extra = industry_map.get("common", [])
        
        # 合并行动清单并去重，确保最小长度 >= 5
        merged_actions = merge_actions(industry_actions, industry_extra, min_len=5)
        merged_actions = merged_actions[:12]  # 限制最多12条
        
        # ✅ 从模板系统获取原因和忽视后果
        reasons = DEFAULT_REASONS_BY_DECISION.get(decision_level, [
            "基于你当前填写信息的综合判断",
            "建议用同一口径持续复查"
        ])
        ignore = DEFAULT_IGNORE_BY_DECISION.get(decision_level, [
            "可能出现补税与罚款风险",
            "一旦触发检查沟通成本会显著上升"
        ])
        
        # ✅ 生成风险阶段解释（A/B/C/D）
        risk_explain = _build_risk_explain(stage, risk_score, modules, tags, matched_triggers)
        
        # 构建完整的 decision 字典（解锁前）
        decision_dict = {
            "level": decision_level,
            "decision_intent": decision_intent,
            "title": base_template["title"],
            "conclusion": base_template["conclusion"],
            "confidence_level": conf,
            "confidence_reason": CONFIDENCE_REASON_MAP.get(decision_level, "基于当前输入信号组合与常见合规阈值生成该判断，建议结合实际材料与专业意见确认。"),  # ✅ 新增：置信度原因
            "next_review_window": next_review,
            "paywall": required_tier,
            "pay_reason": pay_reason,
            "top_risks": top3_findings,
            "reasons": reasons[:3],  # 限制最多3条，但保证至少2条
            "recommended_actions": merged_actions,  # 保证至少5条
            "risk_if_ignore": ignore[:3],  # 限制最多3条，但保证至少2条
            "expert_pack": None,
            "pro_brief": ProBrief(status="coming_soon", summary=None, top_issues=None, recommended_documents=None, export=None),
            "risk_explain": risk_explain,  # ✅ 新增：风险分数解释
            "dont_do": _build_dont_do(stage, risk_score, top3_findings, matched_triggers),
        }
        
        # 根据 unlocked_tier 决定是否生成 expert_pack
        if unlocked_tier == "expert_39":
            meta_with_top = dict(meta or {})
            meta_with_top["top3_findings"] = top3_findings
            decision_dict["expert_pack"] = _expert_pack(stage, industry, decision_level, meta_with_top)
        
        # 按 unlocked_tier 裁剪付费字段
        decision_dict = apply_paywall(decision_dict, required_tier, unlocked_tier)
        
        # 开发环境：验证字段长度（断言）
        if unlocked_tier != "none" and required_tier != "none":
            tier_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(unlocked_tier, 0)
            required_rank = {"none": 0, "basic_15": 1, "expert_39": 2}.get(required_tier, 0)
            if tier_rank >= required_rank:
                assert len(decision_dict["reasons"]) >= 2, f"reasons length {len(decision_dict['reasons'])} < 2 for {decision_level}"
                assert len(decision_dict["recommended_actions"]) >= 5, f"recommended_actions length {len(decision_dict['recommended_actions'])} < 5 for {decision_level}"
                assert len(decision_dict["risk_if_ignore"]) >= 2, f"risk_if_ignore length {len(decision_dict['risk_if_ignore'])} < 2 for {decision_level}"
        
        return DecisionSummarySchema(**decision_dict)

    # 理论上不会到这里，返回默认值（使用模板系统）
    base_template = DECISION_DEFAULT_TEMPLATES.get("OBSERVE_PRE") or DECISION_DEFAULT_TEMPLATES["RISK_AUTONOMO"]
    
    # ✅ 生成风险阶段解释（A/B/C/D）- 默认值
    risk_explain = _build_risk_explain(stage, risk_score, modules, tags, matched_triggers)
    
    decision_dict = {
        "level": "OBSERVE_PRE",
        "decision_intent": "MONITOR",
        "title": base_template["title"],
        "conclusion": "信息不足或输入不完整，请返回重新评估。",
        "confidence_level": "low",
        "confidence_reason": CONFIDENCE_REASON_MAP.get("OBSERVE_PRE", "基于当前输入信号组合与常见合规阈值生成该判断，建议结合实际材料与专业意见确认。"),
        "next_review_window": "30天",
        "paywall": "none",
        "pay_reason": None,
        "top_risks": [],
        "reasons": base_template["reasons"],
        "recommended_actions": base_template["recommended_actions"],
        "risk_if_ignore": base_template["risk_if_ignore"],
        "expert_pack": None,
        "pro_brief": ProBrief(status="coming_soon", summary=None, top_issues=None, recommended_documents=None, export=None),
        "risk_explain": risk_explain,  # ✅ 新增：风险分数解释
        "dont_do": _build_dont_do(stage, risk_score, top3_findings, matched_triggers),
    }
    
    return DecisionSummarySchema(**decision_dict)
