// 行业列表（通信行业已拆分）
export const INDUSTRIES = [
  { value: "bazar", label: "百元店/百货" },
  { value: "supermarket", label: "超市" },
  { value: "restaurant", label: "餐厅" },
  { value: "bar", label: "酒吧" },
  { value: "takeaway", label: "外卖店" },
  { value: "telecom_agent", label: "手机卡代理/套餐办理" },
  { value: "fiber_install", label: "光纤安装/Orange/Vodafone 代理" },
  { value: "phone_shop", label: "手机店/配件零售" },
  { value: "electronics_repair", label: "电子产品维修" },
  { value: "beauty", label: "美容美发" },
  { value: "delivery", label: "配送/外卖" },
  { value: "construction", label: "建筑/装修/水电" },
  { value: "logistics", label: "物流/运输" },
  { value: "professional_translation", label: "翻译" },
  { value: "professional_consulting", label: "咨询" },
  { value: "professional_it", label: "IT / Freelancer" },
  { value: "professional_design", label: "设计" },
  { value: "education_training", label: "教育/培训" },
  { value: "real_estate_agent", label: "房地产中介" },
  { value: "advertising_media", label: "广告 / 传媒" },
  { value: "travel_agency", label: "旅行社 / 旅游服务" },
  { value: "ecommerce", label: "电商 / 网店" },
  { value: "other", label: "其他" },
];

// 收入选项（保留以兼容旧代码，但新代码使用 INCOME_PRESETS_BY_STAGE）
export const INCOME_OPTIONS = [500, 1000, 1500, 2000, 3000, 5000, 7000, 10000];

// 收入快捷档位（按阶段）
export const INCOME_PRESETS_BY_STAGE: Record<string, number[]> = {
  PRE_AUTONOMO: [0, 300, 500, 800, 1000, 1500, 2000, 3000, 5000],
  AUTONOMO: [500, 1000, 1500, 2000, 3000, 5000, 7000, 10000],
  SL: [2000, 3000, 5000, 7000, 10000, 15000, 20000],
};

// Slider 配置（按阶段）
export function getSliderConfig(stage: string | null) {
  if (stage === "PRE_AUTONOMO") return { min: 0, max: 5000, step: 50 };
  if (stage === "SL") return { min: 0, max: 20000, step: 250 };
  return { min: 0, max: 10000, step: 100 }; // AUTONOMO default
}

// 收入区间标签（用于 UI 显示）
export function getIncomeBandLabel(v: number): string {
  if (v === 0) return "还没开始/收入不稳定";
  if (v < 500) return "€0–€499（极低/试水）";
  if (v < 1000) return "€500–€999（低）";
  if (v < 2000) return "€1000–€1999（中）";
  if (v < 3000) return "€2000–€2999（常见）";
  if (v < 5000) return "€3000–€4999（增长）";
  if (v < 10000) return "€5000–€9999（高）";
  if (v < 20000) return "€10000–€19999（很高）";
  return "≥€20000（极高）";
}

// 行业对应的 signals 配置（v2 规则表）
export const INDUSTRY_SIGNALS: Record<string, Array<{
  key: string;
  label: string;
  description: string;
}>> = {
  // 零售行业（bazar / supermarket / phone_shop）
  bazar: [
    { key: "sells_imported_goods", label: "销售进口商品", description: "销售进口商品需要完整票据和标签，抽查更多" },
    { key: "sells_branded_goods", label: "销售品牌商品", description: "如 Nike、Adidas 等知名品牌，需要进货凭证" },
    { key: "keeps_supplier_invoices", label: "已保存供应商发票", description: "有完整的进货发票记录" },
    { key: "has_product_labels", label: "商品标签齐全", description: "商品标签齐全能减少消费品罚单" },
    { key: "sells_electronics", label: "销售电子产品", description: "电子产品需要 CE 认证，安全类被查概率更高" },
    { key: "sells_children_products", label: "销售儿童用品", description: "儿童用品监管更严格，需要符合安全标准" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释收入压力更高" },
    { key: "pos_used_daily", label: "使用 POS 机", description: "POS 机可追溯性增加（需要保持账目一致）" },
  ],
  supermarket: [
    { key: "sells_imported_goods", label: "销售进口商品", description: "销售进口商品需要完整票据和标签，抽查更多" },
    { key: "sells_branded_goods", label: "销售品牌商品", description: "如 Nike、Adidas 等知名品牌，需要进货凭证" },
    { key: "keeps_supplier_invoices", label: "已保存供应商发票", description: "有完整的进货发票记录" },
    { key: "has_product_labels", label: "商品标签齐全", description: "商品标签齐全能减少消费品罚单" },
    { key: "sells_electronics", label: "销售电子产品", description: "电子产品需要 CE 认证，安全类被查概率更高" },
    { key: "sells_children_products", label: "销售儿童用品", description: "儿童用品监管更严格，需要符合安全标准" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释收入压力更高" },
    { key: "pos_used_daily", label: "使用 POS 机", description: "POS 机可追溯性增加（需要保持账目一致）" },
  ],
  phone_shop: [
    { key: "sells_imported_goods", label: "销售进口商品", description: "销售进口商品需要完整票据和标签，抽查更多" },
    { key: "sells_branded_goods", label: "销售品牌商品", description: "如品牌手机、配件等，需要进货凭证" },
    { key: "keeps_supplier_invoices", label: "已保存供应商发票", description: "有完整的进货发票记录" },
    { key: "has_product_labels", label: "商品标签齐全", description: "商品标签齐全能减少消费品罚单" },
    { key: "sells_electronics", label: "销售电子产品", description: "电子产品需要 CE 认证，安全类被查概率更高" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释收入压力更高" },
    { key: "pos_used_daily", label: "使用 POS 机", description: "POS 机可追溯性增加（需要保持账目一致）" },
  ],
  // 餐饮行业（restaurant / bar / takeaway）
  restaurant: [
    { key: "serves_alcohol", label: "销售酒精饮料", description: "提供啤酒、红酒等酒精类饮品，需要许可证" },
    { key: "has_terrace", label: "有露台区域", description: "店外有露台或室外座位，需要市政许可" },
    { key: "has_food_hygiene_plan", label: "有食品卫生计划", description: "建立了食品卫生检查记录" },
    { key: "has_emergency_signage", label: "有紧急出口标识", description: "安全项到位，降低检查风险" },
    { key: "has_emergency_lights", label: "有应急灯维护", description: "应急灯维护到位，降低安全风险" },
    { key: "late_opening_hours", label: "营业至深夜", description: "营业至凌晨 12 点以后" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释压力更高" },
    { key: "uses_delivery_platforms", label: "使用配送平台", description: "使用 Glovo、Uber Eats 等平台" },
  ],
  bar: [
    { key: "serves_alcohol", label: "销售酒精饮料", description: "提供啤酒、红酒等酒精类饮品，需要许可证" },
    { key: "has_terrace", label: "有露台区域", description: "店外有露台或室外座位，需要市政许可" },
    { key: "has_food_hygiene_plan", label: "有食品卫生计划", description: "建立了食品卫生检查记录" },
    { key: "has_emergency_signage", label: "有紧急出口标识", description: "安全项到位，降低检查风险" },
    { key: "has_emergency_lights", label: "有应急灯维护", description: "应急灯维护到位，降低安全风险" },
    { key: "late_opening_hours", label: "营业至深夜", description: "营业至凌晨 12 点以后" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释压力更高" },
    { key: "uses_delivery_platforms", label: "使用配送平台", description: "使用 Glovo、Uber Eats 等平台" },
  ],
  takeaway: [
    { key: "serves_alcohol", label: "销售酒精饮料", description: "提供啤酒、红酒等酒精类饮品，需要许可证" },
    { key: "has_terrace", label: "有露台区域", description: "店外有露台或室外座位，需要市政许可" },
    { key: "has_food_hygiene_plan", label: "有食品卫生计划", description: "建立了食品卫生检查记录" },
    { key: "has_emergency_signage", label: "有紧急出口标识", description: "安全项到位，降低检查风险" },
    { key: "has_emergency_lights", label: "有应急灯维护", description: "应急灯维护到位，降低安全风险" },
    { key: "late_opening_hours", label: "营业至深夜", description: "营业至凌晨 12 点以后" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释压力更高" },
    { key: "uses_delivery_platforms", label: "使用配送平台", description: "使用 Glovo、Uber Eats 等平台" },
  ],
  // 通信代理（telecom_agent）
  telecom_agent: [
    { key: "handles_customer_ids", label: "处理客户身份证件", description: "需要复印或扫描客户身份证" },
    { key: "stores_id_photos", label: "保存身份证照片", description: "在系统中保存身份证照片" },
    { key: "issues_service_invoices", label: "开具服务发票", description: "为服务开具发票，票据清晰" },
    { key: "no_data_policy", label: "无数据保护政策", description: "没有建立客户数据保护流程" },
  ],
  // 光纤安装（fiber_install）
  fiber_install: [
    { key: "installs_inside_homes", label: "入户作业", description: "需要在客户家中进行安装作业" },
    { key: "subcontracts_installations", label: "外包安装", description: "将安装工作外包给其他公司或个人" },
    { key: "uses_company_vehicle", label: "使用公司车辆", description: "使用公司车辆进行施工" },
    { key: "issues_service_invoices", label: "开具服务发票", description: "为安装服务开具发票" },
  ],
  // 维修（electronics_repair）
  electronics_repair: [
    { key: "gives_written_warranty", label: "提供书面保修", description: "为维修服务提供书面保修单" },
    { key: "keeps_parts_invoices", label: "保留配件发票", description: "保留购买配件的发票" },
    { key: "handles_e_waste", label: "处理电子废弃物", description: "维修过程中产生电子废弃物" },
    { key: "repairs_branded_devices", label: "维修品牌设备", description: "维修 Apple、Samsung 等品牌设备" },
    { key: "uses_third_party_parts", label: "使用第三方配件", description: "使用非原厂配件" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释压力更高" },
  ],
  // 美业（beauty）
  beauty: [
    { key: "uses_chemicals", label: "使用化学产品", description: "使用染发剂、烫发剂等化学产品" },
    { key: "keeps_client_records", label: "保存客户记录", description: "在系统中保存客户个人信息和记录" },
    { key: "has_safety_training", label: "有安全培训", description: "员工接受过安全培训" },
    { key: "uses_shared_tools", label: "使用共用工具", description: "工具在客户之间共用" },
    { key: "high_cash_ratio", label: "现金比例高", description: "现金交易比例高，解释压力" },
    { key: "no_data_policy", label: "无数据保护政策", description: "没有建立客户数据保护流程" },
  ],
  // 配送（delivery）
  delivery: [
    { key: "works_for_platforms", label: "为平台工作", description: "为 Glovo、Uber Eats 等平台工作" },
    { key: "uses_personal_vehicle", label: "使用个人车辆", description: "使用自己的车或摩托车配送" },
    { key: "has_insurance", label: "有保险", description: "购买了配送相关的保险" },
    { key: "long_working_hours", label: "工作时间长", description: "每天工作超过 8 小时" },
    { key: "no_written_contract", label: "无书面合同", description: "与平台或客户没有书面合同" },
  ],
  // 建筑/装修/水电（construction）
  construction: [
    { key: "has_subcontractors", label: "有分包/转包", description: "责任链复杂，检查频率高" },
    { key: "no_prl_plan", label: "无 PRL 安全计划", description: "建筑行业强制要求" },
    { key: "hi_risk_work", label: "高风险作业", description: "高空、电力、结构施工" },
    { key: "uses_cash_payments", label: "现金支付工人", description: "劳工与税务双重风险" },
    { key: "no_insurance", label: "无责任/工伤保险", description: "事故时处罚极重" },
  ],
  // 物流/运输（logistics）
  logistics: [
    { key: "owns_vehicles", label: "自有运输车辆", description: "需商业车辆保险" },
    { key: "has_drivers", label: "雇佣司机", description: "用工与工时监管严格" },
    { key: "long_working_hours", label: "长工时运输", description: "易触发劳工检查" },
    { key: "no_transport_insurance", label: "无运输保险", description: "事故风险极高" },
  ],
  // 翻译（professional_translation）
  professional_translation: [
    { key: "works_with_companies", label: "B2B 客户", description: "发票与合同要求高" },
    { key: "foreign_clients", label: "海外客户", description: "跨境税务注意" },
    { key: "no_written_contract", label: "无合同", description: "收入解释风险" },
  ],
  // 咨询（professional_consulting）
  professional_consulting: [
    { key: "high_income", label: "收入较高", description: "税务关注度上升" },
    { key: "no_contracts", label: "无服务合同", description: "纠纷与税务风险" },
    { key: "foreign_clients", label: "海外客户", description: "跨境申报风险" },
  ],
  // IT / Freelancer（professional_it）
  professional_it: [
    { key: "works_on_platforms", label: "平台接单", description: "收入可追溯" },
    { key: "foreign_clients", label: "海外客户", description: "跨境税务" },
    { key: "handles_client_data", label: "处理客户数据", description: "RGPD 风险" },
  ],
  // 设计（professional_design）
  professional_design: [
    { key: "sells_ip", label: "出售知识产权", description: "版权与合同问题" },
    { key: "no_written_contract", label: "无合同", description: "收入解释风险" },
    { key: "foreign_clients", label: "海外客户", description: "税务复杂度提升" },
  ],
  // 教育/培训（education_training）
  education_training: [
    { key: "charges_individuals", label: "直接向个人收费", description: "消费者保护风险" },
    { key: "no_certification", label: "无资质", description: "部分培训需备案" },
    { key: "works_with_minors", label: "涉及未成年人", description: "监管更严格" },
  ],
  // 房地产中介（real_estate_agent）
  real_estate_agent: [
    { key: "handles_large_payments", label: "经手大额款项", description: "反洗钱关注" },
    { key: "charges_commission", label: "收取佣金", description: "收入申报敏感" },
    { key: "no_written_mandate", label: "无委托合同", description: "纠纷与税务风险" },
  ],
  // 广告/传媒（advertising_media）
  advertising_media: [
    { key: "no_written_contracts", label: "无正式服务合同", description: "未签服务合同，收入解释与开票一致性风险更高" },
    { key: "foreign_clients", label: "海外客户较多", description: "涉及跨境服务，VAT/申报口径更复杂" },
    { key: "handles_client_data", label: "处理客户数据/营销数据", description: "涉及客户资料或投放数据，需要符合 RGPD" },
    { key: "platform_payments", label: "通过平台/中介收款", description: "平台流水可追溯，需与开票/申报一致" },
  ],
  // 旅行社/旅游服务（travel_agency）
  travel_agency: [
    { key: "no_travel_license", label: "未取得旅行社相关许可", description: "旅行社是高监管行业，许可/备案缺失风险显著" },
    { key: "handles_prepayments", label: "收取客户预付款/订金", description: "预收款需明确合同条款、退款规则与凭证留存" },
    { key: "no_liability_insurance", label: "未购买责任保险", description: "缺少责任险会放大纠纷与投诉风险" },
    { key: "complaints_from_clients", label: "客户投诉风险较高", description: "投诉是旅行服务行业常见检查触发点之一" },
  ],
  // 电商/网店（ecommerce）- 更新配置
  ecommerce: [
    { key: "cross_border_sales", label: "跨境销售（欧盟内/欧盟外）", description: "可能涉及 OSS/IOSS 与跨境 VAT 申报" },
    { key: "platform_sales", label: "平台销售（Amazon/Shopify 等）", description: "平台数据可追溯，需与开票/申报一致" },
    { key: "no_return_policy", label: "未明确退货/退款政策", description: "消费者保护要求明确退货机制与告知义务" },
    { key: "dropshipping", label: "代发货/供应链不透明", description: "来源与清关责任复杂，解释压力更高" },
  ],
  // 其他
  other: [],
};

// 通用 signals（所有行业都可能用到）
export const COMMON_SIGNALS = [
  { key: "has_prl_insurance", label: "已购买 PRL 保险", description: "为员工购买了工伤预防保险（适用于有员工的行业）" },
];

// 行业标签映射（用于显示）
export const INDUSTRY_LABELS: Record<string, string> = {
  bazar: "百元店/百货",
  supermarket: "超市",
  restaurant: "餐厅",
  bar: "酒吧",
  takeaway: "外卖店",
  telecom_agent: "手机卡代理/套餐办理",
  fiber_install: "光纤安装/Orange/Vodafone 代理",
  phone_shop: "手机店/配件零售",
  electronics_repair: "电子产品维修",
  beauty: "美容美发",
  delivery: "配送/外卖",
  construction: "建筑/装修/水电",
  logistics: "物流/运输",
  professional_translation: "翻译",
  professional_consulting: "咨询",
  professional_it: "IT / Freelancer",
  professional_design: "设计",
  education_training: "教育/培训",
  real_estate_agent: "房地产中介",
  advertising_media: "广告 / 传媒",
  travel_agency: "旅行社 / 旅游服务",
  ecommerce: "电商 / 网店",
  other: "其他",
};
