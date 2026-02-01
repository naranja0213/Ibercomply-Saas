"""
行业目录配置
包含所有行业的基础信息：base 分数、标签、中文名称、分组
"""

from typing import Dict, List, Literal

# ========== 行业基础分数 ==========
INDUSTRY_BASE: Dict[str, int] = {
    # A. 零售/门店型
    "bazar": 25,
    "supermarket": 25,
    "phone_shop": 18,
    "clothing_store": 20,
    "gift_shop": 22,
    "pharmacy": 35,  # 高敏感行业
    "cosmetics_retail": 18,
    "stationery_shop": 15,
    
    # B. 餐饮/食品
    "restaurant": 30,
    "takeaway": 22,
    "bar": 28,
    "bubble_tea_shop": 24,
    "bakery": 26,
    "food_processing": 32,  # 小作坊风险高
    
    # C. 服务业/手艺型
    "electronics_repair": 15,
    "beauty": 12,
    "massage_spa": 14,
    "tailoring": 12,
    "photography": 14,
    "printing_advertising": 16,
    
    # D. 平台/灵活就业
    "delivery": 14,
    "ride_sharing": 16,
    "ecommerce": 30,  # 更新：电商/网店
    "wechat_services": 20,
    "social_media": 16,
    
    # E. 通信/技术/安装
    "telecom_agent": 22,
    "fiber_install": 20,
    "it_outsourcing": 18,
    "network_maintenance": 20,
    "pos_installation": 20,
    
    # F. 建筑/劳务/体力型
    "construction": 48,  # 高风险行业
    "construction_labor": 30,
    "cleaning": 18,
    "moving_logistics": 20,
    "warehouse_loading": 22,
    
    # G. 物流/运输
    "logistics_company": 24,
    "freight_forwarding": 26,
    "courier_franchise": 22,
    "warehouse_storage": 20,
    "logistics": 42,  # 新增
    
    # H. 专业服务/公司型
    "advertising_company": 18,
    "consulting_company": 16,
    "import_export": 22,
    "wholesale_company": 20,
    "multi_location": 28,
    "professional_translation": 26,  # 新增
    "professional_consulting": 30,  # 新增
    "professional_it": 32,  # 新增
    "professional_design": 28,  # 新增
    "education_training": 35,  # 新增
    "real_estate_agent": 38,  # 新增
    
    # 兜底
    "other": 10,
}

# ========== 行业中文名称 ==========
INDUSTRY_LABELS: Dict[str, str] = {
    # A. 零售/门店型
    "bazar": "百元店/杂货店",
    "supermarket": "超市/华人食品店",
    "phone_shop": "手机店（卖手机/配件/卡）",
    "clothing_store": "服装店/饰品店",
    "gift_shop": "礼品店/烟酒店",
    "pharmacy": "药店（华人合伙/转让参与）⚠️",
    "cosmetics_retail": "美妆/护肤品零售",
    "stationery_shop": "文具店/打印店",
    
    # B. 餐饮/食品
    "restaurant": "中餐馆",
    "takeaway": "外卖店/Takeaway",
    "bar": "酒吧（华人经营）",
    "bubble_tea_shop": "奶茶店/烧烤店",
    "bakery": "面包店/甜品店",
    "food_processing": "亚洲食品加工/批发（小作坊）⚠️",
    
    # C. 服务业/手艺型
    "electronics_repair": "手机/电子维修",
    "beauty": "美甲/美容/理发",
    "massage_spa": "按摩/养生",
    "tailoring": "裁缝/修鞋",
    "photography": "摄影/视频拍摄",
    "printing_advertising": "广告制作/印刷",
    
    # D. 平台/灵活就业
    "delivery": "外卖骑手（Glovo / Uber Eats）",
    "ride_sharing": "网约车/接送",
    "ecommerce": "电商 / 网店",
    "wechat_services": "微信接单（代购/跑腿/服务）",
    "social_media": "自媒体/带货/小红书合作",
    
    # E. 通信/技术/安装
    "telecom_agent": "手机卡/运营商代理",
    "fiber_install": "光纤安装/上门施工",
    "it_outsourcing": "IT 外包/技术服务",
    "network_maintenance": "网络维护/弱电工程",
    "pos_installation": "POS 安装/系统集成",
    
    # F. 建筑/劳务/体力型
    "construction": "建筑/装修/水电",
    "construction_labor": "工地劳务",
    "cleaning": "清洁/家政",
    "moving_logistics": "搬家/小型物流",
    "warehouse_loading": "仓库装卸/分拣",
    
    # G. 物流/运输
    "logistics_company": "物流公司（本地/跨境）",
    "freight_forwarding": "华人货代",
    "courier_franchise": "快递加盟/直营网点",
    "warehouse_storage": "仓储/中转",
    "logistics": "物流/运输",
    
    # H. 专业服务/公司型
    "advertising_company": "广告公司",
    "consulting_company": "咨询公司",
    "import_export": "进出口贸易",
    "wholesale_company": "批发公司",
    "multi_location": "多门店经营",
    "professional_translation": "翻译",
    "professional_consulting": "咨询",
    "professional_it": "IT / Freelancer",
    "professional_design": "设计",
    "education_training": "教育/培训",
    "real_estate_agent": "房地产中介",
    "advertising_media": "广告 / 传媒",
    "travel_agency": "旅行社 / 旅游服务",
    
    # 兜底
    "other": "其他",
}

# ========== 行业标签 ==========
INDUSTRY_TAGS: Dict[str, List[str]] = {
    # A. 零售/门店型
    "bazar": ["tax", "consumer", "municipal"],
    "supermarket": ["tax", "consumer", "municipal"],
    "phone_shop": ["consumer", "tax", "data"],
    "clothing_store": ["tax", "consumer", "municipal"],
    "gift_shop": ["tax", "consumer", "municipal"],
    "pharmacy": ["tax", "consumer", "municipal", "data"],
    "cosmetics_retail": ["tax", "consumer", "municipal"],
    "stationery_shop": ["tax", "consumer", "municipal"],
    
    # B. 餐饮/食品
    "restaurant": ["tax", "municipal", "consumer", "labor"],
    "takeaway": ["tax", "municipal", "consumer"],
    "bar": ["tax", "municipal", "consumer", "labor"],
    "bubble_tea_shop": ["tax", "municipal", "consumer"],
    "bakery": ["tax", "municipal", "consumer", "labor"],
    "food_processing": ["tax", "municipal", "consumer", "labor", "environment"],
    
    # C. 服务业/手艺型
    "electronics_repair": ["environment", "consumer", "tax"],
    "beauty": ["consumer", "municipal", "tax", "data"],
    "massage_spa": ["consumer", "municipal", "tax", "data"],
    "tailoring": ["consumer", "tax"],
    "photography": ["consumer", "tax", "data"],
    "printing_advertising": ["consumer", "tax", "data"],
    
    # D. 平台/灵活就业
    "delivery": ["labor", "tax"],
    "ride_sharing": ["labor", "tax"],
    "ecommerce": ["tax", "consumer", "customs"],
    "wechat_services": ["tax", "labor", "data"],
    "social_media": ["tax", "data"],
    
    # E. 通信/技术/安装
    "telecom_agent": ["data", "consumer", "tax"],
    "fiber_install": ["labor", "municipal", "tax"],
    "it_outsourcing": ["tax", "data", "labor"],
    "network_maintenance": ["labor", "tax", "data"],
    "pos_installation": ["labor", "tax", "data"],
    
    # F. 建筑/劳务/体力型
    "construction": ["labor", "safety", "tax", "subcontracting"],
    "construction_labor": ["labor", "municipal", "tax"],
    "cleaning": ["labor", "tax"],
    "moving_logistics": ["labor", "tax"],
    "warehouse_loading": ["labor", "tax"],
    
    # G. 物流/运输
    "logistics_company": ["labor", "tax"],
    "freight_forwarding": ["labor", "tax"],
    "courier_franchise": ["labor", "tax"],
    "warehouse_storage": ["labor", "tax", "municipal"],
    "logistics": ["labor", "transport", "insurance", "tax"],
    
    # H. 专业服务/公司型
    "advertising_company": ["tax", "data"],
    "consulting_company": ["tax", "data"],
    "import_export": ["tax", "data"],
    "wholesale_company": ["tax", "consumer"],
    "multi_location": ["tax", "consumer", "municipal", "labor"],
    "professional_translation": ["tax", "invoicing"],
    "professional_consulting": ["tax", "invoicing", "liability"],
    "professional_it": ["tax", "data", "platform"],
    "professional_design": ["tax", "IP"],
    "education_training": ["consumer", "tax", "liability"],
    "real_estate_agent": ["tax", "consumer", "AML"],
    "advertising_media": ["tax", "contract", "data"],
    "travel_agency": ["consumer", "municipal", "tax"],
    
    # 兜底
    "other": ["tax"],
}

# ========== 行业分组（供前端使用） ==========
INDUSTRY_GROUPS: List[Dict[str, any]] = [
    {
        "label": "零售/门店型",
        "items": [
            {"key": "bazar", "label": "百元店/杂货店"},
            {"key": "supermarket", "label": "超市/华人食品店"},
            {"key": "phone_shop", "label": "手机店（卖手机/配件/卡）"},
            {"key": "clothing_store", "label": "服装店/饰品店"},
            {"key": "gift_shop", "label": "礼品店/烟酒店"},
            {"key": "pharmacy", "label": "药店（华人合伙/转让参与）⚠️"},
            {"key": "cosmetics_retail", "label": "美妆/护肤品零售"},
            {"key": "stationery_shop", "label": "文具店/打印店"},
        ]
    },
    {
        "label": "餐饮/食品",
        "items": [
            {"key": "restaurant", "label": "中餐馆"},
            {"key": "takeaway", "label": "外卖店/Takeaway"},
            {"key": "bar", "label": "酒吧（华人经营）"},
            {"key": "bubble_tea_shop", "label": "奶茶店/烧烤店"},
            {"key": "bakery", "label": "面包店/甜品店"},
            {"key": "food_processing", "label": "亚洲食品加工/批发（小作坊）⚠️"},
        ]
    },
    {
        "label": "服务业/手艺型",
        "items": [
            {"key": "electronics_repair", "label": "手机/电子维修"},
            {"key": "beauty", "label": "美甲/美容/理发"},
            {"key": "massage_spa", "label": "按摩/养生"},
            {"key": "tailoring", "label": "裁缝/修鞋"},
            {"key": "photography", "label": "摄影/视频拍摄"},
            {"key": "printing_advertising", "label": "广告制作/印刷"},
        ]
    },
    {
        "label": "平台/灵活就业",
        "items": [
            {"key": "delivery", "label": "外卖骑手（Glovo / Uber Eats）"},
            {"key": "ride_sharing", "label": "网约车/接送"},
            {"key": "ecommerce", "label": "Amazon / 电商"},
            {"key": "wechat_services", "label": "微信接单（代购/跑腿/服务）"},
            {"key": "social_media", "label": "自媒体/带货/小红书合作"},
        ]
    },
    {
        "label": "通信/技术/安装",
        "items": [
            {"key": "telecom_agent", "label": "手机卡/运营商代理"},
            {"key": "fiber_install", "label": "光纤安装/上门施工"},
            {"key": "it_outsourcing", "label": "IT 外包/技术服务"},
            {"key": "network_maintenance", "label": "网络维护/弱电工程"},
            {"key": "pos_installation", "label": "POS 安装/系统集成"},
        ]
    },
    {
        "label": "建筑/劳务/体力型",
        "items": [
            {"key": "construction", "label": "装修/水电"},
            {"key": "construction_labor", "label": "工地劳务"},
            {"key": "cleaning", "label": "清洁/家政"},
            {"key": "moving_logistics", "label": "搬家/小型物流"},
            {"key": "warehouse_loading", "label": "仓库装卸/分拣"},
        ]
    },
    {
        "label": "物流/运输",
        "items": [
            {"key": "logistics_company", "label": "物流公司（本地/跨境）"},
            {"key": "freight_forwarding", "label": "华人货代"},
            {"key": "courier_franchise", "label": "快递加盟/直营网点"},
            {"key": "warehouse_storage", "label": "仓储/中转"},
        ]
    },
    {
        "label": "专业服务/公司型",
        "items": [
            {"key": "advertising_company", "label": "广告公司"},
            {"key": "consulting_company", "label": "咨询公司"},
            {"key": "import_export", "label": "进出口贸易"},
            {"key": "wholesale_company", "label": "批发公司"},
            {"key": "multi_location", "label": "多门店经营"},
        ]
    },
    {
        "label": "其他",
        "items": [
            {"key": "other", "label": "其他"},
        ]
    },
]


def get_industry_base(industry_key: str) -> int:
    """获取行业基础分数"""
    return INDUSTRY_BASE.get(industry_key.lower(), 10)


def get_industry_tags(industry_key: str) -> List[str]:
    """获取行业标签"""
    return INDUSTRY_TAGS.get(industry_key.lower(), ["tax"])


def get_industry_label(industry_key: str) -> str:
    """获取行业中文名称"""
    return INDUSTRY_LABELS.get(industry_key.lower(), "其他")

