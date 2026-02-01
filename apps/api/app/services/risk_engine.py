from typing import Literal, List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from ..schemas.assessment import Finding, RiskAssessmentRequest
from .risk.industry_catalog import INDUSTRY_BASE, INDUSTRY_TAGS, get_industry_base, get_industry_tags
from .risk.signals_catalog import SIGNAL_DEFS, INDUSTRY_SIGNALS, INDUSTRY_COMBOS
from .risk.risk_bands import get_risk_band


@dataclass
class SignalRule:
    """Signal 规则"""
    points: int
    severity: Literal["info", "low", "medium", "high"]
    critical: bool
    finding: Finding


@dataclass
class ComboRule:
    """组合规则"""
    condition: Dict[str, bool]  # 需要同时满足的 signals
    points: int
    finding: Finding


@dataclass
class IndustryProfile:
    """行业画像"""
    base: int
    tags: List[str]
    signal_rules: Dict[str, SignalRule]
    combo_rules: List[ComboRule]
    checklist: List[str]


# Signals 权重上限
SIGNALS_POINTS_CAP = 22

# ========== 收入评分配置（按阶段） ==========
INCOME_SCORE_BY_STAGE: Dict[str, List[Tuple[int, int]]] = {
    "PRE_AUTONOMO": [
        (0, 0),
        (1000, 0),
        (2000, 4),
        (3000, 8),
        (5000, 14),
        (7000, 20),
        (10**9, 26),
    ],
    "AUTONOMO": [
        (0, 0),
        (1000, 4),
        (1500, 8),
        (2000, 12),
        (3000, 18),
        (5000, 24),
        (7000, 28),
        (10**9, 30),
    ],
    "SL": [
        (0, 0),
        (2000, 6),
        (3000, 12),
        (5000, 18),
        (7000, 24),
        (10000, 28),
        (15000, 32),
        (10**9, 36),
    ],
}


def calc_income_score(stage: str, monthly_income: Optional[float]) -> Tuple[int, str]:
    """
    按阶段计算收入分数
    返回: (score, band_label)
    """
    if not monthly_income or monthly_income < 0:
        monthly_income = 0.0

    s = (stage or "").upper().strip()
    table = INCOME_SCORE_BY_STAGE.get(s) or INCOME_SCORE_BY_STAGE["AUTONOMO"]

    income = float(monthly_income)

    # table: list[(threshold, score)] sorted by threshold ascending
    # find first threshold > income, use its score
    prev_threshold = 0
    for threshold, score in table:
        if income < threshold:
            # 生成 band label
            if threshold >= 10**9:
                band_label = f"≥€{prev_threshold:.0f}"
            else:
                band_label = f"€{prev_threshold:.0f}–€{threshold - 1:.0f}"
            return int(score), band_label
        prev_threshold = threshold
    
    # 如果收入超过最大值，返回最后一档
    last_score = table[-1][1]
    band_label = f"≥€{prev_threshold:.0f}"
    return int(last_score), band_label


def income_band_label(stage: str, income: float) -> str:
    """
    获取收入区间标签（用于 UI 显示）
    """
    if income == 0:
        return "还没开始/收入不稳定"
    if income < 500:
        return "€0–€499（极低/试水）"
    if income < 1000:
        return "€500–€999（低）"
    if income < 2000:
        return "€1000–€1999（中）"
    if income < 3000:
        return "€2000–€2999（常见）"
    if income < 5000:
        return "€3000–€4999（增长）"
    if income < 10000:
        return "€5000–€9999（高）"
    if income < 20000:
        return "€10000–€19999（很高）"
    return "≥€20000（极高）"


def create_signal_rule(points: int, severity: str, critical: bool, code: str, title: str, detail: str, legal_ref: Optional[str] = None, pro_only: bool = False) -> SignalRule:
    """创建 Signal 规则"""
    return SignalRule(
        points=points,
        severity=severity,
        critical=critical,
        finding=Finding(
            code=code,
            title=title,
            detail=detail,
            severity=severity,
            legal_ref=legal_ref,
            pro_only=pro_only
        )
    )


# 零售行业规则（bazar / supermarket / phone_shop）
RETAIL_SIGNAL_RULES: Dict[str, SignalRule] = {
    "sells_imported_goods": create_signal_rule(6, "medium", False, "RETAIL_IMPORT", "销售进口商品", "进口商品需要完整票据和标签，抽查更多", pro_only=False),
    "sells_branded_goods": create_signal_rule(10, "high", True, "RETAIL_BRAND", "销售品牌商品", "销售品牌商品需要提供进货凭证，否则可能面临扣货和罚款", "Real Decreto 1/2007", False),
    "keeps_supplier_invoices": create_signal_rule(-6, "low", False, "RETAIL_HAS_INVOICES", "已保存供应商发票", "保留完整的进货发票可以有效降低被查风险", pro_only=True),
    "has_product_labels": create_signal_rule(-5, "low", False, "RETAIL_LABELS", "商品标签齐全", "商品标签齐全能减少消费品罚单", pro_only=True),
    "sells_electronics": create_signal_rule(4, "medium", False, "RETAIL_ELECTRONICS", "销售电子产品", "电子产品需要 CE 认证，安全类被查概率更高", pro_only=False),
    "sells_children_products": create_signal_rule(6, "medium", False, "RETAIL_CHILDREN", "销售儿童用品", "儿童用品监管更严格，需要符合安全标准", pro_only=False),
    "high_cash_ratio": create_signal_rule(6, "medium", False, "RETAIL_HIGH_CASH", "现金比例高", "现金比例高，解释收入压力更高", pro_only=True),
    "pos_used_daily": create_signal_rule(2, "low", False, "RETAIL_POS", "使用 POS 机", "POS 机可追溯性增加（需要保持账目一致）", pro_only=True),
}

RETAIL_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
        points=8,
        finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
    ),
    ComboRule(
        condition={"sells_imported_goods": True, "has_product_labels": False},
        points=6,
        finding=Finding(code="COMBO_IMPORT_LABEL", title="进口商品标签不齐", detail="销售进口商品但标签不齐全，可能面临消费者保护罚款", severity="high", pro_only=False)
    ),
]


# 餐饮行业规则（restaurant / bar / takeaway）
FOOD_SIGNAL_RULES: Dict[str, SignalRule] = {
    "serves_alcohol": create_signal_rule(4, "medium", False, "FOOD_ALCOHOL", "销售酒精饮料", "销售酒精饮料需要许可证，检查密度更高", "Ley 17/2011", False),
    "has_terrace": create_signal_rule(8, "high", True, "FOOD_TERRACE", "有露台区域", "外摆/许可范围是高频罚点，需要市政许可", "Ordenanza Municipal", False),
    "has_food_hygiene_plan": create_signal_rule(-6, "low", False, "FOOD_HYGIENE_PLAN", "有食品卫生计划", "有食品卫生计划记录可以大幅降低风险", pro_only=True),
    "has_emergency_signage": create_signal_rule(-4, "low", False, "FOOD_EMERGENCY_SIGNS", "有紧急出口标识", "安全项到位，降低检查风险", pro_only=True),
    "has_emergency_lights": create_signal_rule(-4, "low", False, "FOOD_EMERGENCY_LIGHTS", "有应急灯维护", "应急灯维护到位，降低安全风险", pro_only=True),
    "late_opening_hours": create_signal_rule(6, "medium", False, "FOOD_LATE_HOURS", "营业至深夜", "深夜营业噪音/投诉概率更高", pro_only=False),
    "high_cash_ratio": create_signal_rule(6, "medium", False, "FOOD_HIGH_CASH", "现金比例高", "现金比例高，解释压力更高", pro_only=True),
    "uses_delivery_platforms": create_signal_rule(2, "low", False, "FOOD_DELIVERY", "使用配送平台", "平台流水可对账（风险不高）", pro_only=True),
}

FOOD_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
        points=8,
        finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
    ),
    ComboRule(
        condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
        points=6,
        finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
    ),
]


# 通信代理规则（telecom_agent）
TELECOM_SIGNAL_RULES: Dict[str, SignalRule] = {
    "handles_customer_ids": create_signal_rule(8, "high", True, "TELECOM_IDS", "处理客户身份证件", "处理身份证件需要遵守数据保护法，否则面临高额罚款", "RGPD", False),
    "stores_id_photos": create_signal_rule(10, "high", True, "TELECOM_PHOTOS", "保存身份证照片", "留存证件照片非常敏感，违反数据保护法风险极高", "RGPD", False),
    "issues_service_invoices": create_signal_rule(-4, "low", False, "TELECOM_INVOICES", "开具服务发票", "票据清晰降纠纷+解释压力", pro_only=True),
    "no_data_policy": create_signal_rule(8, "high", True, "TELECOM_NO_POLICY", "无数据保护政策", "没流程=出事概率高，违反 RGPD 可能面临最高 €20M 罚款", "RGPD", False),
}

TELECOM_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"handles_customer_ids": True, "stores_id_photos": True, "no_data_policy": True},
        points=10,
        finding=Finding(code="COMBO_DATA_PROTECTION", title="数据处理无合规流程", detail="处理并保存身份证照片但无数据保护政策，严重违反 RGPD，面临极高罚款风险", severity="high", legal_ref="RGPD", pro_only=False)
    ),
]


# 光纤安装规则（fiber_install）
FIBER_SIGNAL_RULES: Dict[str, SignalRule] = {
    "installs_inside_homes": create_signal_rule(4, "medium", False, "FIBER_HOMES", "入户作业", "入户作业风险更高，需要客户授权和保险", pro_only=False),
    "subcontracts_installations": create_signal_rule(8, "high", True, "FIBER_SUBCONTRACT", "外包安装", "外包责任链/用工风险，需要确保分包商有保险和资质", pro_only=False),
    "uses_company_vehicle": create_signal_rule(2, "low", False, "FIBER_VEHICLE", "使用公司车辆", "成本与用途解释压力", pro_only=True),
    "issues_service_invoices": create_signal_rule(-4, "low", False, "FIBER_INVOICES", "开具服务发票", "服务-收款更清晰", pro_only=True),
}

FIBER_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"subcontracts_installations": True, "installs_inside_homes": True},
        points=6,
        finding=Finding(code="COMBO_SUBCONTRACT_PRL", title="外包+入户施工", detail="外包安装且入户作业，需要确保分包商有 PRL 保险和资质，否则面临用工风险", severity="high", pro_only=False)
    ),
]


# 维修规则（electronics_repair）
REPAIR_SIGNAL_RULES: Dict[str, SignalRule] = {
    "gives_written_warranty": create_signal_rule(-3, "low", False, "REPAIR_WARRANTY", "提供书面保修", "提供保修降纠纷、投诉风险", pro_only=True),
    "keeps_parts_invoices": create_signal_rule(-5, "low", False, "REPAIR_INVOICES", "保留配件发票", "成本来源可解释", pro_only=True),
    "handles_e_waste": create_signal_rule(6, "medium", False, "REPAIR_WASTE", "处理电子废弃物", "电子废弃物需要交给授权的回收公司", "RD 110/2015", False),
    "repairs_branded_devices": create_signal_rule(4, "medium", False, "REPAIR_BRANDED", "维修品牌设备", "维修品牌设备纠纷概率更高", pro_only=False),
    "uses_third_party_parts": create_signal_rule(3, "low", False, "REPAIR_THIRD_PARTY", "使用第三方配件", "需说明来源与质量", pro_only=True),
    "high_cash_ratio": create_signal_rule(5, "medium", False, "REPAIR_HIGH_CASH", "现金比例高", "解释压力更高", pro_only=True),
}

REPAIR_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"handles_e_waste": True, "keeps_parts_invoices": False},
        points=6,
        finding=Finding(code="COMBO_EWASTE_TRACE", title="电子废弃物无票据", detail="处理电子废弃物但无回收凭证，违反环保法规", severity="medium", legal_ref="RD 110/2015", pro_only=False)
    ),
]


# 美业规则（beauty）
BEAUTY_SIGNAL_RULES: Dict[str, SignalRule] = {
    "uses_chemicals": create_signal_rule(4, "medium", False, "BEAUTY_CHEMICALS", "使用化学产品", "使用化学产品需要符合安全/材料合规要求", pro_only=False),
    "keeps_client_records": create_signal_rule(4, "medium", False, "BEAUTY_CLIENT_RECORDS", "保存客户记录", "数据留存风险，需要遵守数据保护法", pro_only=False),
    "has_safety_training": create_signal_rule(-3, "low", False, "BEAUTY_TRAINING", "有安全培训", "安全培训降事故概率", pro_only=True),
    "uses_shared_tools": create_signal_rule(3, "low", False, "BEAUTY_SHARED_TOOLS", "使用共用工具", "卫生/投诉风险", pro_only=True),
    "high_cash_ratio": create_signal_rule(5, "medium", False, "BEAUTY_HIGH_CASH", "现金比例高", "解释压力", pro_only=True),
    "no_data_policy": create_signal_rule(8, "high", True, "BEAUTY_NO_POLICY", "无数据保护政策", "保存客户记录但无数据保护政策，违反 RGPD", "RGPD", False),
}

BEAUTY_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"keeps_client_records": True, "no_data_policy": True},
        points=6,
        finding=Finding(code="COMBO_CLIENT_DATA", title="客户数据无保护流程", detail="保存客户记录但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
    ),
]


# 配送规则（delivery）
DELIVERY_SIGNAL_RULES: Dict[str, SignalRule] = {
    "works_for_platforms": create_signal_rule(2, "low", False, "DELIVERY_PLATFORM", "为平台工作", "平台不等于风险，但可能涉及用工关系", pro_only=False),
    "uses_personal_vehicle": create_signal_rule(2, "low", False, "DELIVERY_VEHICLE", "使用个人车辆", "成本解释", pro_only=True),
    "has_insurance": create_signal_rule(-3, "low", False, "DELIVERY_INSURANCE", "有保险", "降事故风险", pro_only=True),
    "long_working_hours": create_signal_rule(3, "low", False, "DELIVERY_HOURS", "工作时间长", "风险略上升", pro_only=True),
    "no_written_contract": create_signal_rule(6, "medium", True, "DELIVERY_NO_CONTRACT", "无书面合同", "用工/合作关系不清晰，可能面临劳动关系争议", pro_only=False),
}

DELIVERY_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"works_for_platforms": True, "no_written_contract": True},
        points=6,
        finding=Finding(code="COMBO_PLATFORM_LABOR", title="平台接单+无合同", detail="为平台工作但无书面合同，用工关系不清晰，可能面临劳动关系争议", severity="medium", pro_only=False)
    ),
]

# 建筑/劳务规则（construction / labor）
CONSTRUCTION_SIGNAL_RULES: Dict[str, SignalRule] = {
    "subcontracts_work": create_signal_rule(8, "high", True, "CONSTRUCTION_SUBCONTRACT", "外包工程", "外包责任链/用工风险，需要确保分包商有保险和资质", pro_only=False),
    "works_on_site": create_signal_rule(6, "medium", False, "CONSTRUCTION_SITE", "工地作业", "工地作业需要 PRL 保险和安全规范", pro_only=False),
    "uses_heavy_machinery": create_signal_rule(6, "medium", False, "CONSTRUCTION_MACHINERY", "使用重型机械", "机械操作需要资质和保险", pro_only=False),
    "has_prl_insurance": create_signal_rule(-5, "low", False, "CONSTRUCTION_PRL", "有 PRL 保险", "PRL 保险降低用工风险", pro_only=True),
    "has_work_permits": create_signal_rule(-4, "low", False, "CONSTRUCTION_PERMITS", "有施工许可", "施工许可降低市政风险", pro_only=True),
    "high_cash_ratio": create_signal_rule(6, "medium", False, "CONSTRUCTION_HIGH_CASH", "现金比例高", "解释压力更高", pro_only=True),
}

CONSTRUCTION_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"subcontracts_work": True, "has_prl_insurance": False},
        points=8,
        finding=Finding(code="COMBO_CONSTRUCTION_PRL", title="外包工程无 PRL 保险", detail="外包工程但无 PRL 保险，面临用工和事故责任风险", severity="high", pro_only=False)
    ),
]

# 物流/运输规则（logistics / transport）
LOGISTICS_SIGNAL_RULES: Dict[str, SignalRule] = {
    "uses_company_vehicles": create_signal_rule(4, "medium", False, "LOGISTICS_VEHICLES", "使用公司车辆", "车辆成本与用途解释压力", pro_only=False),
    "handles_customs": create_signal_rule(6, "medium", False, "LOGISTICS_CUSTOMS", "处理海关事务", "海关事务需要专业资质和完整单据", pro_only=False),
    "has_warehouse": create_signal_rule(4, "medium", False, "LOGISTICS_WAREHOUSE", "有仓库", "仓库需要许可和保险", pro_only=False),
    "has_transport_license": create_signal_rule(-4, "low", False, "LOGISTICS_LICENSE", "有运输许可证", "运输许可证降低风险", pro_only=True),
    "high_cash_ratio": create_signal_rule(5, "medium", False, "LOGISTICS_HIGH_CASH", "现金比例高", "解释压力", pro_only=True),
}

LOGISTICS_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"handles_customs": True, "has_transport_license": False},
        points=6,
        finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
    ),
]

# 专业服务规则（professional services）
PROFESSIONAL_SIGNAL_RULES: Dict[str, SignalRule] = {
    "handles_client_data": create_signal_rule(6, "medium", False, "PROF_CLIENT_DATA", "处理客户数据", "数据留存风险，需要遵守数据保护法", pro_only=False),
    "has_service_contracts": create_signal_rule(-4, "low", False, "PROF_CONTRACTS", "有服务合同", "合同清晰降纠纷", pro_only=True),
    "issues_invoices": create_signal_rule(-3, "low", False, "PROF_INVOICES", "开具发票", "发票清晰降解释压力", pro_only=True),
    "no_data_policy": create_signal_rule(8, "high", True, "PROF_NO_POLICY", "无数据保护政策", "处理客户数据但无数据保护政策，违反 RGPD", "RGPD", False),
    "high_cash_ratio": create_signal_rule(5, "medium", False, "PROF_HIGH_CASH", "现金比例高", "解释压力", pro_only=True),
}

PROFESSIONAL_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"handles_client_data": True, "no_data_policy": True},
        points=6,
        finding=Finding(code="COMBO_PROF_DATA", title="客户数据无保护流程", detail="处理客户数据但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
    ),
]

# 平台/灵活就业规则（platform / gig economy）
PLATFORM_SIGNAL_RULES: Dict[str, SignalRule] = {
    "works_for_platforms": create_signal_rule(2, "low", False, "PLATFORM_WORK", "为平台工作", "平台不等于风险，但可能涉及用工关系", pro_only=False),
    "no_written_contract": create_signal_rule(6, "medium", True, "PLATFORM_NO_CONTRACT", "无书面合同", "用工/合作关系不清晰，可能面临劳动关系争议", pro_only=False),
    "uses_personal_resources": create_signal_rule(3, "low", False, "PLATFORM_RESOURCES", "使用个人资源", "成本解释压力", pro_only=True),
    "high_platform_income": create_signal_rule(4, "medium", False, "PLATFORM_HIGH_INCOME", "平台收入高", "平台收入可追溯，需要与申报一致", pro_only=False),
    "has_multiple_platforms": create_signal_rule(2, "low", False, "PLATFORM_MULTIPLE", "多平台接单", "多平台收入对账压力", pro_only=True),
}

PLATFORM_COMBO_RULES: List[ComboRule] = [
    ComboRule(
        condition={"works_for_platforms": True, "no_written_contract": True, "high_platform_income": True},
        points=8,
        finding=Finding(code="COMBO_PLATFORM_LABOR_HIGH", title="平台高收入+无合同", detail="平台收入高但无书面合同，用工关系不清晰且对账压力大", severity="high", pro_only=False)
    ),
]

# 广告/传媒规则（advertising_media）
ADVERTISING_SIGNAL_RULES: Dict[str, SignalRule] = {
    "no_written_contracts": create_signal_rule(12, "high", True, "ADV_NO_CONTRACTS", "无正式服务合同", "未与客户签署书面服务合同，收入解释与开票一致性风险更高", pro_only=False),
    "foreign_clients": create_signal_rule(10, "medium", False, "PROF_FOREIGN_CLIENTS", "海外客户较多", "涉及跨境服务，VAT/申报口径更复杂", pro_only=False),
    "handles_client_data": create_signal_rule(8, "medium", False, "PROF_CLIENT_DATA", "处理客户数据/营销数据", "涉及客户资料或投放数据，需遵守 RGPD/数据最小化", pro_only=False),
    "platform_payments": create_signal_rule(6, "medium", False, "ADV_PLATFORM_PAY", "通过平台/中介收款", "平台流水可追溯，需与开票/申报一致", pro_only=False),
}

ADVERTISING_COMBO_RULES: List[ComboRule] = []

# 旅行社规则（travel_agency）
TRAVEL_SIGNAL_RULES: Dict[str, SignalRule] = {
    "no_travel_license": create_signal_rule(18, "high", True, "TRAVEL_NO_LICENSE", "未取得旅行社相关许可", "旅行社属于高监管行业，许可/备案缺失会显著放大处罚风险", pro_only=False),
    "handles_prepayments": create_signal_rule(10, "high", True, "TRAVEL_PREPAY", "收取客户预付款/订金", "预收款需要明确合同条款、退款规则与凭证留存", pro_only=False),
    "no_liability_insurance": create_signal_rule(12, "high", True, "TRAVEL_NO_INSURANCE", "未购买责任保险", "缺少责任险会在纠纷或投诉时显著放大风险与成本", pro_only=False),
    "complaints_from_clients": create_signal_rule(8, "medium", False, "TRAVEL_COMPLAINTS", "客户投诉风险较高", "投诉是旅行服务行业常见的检查触发点之一", pro_only=False),
}

TRAVEL_COMBO_RULES: List[ComboRule] = []

# 电商规则（ecommerce）- 更新配置
ECOMMERCE_SIGNAL_RULES: Dict[str, SignalRule] = {
    "cross_border_sales": create_signal_rule(14, "high", True, "ECOMM_CROSS_BORDER", "跨境销售", "涉及 OSS / IOSS / 跨境 VAT 申报", pro_only=False),
    "no_return_policy": create_signal_rule(10, "high", True, "ECOMM_NO_RETURN", "无退货政策", "消费者保护法要求明确退货机制", pro_only=False),
    "dropshipping": create_signal_rule(8, "medium", False, "ECOMM_DROPSHIP", "使用代发货模式", "商品来源与清关责任复杂", pro_only=False),
    "platform_sales": create_signal_rule(6, "medium", False, "ECOMM_PLATFORM", "平台销售（Amazon / Shopify 等）", "平台数据高度可追溯", pro_only=False),
}

ECOMMERCE_COMBO_RULES: List[ComboRule] = []


# 行业映射表
INDUSTRY_PROFILES: Dict[str, IndustryProfile] = {
    "bazar": IndustryProfile(
        base=25,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目"
        ]
    ),
    "supermarket": IndustryProfile(
        base=25,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目"
        ]
    ),
    "phone_shop": IndustryProfile(
        base=18,
        tags=["consumer", "tax", "data"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保留手机 IMEI 码记录",
            "记录买卖双方身份信息",
            "遵守数据保护规定",
            "建立售后服务体系"
        ]
    ),
    "restaurant": IndustryProfile(
        base=30,
        tags=["tax", "municipal", "consumer", "labor"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得食品卫生许可（Registro Sanitario）",
            "员工持有食品操作证（Manipulador de Alimentos）",
            "建立 HACCP 食品安全记录",
            "定期进行虫害防治并保留记录"
        ]
    ),
    "bar": IndustryProfile(
        base=28,
        tags=["tax", "municipal", "consumer", "labor"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得酒精销售许可证",
            "遵守市政营业时间规定",
            "设置噪音控制措施",
            "员工培训未成年人保护政策"
        ]
    ),
    "takeaway": IndustryProfile(
        base=22,
        tags=["tax", "municipal", "consumer"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得食品卫生许可",
            "建立食品卫生记录",
            "遵守配送平台要求"
        ]
    ),
    "telecom_agent": IndustryProfile(
        base=22,
        tags=["data", "consumer", "tax"],
        signal_rules=TELECOM_SIGNAL_RULES,
        combo_rules=TELECOM_COMBO_RULES,
        checklist=[
            "在 AEPD 注册数据处理活动",
            "制定并张贴隐私政策",
            "建立客户数据访问和删除流程",
            "员工签署数据保护保密协议"
        ]
    ),
    "fiber_install": IndustryProfile(
        base=20,
        tags=["labor", "municipal", "tax"],
        signal_rules=FIBER_SIGNAL_RULES,
        combo_rules=FIBER_COMBO_RULES,
        checklist=[
            "获得市政施工许可",
            "购买施工责任保险",
            "建立施工安全规范",
            "保留施工记录和客户签收"
        ]
    ),
    "electronics_repair": IndustryProfile(
        base=15,
        tags=["environment", "consumer", "tax"],
        signal_rules=REPAIR_SIGNAL_RULES,
        combo_rules=REPAIR_COMBO_RULES,
        checklist=[
            "与授权回收公司签署协议",
            "保留废弃物回收凭证",
            "建立维修记录系统",
            "遵守消费者权益保护法（保修期）"
        ]
    ),
    "beauty": IndustryProfile(
        base=12,
        tags=["consumer", "municipal", "tax", "data"],
        signal_rules=BEAUTY_SIGNAL_RULES,
        combo_rules=BEAUTY_COMBO_RULES,
        checklist=[
            "获得市政卫生许可",
            "使用合格的美容产品",
            "建立客户过敏反应记录",
            "保持清洁和消毒记录"
        ]
    ),
    "delivery": IndustryProfile(
        base=14,
        tags=["labor", "tax"],
        signal_rules=DELIVERY_SIGNAL_RULES,
        combo_rules=DELIVERY_COMBO_RULES,
        checklist=[
            "明确与平台的法律关系",
            "购买合适的商业保险",
            "保留配送记录和收入凭证",
            "建立收入与成本对账体系"
        ]
    ),
    # ========== A. 零售/门店型（新增） ==========
    "clothing_store": IndustryProfile(
        base=20,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目",
            "服装标签齐全（成分、洗涤说明）"
        ]
    ),
    "gift_shop": IndustryProfile(
        base=22,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目",
            "烟酒类商品需要特殊许可"
        ]
    ),
    "pharmacy": IndustryProfile(
        base=35,  # 高敏感行业
        tags=["tax", "consumer", "municipal", "data"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "获得药房经营许可（需专业资质）",
            "保存所有供应商发票（至少 4 年）",
            "建立药品进货登记册",
            "遵守药品存储和销售规定",
            "客户数据保护（RGPD）"
        ]
    ),
    "cosmetics_retail": IndustryProfile(
        base=18,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "化妆品需要 CE 认证和成分标签",
            "定期核对库存与账目"
        ]
    ),
    "stationery_shop": IndustryProfile(
        base=15,
        tags=["tax", "consumer", "municipal"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "定期核对库存与账目",
            "打印服务需要遵守数据保护法"
        ]
    ),
    
    # ========== B. 餐饮/食品（新增） ==========
    "bubble_tea_shop": IndustryProfile(
        base=24,
        tags=["tax", "municipal", "consumer"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得食品卫生许可（Registro Sanitario）",
            "员工持有食品操作证（Manipulador de Alimentos）",
            "建立 HACCP 食品安全记录",
            "定期进行虫害防治并保留记录",
            "配料来源和标签合规"
        ]
    ),
    "bakery": IndustryProfile(
        base=26,
        tags=["tax", "municipal", "consumer", "labor"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得食品卫生许可（Registro Sanitario）",
            "员工持有食品操作证（Manipulador de Alimentos）",
            "建立 HACCP 食品安全记录",
            "定期进行虫害防治并保留记录",
            "原料来源和标签合规"
        ]
    ),
    "food_processing": IndustryProfile(
        base=32,  # 小作坊风险高
        tags=["tax", "municipal", "consumer", "labor", "environment"],
        signal_rules=FOOD_SIGNAL_RULES,
        combo_rules=FOOD_COMBO_RULES,
        checklist=[
            "获得食品加工许可（需专业资质）",
            "建立 HACCP 食品安全记录",
            "遵守食品加工卫生规范",
            "废水处理和环境合规",
            "员工持有食品操作证"
        ]
    ),
    
    # ========== C. 服务业/手艺型（新增） ==========
    "massage_spa": IndustryProfile(
        base=14,
        tags=["consumer", "municipal", "tax", "data"],
        signal_rules=BEAUTY_SIGNAL_RULES,
        combo_rules=BEAUTY_COMBO_RULES,
        checklist=[
            "获得市政卫生许可",
            "使用合格的产品和工具",
            "建立客户过敏反应记录",
            "保持清洁和消毒记录",
            "客户数据保护（RGPD）"
        ]
    ),
    "tailoring": IndustryProfile(
        base=12,
        tags=["consumer", "tax"],
        signal_rules={},
        combo_rules=[],
        checklist=[
            "保留客户订单和收据",
            "建立维修/定制记录",
            "成本票据归档",
            "客户数据保护（如有）"
        ]
    ),
    "photography": IndustryProfile(
        base=14,
        tags=["consumer", "tax", "data"],
        signal_rules=PROFESSIONAL_SIGNAL_RULES,
        combo_rules=PROFESSIONAL_COMBO_RULES,
        checklist=[
            "客户数据保护（RGPD）",
            "建立服务合同和发票系统",
            "保留作品和客户记录",
            "成本票据归档"
        ]
    ),
    "printing_advertising": IndustryProfile(
        base=16,
        tags=["consumer", "tax", "data"],
        signal_rules=PROFESSIONAL_SIGNAL_RULES,
        combo_rules=PROFESSIONAL_COMBO_RULES,
        checklist=[
            "客户数据保护（RGPD）",
            "建立服务合同和发票系统",
            "保留作品和客户记录",
            "成本票据归档",
            "遵守广告法规"
        ]
    ),
    
    # ========== D. 平台/灵活就业（新增） ==========
    "ride_sharing": IndustryProfile(
        base=16,
        tags=["labor", "tax"],
        signal_rules=PLATFORM_SIGNAL_RULES,
        combo_rules=PLATFORM_COMBO_RULES,
        checklist=[
            "明确与平台的法律关系",
            "购买合适的商业保险",
            "保留工作记录和收入凭证",
            "建立收入与成本对账体系",
            "车辆成本与用途解释"
        ]
    ),
    "ecommerce": IndustryProfile(
        base=30,
        tags=["tax", "consumer", "customs"],
        signal_rules=ECOMMERCE_SIGNAL_RULES,
        combo_rules=ECOMMERCE_COMBO_RULES,
        checklist=[
            "平台流水与申报一致",
            "保留订单和收款记录",
            "建立库存与账目对账",
            "建立退货政策（消费者保护）",
            "跨境销售需处理 OSS/IOSS VAT",
            "成本票据归档"
        ]
    ),
    "wechat_services": IndustryProfile(
        base=20,
        tags=["tax", "labor", "data"],
        signal_rules=PLATFORM_SIGNAL_RULES,
        combo_rules=PLATFORM_COMBO_RULES,
        checklist=[
            "明确服务关系和合同",
            "保留订单和收款记录",
            "建立收入与成本对账体系",
            "客户数据保护（RGPD）",
            "成本票据归档"
        ]
    ),
    "social_media": IndustryProfile(
        base=16,
        tags=["tax", "data"],
        signal_rules=PLATFORM_SIGNAL_RULES,
        combo_rules=PLATFORM_COMBO_RULES,
        checklist=[
            "平台收入与申报一致",
            "保留合作合同和收款记录",
            "建立收入与成本对账体系",
            "客户数据保护（RGPD）",
            "成本票据归档"
        ]
    ),
    
    # ========== E. 通信/技术/安装（新增） ==========
    "it_outsourcing": IndustryProfile(
        base=18,
        tags=["tax", "data", "labor"],
        signal_rules=TELECOM_SIGNAL_RULES,
        combo_rules=TELECOM_COMBO_RULES,
        checklist=[
            "在 AEPD 注册数据处理活动（如涉及客户数据）",
            "制定并张贴隐私政策",
            "建立客户数据访问和删除流程",
            "建立服务合同和发票系统",
            "员工签署数据保护保密协议"
        ]
    ),
    "network_maintenance": IndustryProfile(
        base=20,
        tags=["labor", "tax", "data"],
        signal_rules=FIBER_SIGNAL_RULES,
        combo_rules=FIBER_COMBO_RULES,
        checklist=[
            "获得市政施工许可（如需要）",
            "购买施工责任保险",
            "建立施工安全规范",
            "保留施工记录和客户签收",
            "客户数据保护（如有）"
        ]
    ),
    "pos_installation": IndustryProfile(
        base=20,
        tags=["labor", "tax", "data"],
        signal_rules=FIBER_SIGNAL_RULES,
        combo_rules=FIBER_COMBO_RULES,
        checklist=[
            "获得市政施工许可（如需要）",
            "购买施工责任保险",
            "建立施工安全规范",
            "保留施工记录和客户签收",
            "客户数据保护（如有）"
        ]
    ),
    
    # ========== F. 建筑/劳务/体力型（新增） ==========
    "construction": IndustryProfile(
        base=28,
        tags=["labor", "municipal", "tax"],
        signal_rules=CONSTRUCTION_SIGNAL_RULES,
        combo_rules=CONSTRUCTION_COMBO_RULES,
        checklist=[
            "获得市政施工许可",
            "购买施工责任保险和 PRL 保险",
            "建立施工安全规范",
            "保留施工记录和客户签收",
            "分包商资质和保险齐全"
        ]
    ),
    "construction_labor": IndustryProfile(
        base=30,
        tags=["labor", "municipal", "tax"],
        signal_rules=CONSTRUCTION_SIGNAL_RULES,
        combo_rules=CONSTRUCTION_COMBO_RULES,
        checklist=[
            "获得市政施工许可",
            "购买施工责任保险和 PRL 保险",
            "建立施工安全规范",
            "保留施工记录和客户签收",
            "分包商资质和保险齐全",
            "用工合同和社保齐全"
        ]
    ),
    "cleaning": IndustryProfile(
        base=18,
        tags=["labor", "tax"],
        signal_rules=CONSTRUCTION_SIGNAL_RULES,
        combo_rules=CONSTRUCTION_COMBO_RULES,
        checklist=[
            "购买商业保险和 PRL 保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "用工合同和社保齐全（如有员工）"
        ]
    ),
    "moving_logistics": IndustryProfile(
        base=20,
        tags=["labor", "tax"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得运输许可证",
            "购买商业保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "车辆成本与用途解释"
        ]
    ),
    "warehouse_loading": IndustryProfile(
        base=22,
        tags=["labor", "tax"],
        signal_rules=CONSTRUCTION_SIGNAL_RULES,
        combo_rules=CONSTRUCTION_COMBO_RULES,
        checklist=[
            "购买商业保险和 PRL 保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "用工合同和社保齐全（如有员工）"
        ]
    ),
    
    # ========== G. 物流/运输（新增） ==========
    "logistics_company": IndustryProfile(
        base=24,
        tags=["labor", "tax"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得运输许可证",
            "购买商业保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "车辆成本与用途解释",
            "海关事务需要专业资质和完整单据"
        ]
    ),
    "freight_forwarding": IndustryProfile(
        base=26,
        tags=["labor", "tax"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得运输许可证和海关代理资质",
            "购买商业保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "海关事务需要专业资质和完整单据"
        ]
    ),
    "courier_franchise": IndustryProfile(
        base=22,
        tags=["labor", "tax"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得运输许可证",
            "购买商业保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "车辆成本与用途解释"
        ]
    ),
    "warehouse_storage": IndustryProfile(
        base=20,
        tags=["labor", "tax", "municipal"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得仓库许可",
            "购买商业保险",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "遵守仓库安全规范"
        ]
    ),
    
    # ========== H. 专业服务/公司型（新增） ==========
    "advertising_company": IndustryProfile(
        base=18,
        tags=["tax", "data"],
        signal_rules=PROFESSIONAL_SIGNAL_RULES,
        combo_rules=PROFESSIONAL_COMBO_RULES,
        checklist=[
            "客户数据保护（RGPD）",
            "建立服务合同和发票系统",
            "保留作品和客户记录",
            "成本票据归档",
            "遵守广告法规"
        ]
    ),
    "consulting_company": IndustryProfile(
        base=16,
        tags=["tax", "data"],
        signal_rules=PROFESSIONAL_SIGNAL_RULES,
        combo_rules=PROFESSIONAL_COMBO_RULES,
        checklist=[
            "客户数据保护（RGPD）",
            "建立服务合同和发票系统",
            "保留服务记录和客户记录",
            "成本票据归档"
        ]
    ),
    "import_export": IndustryProfile(
        base=22,
        tags=["tax", "data"],
        signal_rules=LOGISTICS_SIGNAL_RULES,
        combo_rules=LOGISTICS_COMBO_RULES,
        checklist=[
            "获得进出口许可和海关代理资质",
            "建立服务合同和发票系统",
            "保留服务记录和客户签收",
            "海关事务需要专业资质和完整单据",
            "客户数据保护（如有）"
        ]
    ),
    "wholesale_company": IndustryProfile(
        base=20,
        tags=["tax", "consumer"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目",
            "建立服务合同和发票系统"
        ]
    ),
    "multi_location": IndustryProfile(
        base=28,
        tags=["tax", "consumer", "municipal", "labor"],
        signal_rules=RETAIL_SIGNAL_RULES,
        combo_rules=RETAIL_COMBO_RULES,
        checklist=[
            "每个门店都需要独立许可和保险",
            "保存所有供应商发票（至少 4 年）",
            "建立商品进货登记册",
            "保留品牌商品授权证明或进货凭证",
            "定期核对库存与账目",
            "用工合同和社保齐全"
        ]
    ),
    
    # ========== J. 新增行业 ==========
    "advertising_media": IndustryProfile(
        base=24,
        tags=["tax", "contract", "data"],
        signal_rules=ADVERTISING_SIGNAL_RULES,
        combo_rules=ADVERTISING_COMBO_RULES,
        checklist=[
            "与客户签署正式服务合同",
            "建立发票与对账系统",
            "客户数据保护（RGPD）",
            "跨境服务 VAT 申报",
            "成本票据归档"
        ]
    ),
    "travel_agency": IndustryProfile(
        base=34,
        tags=["consumer", "municipal", "tax"],
        signal_rules=TRAVEL_SIGNAL_RULES,
        combo_rules=TRAVEL_COMBO_RULES,
        checklist=[
            "取得自治区旅行社许可",
            "购买责任保险",
            "建立预收款合同与退款机制",
            "建立客户投诉处理流程",
            "保留服务记录和发票",
            "成本票据归档"
        ]
    ),
    
    # ========== 兜底 ==========
    "other": IndustryProfile(
        base=10,
        tags=["tax"],
        signal_rules={},
        combo_rules=[],
        checklist=[
            "了解您所在行业的具体法规要求",
            "保持完整的财务记录",
            "定期咨询税务和法律顾问"
        ]
    )
}


def check_combo_condition(combo: ComboRule, signals: Dict[str, bool]) -> bool:
    """检查组合条件是否满足"""
    return all(signals.get(key, False) == value for key, value in combo.condition.items())


# 模块化 points 上限（避免全红）
SIGNALS_POINTS_CAP = 22
INCOME_POINTS_CAP = 22
EMP_POINTS_CAP = 18
POS_POINTS_CAP = 10


def assess_risk_v2(request: RiskAssessmentRequest) -> Tuple[int, str, List[Finding], Dict[str, Any]]:
    """
    Risk Engine v3
    基于 IndustryProfile、signals、组合加成等计算风险
    
    核心原则：
    - 只输出风险事实，不输出行动建议
    - Finding 文案必须中性，不能包含"建议注册/必须注册/SL/autónomo"等动作性结论
    - 所有"建议注册/建议SL"等结论由 Decision Engine 产出
    
    返回: (score, level, findings, meta)
    """
    score = 0
    findings: List[Finding] = []
    critical_count = 0
    finding_sources: Dict[str, Dict[str, List[str]]] = {}
    
    # 获取行业画像
    industry_key = request.industry.lower()
    profile = INDUSTRY_PROFILES.get(industry_key, INDUSTRY_PROFILES["other"])
    
    # 基础分
    score += profile.base
    
    # Signals 触发规则
    signals_points = 0
    for signal_key, is_triggered in request.signals.items():
        if is_triggered and signal_key in profile.signal_rules:
            rule = profile.signal_rules[signal_key]
            signals_points += rule.points
            findings.append(rule.finding)
            finding_sources.setdefault(rule.finding.code, {}).setdefault("signal_keys", []).append(signal_key)
            if rule.critical:
                critical_count += 1
    
    # Signals 权重上限（A1）
    signals_points = min(signals_points, SIGNALS_POINTS_CAP)
    score += signals_points
    
    # 组合加成（A3）
    matched_triggers: List[str] = []
    combo_points = 0
    for combo in profile.combo_rules:
        if check_combo_condition(combo, request.signals):
            combo_points += combo.points
            findings.append(combo.finding)
            matched_triggers.append(combo.finding.code)
            finding_sources.setdefault(combo.finding.code, {}).setdefault("combo_signals", []).extend(list(combo.condition.keys()))
            # 检查是否是 critical combo
            if combo.finding.code.startswith("COMBO") and combo.finding.severity == "high":
                critical_combo_codes = ["COMBO_BRAND_SOURCE", "COMBO_DATA_PROTECTION", "COMBO_SUBCONTRACT_PRL", 
                                       "COMBO_MUNICIPAL_NOISE", "COMBO_CLIENT_DATA", "COMBO_PLATFORM_LABOR"]
                if combo.finding.code in critical_combo_codes:
                    critical_count += 1
    
    score += combo_points
    
    # 收入风险评估（模块化，带 cap，中性描述）
    income_points = 0
    if request.monthly_income >= 3000:
        income_points = 22
        findings.append(Finding(
            code="INC_HIGH",
            title="收入规模偏高",
            detail=f"月收入约 €{request.monthly_income:.0f}，需要更强的票据与对账体系来解释收入来源。",
            severity="high",
            pro_only=False
        ))
        finding_sources.setdefault("INC_HIGH", {}).setdefault("signal_keys", []).append("income_high")
    elif request.monthly_income >= 1500:
        income_points = 14
        findings.append(Finding(
            code="INC_MEDIUM",
            title="收入规模上升",
            detail=f"月收入约 €{request.monthly_income:.0f}，建议建立固定记账与收款对账流程。",
            severity="medium",
            pro_only=False
        ))
        finding_sources.setdefault("INC_MEDIUM", {}).setdefault("signal_keys", []).append("income_medium")
    else:
        income_points = 6
    
    income_points = min(income_points, INCOME_POINTS_CAP)
    score += income_points
    
    # 雇员风险评估（模块化，带 cap，中性描述）
    emp_points = 0
    if request.employee_count > 0:
        emp_points = 18
        findings.append(Finding(
            code="EMP_PRESENT",
            title="存在用工合规点",
            detail=f"您填写了 {request.employee_count} 名员工/帮工，用工通常涉及合同、社保、工时与PRL等材料准备。",
            severity="high" if request.employee_count >= 3 else "medium",
            pro_only=False
        ))
        finding_sources.setdefault("EMP_PRESENT", {}).setdefault("signal_keys", []).append("employees")
    
    emp_points = min(emp_points, EMP_POINTS_CAP)
    score += emp_points
    
    # POS 风险评估（模块化，带 cap，中性描述）
    pos_points = 0
    if request.has_pos:
        pos_points = 10
        findings.append(Finding(
            code="POS_TRACEABLE",
            title="刷卡流水可追溯性更高",
            detail="刷卡流水更容易被对账与追溯，建议确保收款与申报/账目长期一致。",
            severity="medium",
            pro_only=False
        ))
        finding_sources.setdefault("POS_TRACEABLE", {}).setdefault("signal_keys", []).append("pos_used")
    
    pos_points = min(pos_points, POS_POINTS_CAP)
    score += pos_points
    
    # Stage-based 阶段提示 finding（解释性，不包含行动建议）
    if request.stage == "PRE_AUTONOMO":
        findings.append(Finding(
            code="STAGE_PRE",
            title="当前阶段：尚未登记经营结构",
            detail="本阶段风险通常来自：收入形成但票据/对账/申报体系尚未建立。",
            severity="info",
            pro_only=False
        ))
    elif request.stage == "AUTONOMO":
        findings.append(Finding(
            code="STAGE_AUTONOMO",
            title="当前阶段：已登记为 Autónomo",
            detail="本阶段风险通常来自：申报一致性、票据链、用工材料与许可项。",
            severity="info",
            pro_only=False
        ))
    else:  # stage == "SL"
        findings.append(Finding(
            code="STAGE_SL",
            title="当前阶段：已使用 SL 公司结构",
            detail="本阶段风险通常来自：公司治理、税务申报、雇员合规与合同/数据处理流程。",
            severity="info",
            pro_only=False
        ))
    
    # 最终得分（clamp 到 0-100）
    score = max(0, min(score, 100))
    
    # 确定风险等级
    if score >= 80:
        level = "red"
    elif score >= 60:
        level = "orange"
    elif score >= 40:
        level = "yellow"
    else:
        level = "green"
    
    # 返回 meta 信息（包含 modules breakdown）
    meta = {
        "critical_count": critical_count,
        "tags": profile.tags,
        "matched_triggers": matched_triggers,
        "finding_sources": finding_sources,
        "risk_score": score,
        "modules": {
            "base": profile.base,
            "signals": signals_points,
            "combo": combo_points,
            "income": income_points,
            "employees": emp_points,
            "pos": pos_points
        }
    }
    
    return score, level, findings, meta


def check_combo_condition_v3(combo_condition: Dict[str, bool], signals: Dict[str, bool]) -> bool:
    """检查组合条件是否满足（v3 版本，用于 signals_catalog）"""
    return all(signals.get(key, False) == value for key, value in combo_condition.items())


def assess_risk_v3(request: RiskAssessmentRequest) -> Tuple[int, str, List[Finding], Dict[str, Any]]:
    """
    Risk Engine v3 - 配置驱动版本
    基于 industry_catalog 和 signals_catalog 配置计算风险
    
    核心原则：
    - 只输出风险事实，不输出行动建议
    - Finding 文案必须中性，不能包含"建议注册/必须注册/SL/autónomo"等动作性结论
    - 所有"建议注册/建议SL"等结论由 Decision Engine 产出
    
    返回: (score, level, findings, meta)
    meta 包含：industry_key, base_score, signals_points, matched_triggers, critical_count, tags, modules
    """
    score = 0
    findings: List[Finding] = []
    critical_count = 0
    matched_triggers: List[str] = []
    finding_sources: Dict[str, Dict[str, List[str]]] = {}
    
    # 获取行业 key
    industry_key = request.industry.lower()
    
    # 从配置获取基础分和标签
    base = get_industry_base(industry_key)
    tags = get_industry_tags(industry_key)
    score += base
    
    # 获取该行业允许的信号列表（后端兜底：未知信号会被忽略）
    allowed_signals = set(INDUSTRY_SIGNALS.get(industry_key, []))
    
    # Signals 触发规则（从配置动态生成）
    signals_points = 0
    for signal_key, is_triggered in request.signals.items():
        # 后端兜底：只处理该行业允许的信号，未知信号忽略
        if not is_triggered or signal_key not in allowed_signals:
            continue
        
        # 从配置获取信号定义
        signal_def = SIGNAL_DEFS.get(signal_key)
        if not signal_def:
            continue
        
        signals_points += signal_def.points
        
        # 动态生成 Finding
        findings.append(Finding(
            code=signal_def.code,
            title=signal_def.title,
            detail=signal_def.detail,
            severity=signal_def.severity,
            legal_ref=signal_def.legal_ref,
            pro_only=signal_def.pro_only
        ))
        finding_sources.setdefault(signal_def.code, {}).setdefault("signal_keys", []).append(signal_key)
        
        if signal_def.critical:
            critical_count += 1
    
    # Signals 权重上限
    signals_points = min(signals_points, SIGNALS_POINTS_CAP)
    score += signals_points
    
    # 组合加成（从配置获取）
    combo_points = 0
    combos = INDUSTRY_COMBOS.get(industry_key, [])
    for combo in combos:
        if check_combo_condition_v3(combo.condition, request.signals):
            combo_points += combo.points
            findings.append(combo.finding)
            matched_triggers.append(combo.finding.code)
            finding_sources.setdefault(combo.finding.code, {}).setdefault("combo_signals", []).extend(list(combo.condition.keys()))
            
            # 检查是否是 critical combo
            if combo.finding.code.startswith("COMBO") and combo.finding.severity == "high":
                critical_combo_codes = ["COMBO_BRAND_SOURCE", "COMBO_DATA_PROTECTION", "COMBO_SUBCONTRACT_PRL", 
                                       "COMBO_MUNICIPAL_NOISE", "COMBO_CLIENT_DATA", "COMBO_PLATFORM_LABOR",
                                       "COMBO_PLATFORM_LABOR_HIGH", "COMBO_CONSTRUCTION_PRL", "COMBO_LOGISTICS_CUSTOMS",
                                       "COMBO_PROF_DATA", "COMBO_EWASTE_TRACE", "COMBO_IMPORT_LABEL"]
                if combo.finding.code in critical_combo_codes:
                    critical_count += 1
    
    score += combo_points
    
    # 收入风险评估（使用 stage-aware 分档）
    income_points, income_band = calc_income_score(request.stage, request.monthly_income)
    
    # 根据 stage 和收入金额生成 finding（阈值按 stage 变化）
    income = request.monthly_income or 0
    stage_upper = (request.stage or "").upper().strip()
    
    if stage_upper == "PRE_AUTONOMO":
        # PRE：>=5000 才算 HIGH（对应 14分以上）
        if income >= 5000:
            findings.append(Finding(
                code="INC_HIGH",
                title="收入规模偏高",
                detail=f"月收入约 €{income:.0f}，需要更强的票据与对账体系来解释收入来源。",
                severity="high",
                pro_only=False
            ))
            finding_sources.setdefault("INC_HIGH", {}).setdefault("signal_keys", []).append("income_high")
        elif income >= 2000:
            findings.append(Finding(
                code="INC_MEDIUM",
                title="收入规模上升",
                detail=f"月收入约 €{income:.0f}，建议建立固定记账与收款对账流程。",
                severity="medium",
                pro_only=False
            ))
            finding_sources.setdefault("INC_MEDIUM", {}).setdefault("signal_keys", []).append("income_medium")
        elif income > 0:
            findings.append(Finding(
                code="INC_LOW",
                title="收入规模较低",
                detail=f"月收入约 €{income:.0f}，建议保持基础记录习惯。",
                severity="low",
                pro_only=False
            ))
            finding_sources.setdefault("INC_LOW", {}).setdefault("signal_keys", []).append("income_low")
    elif stage_upper == "SL":
        # SL：>=7000 算 HIGH（对应 24分以上）
        if income >= 7000:
            findings.append(Finding(
                code="INC_HIGH",
                title="收入规模偏高",
                detail=f"月收入约 €{income:.0f}，需要更强的票据与对账体系来解释收入来源。",
                severity="high",
                pro_only=False
            ))
            finding_sources.setdefault("INC_HIGH", {}).setdefault("signal_keys", []).append("income_high")
        elif income >= 3000:
            findings.append(Finding(
                code="INC_MEDIUM",
                title="收入规模上升",
                detail=f"月收入约 €{income:.0f}，建议建立固定记账与收款对账流程。",
                severity="medium",
                pro_only=False
            ))
            finding_sources.setdefault("INC_MEDIUM", {}).setdefault("signal_keys", []).append("income_medium")
        elif income > 0:
            findings.append(Finding(
                code="INC_LOW",
                title="收入规模较低",
                detail=f"月收入约 €{income:.0f}，建议保持基础记录习惯。",
                severity="low",
                pro_only=False
            ))
            finding_sources.setdefault("INC_LOW", {}).setdefault("signal_keys", []).append("income_low")
    else:
        # AUTONOMO：>=3000 算 HIGH（对应 18分以上）
        if income >= 3000:
            findings.append(Finding(
                code="INC_HIGH",
                title="收入规模偏高",
                detail=f"月收入约 €{income:.0f}，需要更强的票据与对账体系来解释收入来源。",
                severity="high",
                pro_only=False
            ))
            finding_sources.setdefault("INC_HIGH", {}).setdefault("signal_keys", []).append("income_high")
        elif income >= 1500:
            findings.append(Finding(
                code="INC_MEDIUM",
                title="收入规模上升",
                detail=f"月收入约 €{income:.0f}，建议建立固定记账与收款对账流程。",
                severity="medium",
                pro_only=False
            ))
            finding_sources.setdefault("INC_MEDIUM", {}).setdefault("signal_keys", []).append("income_medium")
        elif income > 0:
            findings.append(Finding(
                code="INC_LOW",
                title="收入规模较低",
                detail=f"月收入约 €{income:.0f}，建议保持基础记录习惯。",
                severity="low",
                pro_only=False
            ))
            finding_sources.setdefault("INC_LOW", {}).setdefault("signal_keys", []).append("income_low")
    
    score += income_points
    
    # 雇员风险评估（模块化，带 cap，中性描述）
    emp_points = 0
    if request.employee_count > 0:
        emp_points = 18
        findings.append(Finding(
            code="EMP_PRESENT",
            title="存在用工合规点",
            detail=f"您填写了 {request.employee_count} 名员工/帮工，用工通常涉及合同、社保、工时与PRL等材料准备。",
            severity="high" if request.employee_count >= 3 else "medium",
            pro_only=False
        ))
        finding_sources.setdefault("EMP_PRESENT", {}).setdefault("signal_keys", []).append("employees")
    
    emp_points = min(emp_points, EMP_POINTS_CAP)
    score += emp_points
    
    # POS 风险评估（模块化，带 cap，中性描述）
    pos_points = 0
    if request.has_pos:
        pos_points = 10
        findings.append(Finding(
            code="POS_TRACEABLE",
            title="刷卡流水可追溯性更高",
            detail="刷卡流水更容易被对账与追溯，建议确保收款与申报/账目长期一致。",
            severity="medium",
            pro_only=False
        ))
        finding_sources.setdefault("POS_TRACEABLE", {}).setdefault("signal_keys", []).append("pos_used")
    
    pos_points = min(pos_points, POS_POINTS_CAP)
    score += pos_points
    
    # Stage-based 阶段提示 finding（解释性，不包含行动建议）
    if request.stage == "PRE_AUTONOMO":
        findings.append(Finding(
            code="STAGE_PRE",
            title="当前阶段：尚未登记经营结构",
            detail="本阶段风险通常来自：收入形成但票据/对账/申报体系尚未建立。",
            severity="info",
            pro_only=False
        ))
    elif request.stage == "AUTONOMO":
        findings.append(Finding(
            code="STAGE_AUTONOMO",
            title="当前阶段：已登记为 Autónomo",
            detail="本阶段风险通常来自：申报一致性、票据链、用工材料与许可项。",
            severity="info",
            pro_only=False
        ))
    else:  # stage == "SL"
        findings.append(Finding(
            code="STAGE_SL",
            title="当前阶段：已使用 SL 公司结构",
            detail="本阶段风险通常来自：公司治理、税务申报、雇员合规与合同/数据处理流程。",
            severity="info",
            pro_only=False
        ))
    
    # 最终得分（clamp 到 0-100）
    score = max(0, min(score, 100))
    
    # 确定风险等级
    if score >= 80:
        level = "red"
    elif score >= 60:
        level = "orange"
    elif score >= 40:
        level = "yellow"
    else:
        level = "green"
    
    # 获取风险区间（所有用户可见）
    risk_band = get_risk_band(score)
    
    # 构建分数构成（用于专家包，但先在这里计算结构）
    score_breakdown = {
        "industry_base": {
            "score": base,
            "reason": f"{industry_key} 行业通常被视为持续经营活动"
        },
        "signals": [],  # 将在 expert_pack 中填充
        "income": {
            "score": income_points,
            "band": income_band,
            "stage": request.stage,
            "reason": f"月收入约 €{request.monthly_income:.0f}，属于{income_band}区间"
        },
        "employee": {
            "score": emp_points,
            "reason": f"{request.employee_count} 名员工" if request.employee_count > 0 else "无员工"
        },
        "pos": {
            "score": pos_points,
            "reason": "使用 POS 系统" if request.has_pos else "未使用 POS"
        },
        "deductions": []  # 扣分项（如果有）
    }
    
    # 填充 signals 详情（仅用于专家包）
    for signal_key, is_triggered in request.signals.items():
        if not is_triggered or signal_key not in allowed_signals:
            continue
        signal_def = SIGNAL_DEFS.get(signal_key)
        if signal_def:
            score_breakdown["signals"].append({
                "code": signal_def.code,
                "score": signal_def.points,
                "reason": signal_def.title
            })
    
    # 返回增强的 meta 信息（包含 industry_key, risk_band, score_breakdown）
    meta = {
        "industry_key": industry_key,  # ✅ 新增：行业 key
        "base_score": base,  # ✅ 新增：基础分
        "critical_count": critical_count,
        "tags": tags,
        "matched_triggers": matched_triggers,  # ✅ 确保包含所有匹配的触发器
        "finding_sources": finding_sources,
        "risk_score": score,
        "risk_band": risk_band,  # ✅ 新增：风险区间（所有用户可见）
        "score_breakdown": score_breakdown,  # ✅ 新增：分数构成（用于专家包）
        "modules": {
            "base": base,
            "signals": signals_points,
            "combo": combo_points,
            "income": income_points,
            "employees": emp_points,
            "pos": pos_points
        }
    }
    
    return score, level, findings, meta
