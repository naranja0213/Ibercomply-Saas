"""
信号规则目录配置
包含所有信号的定义和行业与信号的映射关系
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from ...schemas.assessment import Finding


@dataclass
class SignalDef:
    """信号定义"""
    points: int
    severity: Literal["info", "low", "medium", "high"]
    critical: bool
    code: str
    title: str
    detail: str
    legal_ref: Optional[str] = None
    pro_only: bool = False


@dataclass
class ComboDef:
    """组合规则定义"""
    condition: Dict[str, bool]
    points: int
    finding: Finding


# ========== 所有信号定义 ==========
SIGNAL_DEFS: Dict[str, SignalDef] = {
    # 零售行业信号
    "sells_imported_goods": SignalDef(6, "medium", False, "RETAIL_IMPORT", "销售进口商品", "进口商品需要完整票据和标签，抽查更多", None, False),
    "sells_branded_goods": SignalDef(10, "high", True, "RETAIL_BRAND", "销售品牌商品", "销售品牌商品需要提供进货凭证，否则可能面临扣货和罚款", "Real Decreto 1/2007", False),
    "keeps_supplier_invoices": SignalDef(-6, "low", False, "RETAIL_HAS_INVOICES", "已保存供应商发票", "保留完整的进货发票可以有效降低被查风险", None, True),
    "has_product_labels": SignalDef(-5, "low", False, "RETAIL_LABELS", "商品标签齐全", "商品标签齐全能减少消费品罚单", None, True),
    "sells_electronics": SignalDef(4, "medium", False, "RETAIL_ELECTRONICS", "销售电子产品", "电子产品需要 CE 认证，安全类被查概率更高", None, False),
    "sells_children_products": SignalDef(6, "medium", False, "RETAIL_CHILDREN", "销售儿童用品", "儿童用品监管更严格，需要符合安全标准", None, False),
    "high_cash_ratio": SignalDef(6, "medium", False, "RETAIL_HIGH_CASH", "现金比例高", "现金比例高，解释收入压力更高", None, True),
    "pos_used_daily": SignalDef(2, "low", False, "RETAIL_POS", "使用 POS 机", "POS 机可追溯性增加（需要保持账目一致）", None, True),
    
    # 餐饮行业信号
    "serves_alcohol": SignalDef(4, "medium", False, "FOOD_ALCOHOL", "销售酒精饮料", "销售酒精饮料需要许可证，检查密度更高", "Ley 17/2011", False),
    "has_terrace": SignalDef(8, "high", True, "FOOD_TERRACE", "有露台区域", "外摆/许可范围是高频罚点，需要市政许可", "Ordenanza Municipal", False),
    "has_food_hygiene_plan": SignalDef(-6, "low", False, "FOOD_HYGIENE_PLAN", "有食品卫生计划", "有食品卫生计划记录可以大幅降低风险", None, True),
    "has_emergency_signage": SignalDef(-4, "low", False, "FOOD_EMERGENCY_SIGNS", "有紧急出口标识", "安全项到位，降低检查风险", None, True),
    "has_emergency_lights": SignalDef(-4, "low", False, "FOOD_EMERGENCY_LIGHTS", "有应急灯维护", "应急灯维护到位，降低安全风险", None, True),
    "late_opening_hours": SignalDef(6, "medium", False, "FOOD_LATE_HOURS", "营业至深夜", "深夜营业噪音/投诉概率更高", None, False),
    "uses_delivery_platforms": SignalDef(2, "low", False, "FOOD_DELIVERY", "使用配送平台", "平台流水可对账（风险不高）", None, True),
    
    # 通信代理信号
    "handles_customer_ids": SignalDef(8, "high", True, "TELECOM_IDS", "处理客户身份证件", "处理身份证件需要遵守数据保护法，否则面临高额罚款", "RGPD", False),
    "stores_id_photos": SignalDef(10, "high", True, "TELECOM_PHOTOS", "保存身份证照片", "留存证件照片非常敏感，违反数据保护法风险极高", "RGPD", False),
    "issues_service_invoices": SignalDef(-4, "low", False, "TELECOM_INVOICES", "开具服务发票", "票据清晰降纠纷+解释压力", None, True),
    "no_data_policy": SignalDef(8, "high", True, "TELECOM_NO_POLICY", "无数据保护政策", "没流程=出事概率高，违反 RGPD 可能面临最高 €20M 罚款", "RGPD", False),
    
    # 光纤安装信号
    "installs_inside_homes": SignalDef(4, "medium", False, "FIBER_HOMES", "入户作业", "入户作业风险更高，需要客户授权和保险", None, False),
    "subcontracts_installations": SignalDef(8, "high", True, "FIBER_SUBCONTRACT", "外包安装", "外包责任链/用工风险，需要确保分包商有保险和资质", None, False),
    "uses_company_vehicle": SignalDef(2, "low", False, "FIBER_VEHICLE", "使用公司车辆", "成本与用途解释压力", None, True),
    
    # 维修信号
    "gives_written_warranty": SignalDef(-3, "low", False, "REPAIR_WARRANTY", "提供书面保修", "提供保修降纠纷、投诉风险", None, True),
    "keeps_parts_invoices": SignalDef(-5, "low", False, "REPAIR_INVOICES", "保留配件发票", "成本来源可解释", None, True),
    "handles_e_waste": SignalDef(6, "medium", False, "REPAIR_WASTE", "处理电子废弃物", "电子废弃物需要交给授权的回收公司", "RD 110/2015", False),
    "repairs_branded_devices": SignalDef(4, "medium", False, "REPAIR_BRANDED", "维修品牌设备", "维修品牌设备纠纷概率更高", None, False),
    "uses_third_party_parts": SignalDef(3, "low", False, "REPAIR_THIRD_PARTY", "使用第三方配件", "需说明来源与质量", None, True),
    
    # 美业信号
    "uses_chemicals": SignalDef(4, "medium", False, "BEAUTY_CHEMICALS", "使用化学产品", "使用化学产品需要符合安全/材料合规要求", None, False),
    "keeps_client_records": SignalDef(4, "medium", False, "BEAUTY_CLIENT_RECORDS", "保存客户记录", "数据留存风险，需要遵守数据保护法", None, False),
    "has_safety_training": SignalDef(-3, "low", False, "BEAUTY_TRAINING", "有安全培训", "安全培训降事故概率", None, True),
    "uses_shared_tools": SignalDef(3, "low", False, "BEAUTY_SHARED_TOOLS", "使用共用工具", "卫生/投诉风险", None, True),
    
    # 配送信号
    "works_for_platforms": SignalDef(2, "low", False, "DELIVERY_PLATFORM", "为平台工作", "平台不等于风险，但可能涉及用工关系", None, False),
    "uses_personal_vehicle": SignalDef(2, "low", False, "DELIVERY_VEHICLE", "使用个人车辆", "成本解释", None, True),
    "has_insurance": SignalDef(-3, "low", False, "DELIVERY_INSURANCE", "有保险", "降事故风险", None, True),
    "long_working_hours": SignalDef(3, "low", False, "DELIVERY_HOURS", "工作时间长", "风险略上升", None, True),
    "no_written_contract": SignalDef(6, "medium", True, "DELIVERY_NO_CONTRACT", "无书面合同", "用工/合作关系不清晰，可能面临劳动关系争议", None, False),
    
    # 建筑/劳务信号
    "subcontracts_work": SignalDef(8, "high", True, "CONSTRUCTION_SUBCONTRACT", "外包工程", "外包责任链/用工风险，需要确保分包商有保险和资质", None, False),
    "works_on_site": SignalDef(6, "medium", False, "CONSTRUCTION_SITE", "工地作业", "工地作业需要 PRL 保险和安全规范", None, False),
    "uses_heavy_machinery": SignalDef(6, "medium", False, "CONSTRUCTION_MACHINERY", "使用重型机械", "机械操作需要资质和保险", None, False),
    "has_prl_insurance": SignalDef(-5, "low", False, "CONSTRUCTION_PRL", "有 PRL 保险", "PRL 保险降低用工风险", None, True),
    "has_work_permits": SignalDef(-4, "low", False, "CONSTRUCTION_PERMITS", "有施工许可", "施工许可降低市政风险", None, True),
    
    # 物流/运输信号
    "uses_company_vehicles": SignalDef(4, "medium", False, "LOGISTICS_VEHICLES", "使用公司车辆", "车辆成本与用途解释压力", None, False),
    "handles_customs": SignalDef(6, "medium", False, "LOGISTICS_CUSTOMS", "处理海关事务", "海关事务需要专业资质和完整单据", None, False),
    "has_warehouse": SignalDef(4, "medium", False, "LOGISTICS_WAREHOUSE", "有仓库", "仓库需要许可和保险", None, False),
    "has_transport_license": SignalDef(-4, "low", False, "LOGISTICS_LICENSE", "有运输许可证", "运输许可证降低风险", None, True),
    
    # 专业服务信号
    "handles_client_data": SignalDef(6, "medium", False, "PROF_CLIENT_DATA", "处理客户数据", "数据留存风险，需要遵守数据保护法", None, False),
    "has_service_contracts": SignalDef(-4, "low", False, "PROF_CONTRACTS", "有服务合同", "合同清晰降纠纷", None, True),
    "issues_invoices": SignalDef(-3, "low", False, "PROF_INVOICES", "开具发票", "发票清晰降解释压力", None, True),
    
    # 平台/灵活就业信号
    "uses_personal_resources": SignalDef(3, "low", False, "PLATFORM_RESOURCES", "使用个人资源", "成本解释压力", None, True),
    "high_platform_income": SignalDef(4, "medium", False, "PLATFORM_HIGH_INCOME", "平台收入高", "平台收入可追溯，需要与申报一致", None, False),
    "has_multiple_platforms": SignalDef(2, "low", False, "PLATFORM_MULTIPLE", "多平台接单", "多平台收入对账压力", None, True),
    
    # 建筑/装修/水电信号（新增）
    "has_subcontractors": SignalDef(8, "high", True, "CONSTRUCTION_SUBCONTRACTORS", "有分包/转包", "责任链复杂，检查频率高", None, False),
    "no_prl_plan": SignalDef(10, "high", True, "CONSTRUCTION_NO_PRL", "无 PRL 安全计划", "建筑行业强制要求", None, False),
    "hi_risk_work": SignalDef(8, "high", True, "CONSTRUCTION_HI_RISK", "高风险作业", "高空、电力、结构施工", None, False),
    "uses_cash_payments": SignalDef(8, "high", True, "CONSTRUCTION_CASH_PAY", "现金支付工人", "劳工与税务双重风险", None, False),
    "no_insurance": SignalDef(10, "high", True, "CONSTRUCTION_NO_INSURANCE", "无责任/工伤保险", "事故时处罚极重", None, False),
    
    # 物流/运输信号（新增）
    "owns_vehicles": SignalDef(6, "medium", False, "LOGISTICS_OWNS_VEHICLES", "自有运输车辆", "需商业车辆保险", None, False),
    "has_drivers": SignalDef(6, "medium", False, "LOGISTICS_HAS_DRIVERS", "雇佣司机", "用工与工时监管严格", None, False),
    "no_transport_insurance": SignalDef(8, "high", True, "LOGISTICS_NO_INSURANCE", "无运输保险", "事故风险极高", None, False),
    
    # 翻译/咨询/IT/设计信号（新增）
    "works_with_companies": SignalDef(4, "medium", False, "PROF_B2B", "B2B 客户", "发票与合同要求高", None, False),
    "foreign_clients": SignalDef(4, "medium", False, "PROF_FOREIGN_CLIENTS", "海外客户", "跨境税务注意", None, False),
    "high_income": SignalDef(4, "medium", False, "PROF_HIGH_INCOME", "收入较高", "税务关注度上升", None, False),
    "no_contracts": SignalDef(6, "medium", True, "PROF_NO_CONTRACTS", "无服务合同", "纠纷与税务风险", None, False),
    "works_on_platforms": SignalDef(2, "low", False, "PROF_PLATFORMS", "平台接单", "收入可追溯", None, False),
    "sells_ip": SignalDef(4, "medium", False, "PROF_SELLS_IP", "出售知识产权", "版权与合同问题", None, False),
    
    # 教育/培训信号（新增）
    "charges_individuals": SignalDef(4, "medium", False, "EDU_CHARGES_INDIVIDUALS", "直接向个人收费", "消费者保护风险", None, False),
    "no_certification": SignalDef(6, "medium", False, "EDU_NO_CERT", "无资质", "部分培训需备案", None, False),
    "works_with_minors": SignalDef(8, "high", True, "EDU_MINORS", "涉及未成年人", "监管更严格", None, False),
    
    # 房地产中介信号（新增）
    "handles_large_payments": SignalDef(8, "high", True, "REAL_ESTATE_LARGE_PAY", "经手大额款项", "反洗钱关注", None, False),
    "charges_commission": SignalDef(4, "medium", False, "REAL_ESTATE_COMMISSION", "收取佣金", "收入申报敏感", None, False),
    "no_written_mandate": SignalDef(6, "medium", True, "REAL_ESTATE_NO_MANDATE", "无委托合同", "纠纷与税务风险", None, False),
    
    # 广告/传媒信号（新增）
    "no_written_contracts": SignalDef(12, "high", True, "ADV_NO_CONTRACTS", "无正式服务合同", "未与客户签署书面服务合同，收入解释与开票一致性风险更高", None, False),
    "platform_payments": SignalDef(6, "medium", False, "ADV_PLATFORM_PAY", "通过平台/中介收款", "平台流水可追溯，需与开票/申报一致", None, False),
    
    # 旅行社信号（新增）
    "no_travel_license": SignalDef(18, "high", True, "TRAVEL_NO_LICENSE", "未取得旅行社相关许可", "旅行社属于高监管行业，许可/备案缺失会显著放大处罚风险", None, False),
    "handles_prepayments": SignalDef(10, "high", True, "TRAVEL_PREPAY", "收取客户预付款/订金", "预收款需要明确合同条款、退款规则与凭证留存", None, False),
    "no_liability_insurance": SignalDef(12, "high", True, "TRAVEL_NO_INSURANCE", "未购买责任保险", "缺少责任险会在纠纷或投诉时显著放大风险与成本", None, False),
    "complaints_from_clients": SignalDef(8, "medium", False, "TRAVEL_COMPLAINTS", "客户投诉风险较高", "投诉是旅行服务行业常见的检查触发点之一", None, False),
    
    # 电商信号（新增）
    "cross_border_sales": SignalDef(14, "high", True, "ECOMM_CROSS_BORDER", "跨境销售（欧盟内/欧盟外）", "可能涉及 OSS/IOSS、跨境 VAT 口径与申报一致性", None, False),
    "platform_sales": SignalDef(6, "medium", False, "ECOMM_PLATFORM", "平台销售（Amazon / eBay / Shopify 等）", "平台流水可追溯，需与开票/申报一致", None, False),
    "no_return_policy": SignalDef(10, "high", True, "ECOMM_NO_RETURN", "未明确退货/退款政策", "消费者保护法要求明确退货机制与告知义务", None, False),
    "dropshipping": SignalDef(8, "medium", False, "ECOMM_DROPSHIP", "使用代发货/供应链不透明", "商品来源/清关责任复杂，易出现来源解释与合规问题", None, False),
}


# ========== 行业与信号映射 ==========
INDUSTRY_SIGNALS: Dict[str, List[str]] = {
    # A. 零售/门店型
    "bazar": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "sells_electronics", "sells_children_products", "high_cash_ratio", "pos_used_daily"],
    "supermarket": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "sells_electronics", "sells_children_products", "high_cash_ratio", "pos_used_daily"],
    "phone_shop": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "sells_electronics", "high_cash_ratio", "pos_used_daily"],
    "clothing_store": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    "gift_shop": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    "pharmacy": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    "cosmetics_retail": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    "stationery_shop": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    
    # B. 餐饮/食品
    "restaurant": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    "takeaway": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    "bar": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    "bubble_tea_shop": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    "bakery": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    "food_processing": ["serves_alcohol", "has_terrace", "has_food_hygiene_plan", "has_emergency_signage", "has_emergency_lights", "late_opening_hours", "high_cash_ratio", "uses_delivery_platforms"],
    
    # C. 服务业/手艺型
    "electronics_repair": ["gives_written_warranty", "keeps_parts_invoices", "handles_e_waste", "repairs_branded_devices", "uses_third_party_parts", "high_cash_ratio"],
    "beauty": ["uses_chemicals", "keeps_client_records", "has_safety_training", "uses_shared_tools", "high_cash_ratio", "no_data_policy"],
    "massage_spa": ["uses_chemicals", "keeps_client_records", "has_safety_training", "uses_shared_tools", "high_cash_ratio", "no_data_policy"],
    "tailoring": [],  # 无特定信号
    "photography": ["handles_client_data", "has_service_contracts", "issues_invoices", "no_data_policy", "high_cash_ratio"],
    "printing_advertising": ["handles_client_data", "has_service_contracts", "issues_invoices", "no_data_policy", "high_cash_ratio"],
    
    # D. 平台/灵活就业
    "delivery": ["works_for_platforms", "uses_personal_vehicle", "has_insurance", "long_working_hours", "no_written_contract"],
    "ride_sharing": ["works_for_platforms", "uses_personal_vehicle", "has_insurance", "long_working_hours", "no_written_contract", "high_platform_income", "has_multiple_platforms"],
    "wechat_services": ["works_for_platforms", "uses_personal_resources", "high_platform_income", "has_multiple_platforms", "no_written_contract"],
    "social_media": ["works_for_platforms", "uses_personal_resources", "high_platform_income", "has_multiple_platforms"],
    
    # E. 通信/技术/安装
    "telecom_agent": ["handles_customer_ids", "stores_id_photos", "issues_service_invoices", "no_data_policy"],
    "fiber_install": ["installs_inside_homes", "subcontracts_installations", "uses_company_vehicle", "issues_service_invoices"],
    "it_outsourcing": ["handles_customer_ids", "stores_id_photos", "issues_service_invoices", "no_data_policy"],
    "network_maintenance": ["installs_inside_homes", "subcontracts_installations", "uses_company_vehicle", "issues_service_invoices"],
    "pos_installation": ["installs_inside_homes", "subcontracts_installations", "uses_company_vehicle", "issues_service_invoices"],
    
    # F. 建筑/劳务/体力型
    "construction": ["has_subcontractors", "no_prl_plan", "hi_risk_work", "uses_cash_payments", "no_insurance"],
    "construction_labor": ["subcontracts_work", "works_on_site", "uses_heavy_machinery", "has_prl_insurance", "has_work_permits", "high_cash_ratio"],
    "cleaning": ["subcontracts_work", "works_on_site", "has_prl_insurance", "high_cash_ratio"],
    "moving_logistics": ["uses_company_vehicles", "has_transport_license", "high_cash_ratio"],
    "warehouse_loading": ["subcontracts_work", "works_on_site", "has_prl_insurance", "high_cash_ratio"],
    
    # G. 物流/运输
    "logistics_company": ["uses_company_vehicles", "handles_customs", "has_warehouse", "has_transport_license", "high_cash_ratio"],
    "freight_forwarding": ["uses_company_vehicles", "handles_customs", "has_warehouse", "has_transport_license", "high_cash_ratio"],
    "courier_franchise": ["uses_company_vehicles", "handles_customs", "has_warehouse", "has_transport_license", "high_cash_ratio"],
    "warehouse_storage": ["uses_company_vehicles", "handles_customs", "has_warehouse", "has_transport_license", "high_cash_ratio"],
    "logistics": ["owns_vehicles", "has_drivers", "long_working_hours", "no_transport_insurance"],
    
    # H. 专业服务/公司型
    "advertising_company": ["handles_client_data", "has_service_contracts", "issues_invoices", "no_data_policy", "high_cash_ratio"],
    "consulting_company": ["handles_client_data", "has_service_contracts", "issues_invoices", "no_data_policy", "high_cash_ratio"],
    "import_export": ["uses_company_vehicles", "handles_customs", "has_warehouse", "has_transport_license", "high_cash_ratio"],
    "wholesale_company": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    "multi_location": ["sells_imported_goods", "sells_branded_goods", "keeps_supplier_invoices", "has_product_labels", "high_cash_ratio", "pos_used_daily"],
    
    # I. 新增专业服务行业
    "professional_translation": ["works_with_companies", "foreign_clients", "no_written_contract"],
    "professional_consulting": ["high_income", "no_contracts", "foreign_clients"],
    "professional_it": ["works_on_platforms", "foreign_clients", "handles_client_data"],
    "professional_design": ["sells_ip", "no_written_contract", "foreign_clients"],
    "education_training": ["charges_individuals", "no_certification", "works_with_minors"],
    "real_estate_agent": ["handles_large_payments", "charges_commission", "no_written_mandate"],
    
    # J. 新增行业
    "advertising_media": ["no_written_contracts", "foreign_clients", "handles_client_data", "platform_payments"],
    "travel_agency": ["no_travel_license", "handles_prepayments", "no_liability_insurance", "complaints_from_clients"],
    "ecommerce": ["cross_border_sales", "platform_sales", "no_return_policy", "dropshipping"],
    
    # 兜底
    "other": [],
}


# ========== 行业组合规则 ==========
INDUSTRY_COMBOS: Dict[str, List[ComboDef]] = {
    # A. 零售/门店型
    "bazar": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
        ComboDef(
            condition={"sells_imported_goods": True, "has_product_labels": False},
            points=6,
            finding=Finding(code="COMBO_IMPORT_LABEL", title="进口商品标签不齐", detail="销售进口商品但标签不齐全，可能面临消费者保护罚款", severity="high", pro_only=False)
        ),
    ],
    "supermarket": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
        ComboDef(
            condition={"sells_imported_goods": True, "has_product_labels": False},
            points=6,
            finding=Finding(code="COMBO_IMPORT_LABEL", title="进口商品标签不齐", detail="销售进口商品但标签不齐全，可能面临消费者保护罚款", severity="high", pro_only=False)
        ),
    ],
    "phone_shop": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "clothing_store": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "gift_shop": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "pharmacy": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "cosmetics_retail": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "stationery_shop": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    
    # B. 餐饮/食品
    "restaurant": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    "takeaway": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    "bar": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    "bubble_tea_shop": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    "bakery": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    "food_processing": [
        ComboDef(
            condition={"has_terrace": True, "serves_alcohol": True, "late_opening_hours": True},
            points=8,
            finding=Finding(code="COMBO_MUNICIPAL_NOISE", title="露台+酒精+深夜营业", detail="露台区域销售酒精且营业至深夜，市政检查和投诉风险显著增加", severity="high", pro_only=False)
        ),
        ComboDef(
            condition={"has_food_hygiene_plan": False, "high_cash_ratio": True},
            points=6,
            finding=Finding(code="COMBO_RECORDS", title="无卫生记录+高现金", detail="无食品卫生记录且现金比例高，解释压力大且检查风险高", severity="high", pro_only=False)
        ),
    ],
    
    # C. 服务业/手艺型
    "electronics_repair": [
        ComboDef(
            condition={"handles_e_waste": True, "keeps_parts_invoices": False},
            points=6,
            finding=Finding(code="COMBO_EWASTE_TRACE", title="电子废弃物无票据", detail="处理电子废弃物但无回收凭证，违反环保法规", severity="medium", legal_ref="RD 110/2015", pro_only=False)
        ),
    ],
    "beauty": [
        ComboDef(
            condition={"keeps_client_records": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_CLIENT_DATA", title="客户数据无保护流程", detail="保存客户记录但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "massage_spa": [
        ComboDef(
            condition={"keeps_client_records": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_CLIENT_DATA", title="客户数据无保护流程", detail="保存客户记录但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "tailoring": [],
    "photography": [
        ComboDef(
            condition={"handles_client_data": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_PROF_DATA", title="客户数据无保护流程", detail="处理客户数据但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "printing_advertising": [
        ComboDef(
            condition={"handles_client_data": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_PROF_DATA", title="客户数据无保护流程", detail="处理客户数据但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    
    # D. 平台/灵活就业
    "delivery": [
        ComboDef(
            condition={"works_for_platforms": True, "no_written_contract": True},
            points=6,
            finding=Finding(code="COMBO_PLATFORM_LABOR", title="平台接单+无合同", detail="为平台工作但无书面合同，用工关系不清晰，可能面临劳动关系争议", severity="medium", pro_only=False)
        ),
    ],
    "ride_sharing": [
        ComboDef(
            condition={"works_for_platforms": True, "no_written_contract": True, "high_platform_income": True},
            points=8,
            finding=Finding(code="COMBO_PLATFORM_LABOR_HIGH", title="平台高收入+无合同", detail="平台收入高但无书面合同，用工关系不清晰且对账压力大", severity="high", pro_only=False)
        ),
    ],
    "ecommerce": [],
    "wechat_services": [
        ComboDef(
            condition={"works_for_platforms": True, "no_written_contract": True, "high_platform_income": True},
            points=8,
            finding=Finding(code="COMBO_PLATFORM_LABOR_HIGH", title="平台高收入+无合同", detail="平台收入高但无书面合同，用工关系不清晰且对账压力大", severity="high", pro_only=False)
        ),
    ],
    "social_media": [
        ComboDef(
            condition={"works_for_platforms": True, "no_written_contract": True, "high_platform_income": True},
            points=8,
            finding=Finding(code="COMBO_PLATFORM_LABOR_HIGH", title="平台高收入+无合同", detail="平台收入高但无书面合同，用工关系不清晰且对账压力大", severity="high", pro_only=False)
        ),
    ],
    
    # E. 通信/技术/安装
    "telecom_agent": [
        ComboDef(
            condition={"handles_customer_ids": True, "stores_id_photos": True, "no_data_policy": True},
            points=10,
            finding=Finding(code="COMBO_DATA_PROTECTION", title="数据处理无合规流程", detail="处理并保存身份证照片但无数据保护政策，严重违反 RGPD，面临极高罚款风险", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "fiber_install": [
        ComboDef(
            condition={"subcontracts_installations": True, "installs_inside_homes": True},
            points=6,
            finding=Finding(code="COMBO_SUBCONTRACT_PRL", title="外包+入户施工", detail="外包安装且入户作业，需要确保分包商有 PRL 保险和资质，否则面临用工风险", severity="high", pro_only=False)
        ),
    ],
    "it_outsourcing": [
        ComboDef(
            condition={"handles_customer_ids": True, "stores_id_photos": True, "no_data_policy": True},
            points=10,
            finding=Finding(code="COMBO_DATA_PROTECTION", title="数据处理无合规流程", detail="处理并保存身份证照片但无数据保护政策，严重违反 RGPD，面临极高罚款风险", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "network_maintenance": [
        ComboDef(
            condition={"subcontracts_installations": True, "installs_inside_homes": True},
            points=6,
            finding=Finding(code="COMBO_SUBCONTRACT_PRL", title="外包+入户施工", detail="外包安装且入户作业，需要确保分包商有 PRL 保险和资质，否则面临用工风险", severity="high", pro_only=False)
        ),
    ],
    "pos_installation": [
        ComboDef(
            condition={"subcontracts_installations": True, "installs_inside_homes": True},
            points=6,
            finding=Finding(code="COMBO_SUBCONTRACT_PRL", title="外包+入户施工", detail="外包安装且入户作业，需要确保分包商有 PRL 保险和资质，否则面临用工风险", severity="high", pro_only=False)
        ),
    ],
    
    # F. 建筑/劳务/体力型
    "construction": [
        ComboDef(
            condition={"subcontracts_work": True, "has_prl_insurance": False},
            points=8,
            finding=Finding(code="COMBO_CONSTRUCTION_PRL", title="外包工程无 PRL 保险", detail="外包工程但无 PRL 保险，面临用工和事故责任风险", severity="high", pro_only=False)
        ),
    ],
    "construction_labor": [
        ComboDef(
            condition={"subcontracts_work": True, "has_prl_insurance": False},
            points=8,
            finding=Finding(code="COMBO_CONSTRUCTION_PRL", title="外包工程无 PRL 保险", detail="外包工程但无 PRL 保险，面临用工和事故责任风险", severity="high", pro_only=False)
        ),
    ],
    "cleaning": [
        ComboDef(
            condition={"subcontracts_work": True, "has_prl_insurance": False},
            points=8,
            finding=Finding(code="COMBO_CONSTRUCTION_PRL", title="外包工程无 PRL 保险", detail="外包工程但无 PRL 保险，面临用工和事故责任风险", severity="high", pro_only=False)
        ),
    ],
    "moving_logistics": [],
    "warehouse_loading": [
        ComboDef(
            condition={"subcontracts_work": True, "has_prl_insurance": False},
            points=8,
            finding=Finding(code="COMBO_CONSTRUCTION_PRL", title="外包工程无 PRL 保险", detail="外包工程但无 PRL 保险，面临用工和事故责任风险", severity="high", pro_only=False)
        ),
    ],
    
    # G. 物流/运输
    "logistics_company": [
        ComboDef(
            condition={"handles_customs": True, "has_transport_license": False},
            points=6,
            finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
        ),
    ],
    "freight_forwarding": [
        ComboDef(
            condition={"handles_customs": True, "has_transport_license": False},
            points=6,
            finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
        ),
    ],
    "courier_franchise": [
        ComboDef(
            condition={"handles_customs": True, "has_transport_license": False},
            points=6,
            finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
        ),
    ],
    "warehouse_storage": [
        ComboDef(
            condition={"handles_customs": True, "has_transport_license": False},
            points=6,
            finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
        ),
    ],
    
    # H. 专业服务/公司型
    "advertising_company": [
        ComboDef(
            condition={"handles_client_data": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_PROF_DATA", title="客户数据无保护流程", detail="处理客户数据但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "consulting_company": [
        ComboDef(
            condition={"handles_client_data": True, "no_data_policy": True},
            points=6,
            finding=Finding(code="COMBO_PROF_DATA", title="客户数据无保护流程", detail="处理客户数据但无数据保护政策，违反数据保护法", severity="high", legal_ref="RGPD", pro_only=False)
        ),
    ],
    "import_export": [
        ComboDef(
            condition={"handles_customs": True, "has_transport_license": False},
            points=6,
            finding=Finding(code="COMBO_LOGISTICS_CUSTOMS", title="处理海关但无运输许可", detail="处理海关事务但无运输许可证，面临高额罚款风险", severity="high", pro_only=False)
        ),
    ],
    "wholesale_company": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    "multi_location": [
        ComboDef(
            condition={"sells_branded_goods": True, "keeps_supplier_invoices": False},
            points=8,
            finding=Finding(code="COMBO_BRAND_SOURCE", title="品牌商品无进货凭证", detail="销售品牌商品但无进货凭证，面临扣货和罚款的高风险", severity="high", legal_ref="Real Decreto 1/2007", pro_only=False)
        ),
    ],
    
    # 兜底
    "other": [],
}

