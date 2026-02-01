"""
Decision 模板字典
保证：每个 decision_code 都必须生成 reasons(>=2)、recommended_actions(>=5)、risk_if_ignore(>=2)
未配置行业模板时用默认模板兜底；并按解锁 tier 裁剪付费字段
"""

from __future__ import annotations

from typing import Dict, List, Literal, TypedDict

PaywallTier = Literal["none", "basic_15", "expert_39"]


class DecisionTemplate(TypedDict):
    title: str
    conclusion: str
    reasons: List[str]
    recommended_actions: List[str]
    risk_if_ignore: List[str]


# ---- 1) 每个 decision_code 的"兜底模板"：永远不为空 ----
DECISION_DEFAULT_TEMPLATES: Dict[str, DecisionTemplate] = {
    # ========== PRE_AUTONOMO ==========
    "OBSERVE_PRE": {
        "title": "当前阶段：暂不急于注册（建议观察）",
        "conclusion": "你目前的风险信号不强，但建议建立基本的票据与记录习惯，避免未来突然被动。",
        "reasons": [
            "当前收入/规模信号不足以形成强注册压力",
            "尚未出现明显的用工/高可追溯收款触发点",
        ],
        "recommended_actions": [
            "建立'收入来源记录'：每笔收入尽量能对应服务/商品说明",
            "保留进货/成本票据（发票、收据、转账凭证）并分类归档",
            "若使用 POS/平台流水：每月做一次对账（流水 vs 申报/记账）",
            "准备一份'被问到收入来源时的解释材料清单'（合同/聊天记录/工单等）",
            "1–3 个月后复评：收入上升或新增员工/外包时立即复评",
        ],
        "risk_if_ignore": [
            "收入增长后才补材料，会导致解释成本变高",
            "票据链缺失会放大被抽查时的沟通压力",
        ],
    },
    "REGISTER_AUTONOMO": {
        "title": "建议注册 Autónomo",
        "conclusion": "你已出现较明确的经营特征。尽早完成注册并把账目与票据流程固定下来，可显著降低后续被追溯处理的风险。",
        "reasons": [
            "收入/经营持续性信号已较为稳定",
            "存在可追溯收款特征，或属于相对更常被关注的经营类型",
        ],
        "recommended_actions": [
            "尽快与 gestoría/税务顾问确认最合适的注册时间点与税制选择",
            "从本月开始建立固定记账流程（收入、成本、发票/收据）",
            "把收款渠道统一：现金、POS、平台流水分别对账归档",
            "准备基础经营材料：合同/工单/报价单/聊天记录截图（可用于解释收入来源）",
            "若涉及员工/帮工：提前咨询社保、合同与工时记录要求",
            "注册后 30 天内复评：根据实际收入与成本结构调整策略",
        ],
        "risk_if_ignore": [
            "若持续经营但未完成注册，未来可能面临补税/补缴情形与行政处罚风险上升",
            "账目与票据链不清晰时，被要求补充说明与材料的成本会显著提高",
        ],
    },
    "STRONG_REGISTER_AUTONOMO": {
        "title": "强烈建议尽快注册 Autónomo",
        "conclusion": "你目前的经营特征已接近或进入高关注区间。建议尽快完成注册并补齐关键材料与对账流程，以降低后续追溯与处罚风险。",
        "reasons": [
            "多项高权重信号叠加（收入/用工/高可追溯收款/行业特征），风险已进入高位区间",
            "若账目与材料不完善，一旦出现核查/投诉等触发因素，处理成本会快速上升",
        ],
        "recommended_actions": [
            "7 天内联系 gestoría：确认注册流程、税种选择、社保缴纳与开票/记账方式",
            "立即建立'日结/周结对账'：收款流水、现金、成本票据能相互对应并留档",
            "优先补齐高风险材料：进货凭证/授权文件/许可证明/安全记录（按行业适用）",
            "若有帮工/员工：尽快完善合同/社保/工时记录，避免劳动与社保风险叠加",
            "整理一份'随时可出示'资料包：经营说明 + 票据链 + 对账记录 + 许可文件（电子版+纸质）",
            "注册完成后 30 天内复评：根据实际收入、成本结构与用工情况优化合规方案",
        ],
        "risk_if_ignore": [
            "若在高暴露状态下继续拖延，出现核查或投诉时更容易触发补税/滞纳金/行政处罚等后果",
            "用工与社保不规范可能引发额外处罚，并显著增加整体合规压力",
        ],
    },
    # ========== AUTONOMO ==========
    "OK_AUTONOMO": {
        "title": "当前阶段：风险可控（Autónomo）",
        "conclusion": "你目前的关键合规点相对稳定，保持对账与票据链完整即可。",
        "reasons": [
            "主要风险触发点较少或已被良好控制",
            "收入与经营规模暂未进入高压区间",
        ],
        "recommended_actions": [
            "维持每月对账：收款流水 vs 发票/记账一致",
            "成本票据分门别类保存（建议至少 4 年）",
            "有 POS/平台流水：单独做月度对账报告并留档",
            "每季度复盘一次：收入/员工/外包/行业变化是否触发新风险",
            "3 个月后复评：收入结构变化或新增业务线时立即复评",
        ],
        "risk_if_ignore": [
            "小问题长期不修复会积累成结构性差异",
            "票据不齐会导致未来扩张时风险突然上升",
        ],
    },
    "RISK_AUTONOMO": {
        "title": "当前阶段：整体风险可控，存在个别需关注点（Autónomo）",
        "conclusion": "你已出现少量更易被关注的经营特征。建议把账目、票据与材料的一致性做扎实，以降低未来进入更高风险区间的概率。",
        "reasons": [
            "部分风险触发点的数量/严重度有所上升",
            "收入/收款可追溯性增强（或经营复杂度上升）导致暴露面扩大",
        ],
        "recommended_actions": [
            "做一次'票据链补全'：供应商发票/收据/转账凭证统一归档",
            "建立固定对账：POS/平台流水、现金收入、开票/记账对齐",
            "补齐行业许可/安全/卫生类记录（如适用）并可随时出示",
            "如果有帮工/临时工：补合同/社保/工时/PRL 记录（按行业）",
            "把高风险业务线单独核算：来源证明、成本凭证、授权文件",
            "30 天后复评：验证风险是否显著下降",
        ],
        "risk_if_ignore": [
            "若出现抽查/核对时材料不足，可能被要求补充说明、补材料，处理成本明显增加",
            "风险点持续叠加可能引发更频繁的信息核查或追溯处理，影响经营稳定性",
        ],
    },
    "CONSIDER_SL": {
        "title": "建议开始评估是否需要成立 SL",
        "conclusion": "你可能已进入'规模上升期'，继续以 Autónomo 承载会带来结构性风险与管理压力。",
        "reasons": [
            "收入与经营复杂度上升（员工/外包/多业务线/责任链）",
            "风险暴露面扩大，需要更公司化的边界与流程",
        ],
        "recommended_actions": [
            "与 gestoría 评估 SL 的成本结构：社保、税制、账务与合规义务",
            "梳理责任链：合同、外包、客户纠纷、数据保护/消费者义务",
            "把业务分层：高风险业务线优先用更清晰的合同与票据框架承载",
            "建立'公司化材料包'：合同模板、发票流程、员工/外包档案",
            "做一次 30 天迁移计划（如果决定成立 SL）：时间点、材料清单、过渡方案",
        ],
        "risk_if_ignore": [
            "规模上升但结构未升级，会导致税务/劳动/责任风险同步放大",
            "纠纷或事故发生时个人责任暴露更高",
        ],
    },
    # ========== SL ==========
    "OK_SL": {
        "title": "当前阶段：风险可控（SL）",
        "conclusion": "公司结构相对稳定，关键是保持账务、合同、数据/用工档案的持续合规。",
        "reasons": [
            "核心风险触发点较少或已建立制度化流程",
            "公司化材料与对账逻辑较完整",
        ],
        "recommended_actions": [
            "固定月度关账与对账：银行流水、发票、费用凭证一致",
            "合同与报价单统一模板化，并集中存档",
            "员工/外包档案齐备：合同、社保、工时、PRL（如适用）",
            "数据保护/消费者条款定期复核（如涉及客户数据）",
            "6 个月后复评：业务扩张/新增门店/新增渠道时提前复评",
        ],
        "risk_if_ignore": [
            "制度松动会造成账务与合同链断裂，后续修复成本高",
            "数据/用工档案缺失容易引发高额罚单或纠纷",
        ],
    },
    "RISK_SL_LOW": {
        "title": "当前阶段：存在风险点（SL）",
        "conclusion": "公司结构是对的，但当前在合同/票据/档案/数据方面存在薄弱点，需要补齐。",
        "reasons": [
            "出现多项可追溯风险点或制度执行不稳定",
            "部分材料链条不完整或记录缺失",
        ],
        "recommended_actions": [
            "补齐合同与票据链：收入必须能对应合同/工单/发票",
            "费用报销制度化：凭证、审批、用途说明齐全",
            "员工/外包档案做一次清点与补齐（合同/社保/PRL）",
            "如处理客户数据：建立最小化留存与删除流程",
            "30 天内做一次内部自检并复评",
        ],
        "risk_if_ignore": [
            "制度缺口在检查/纠纷出现时会迅速变成罚款/诉讼风险",
            "账务与合同不一致会引发税务关注",
        ],
    },
    "RISK_SL_HIGH": {
        "title": "高风险：建议立即整改（SL）",
        "conclusion": "你目前存在高暴露风险点（用工/数据/票据/责任链），建议立刻按清单整改并寻求专业协助。",
        "reasons": [
            "高严重度触发点数量较多（或出现 critical 组合触发）",
            "潜在罚款/纠纷/停业成本显著上升",
        ],
        "recommended_actions": [
            "7 天内完成高风险点整改：用工/数据/许可/票据链优先",
            "对账与合同链立刻补齐：每笔收入可追溯到合同/工单/发票",
            "如涉及客户身份证/敏感数据：立刻停止不合规留存，建立权限与删除流程",
            "检查外包/分包责任链与保险覆盖范围（如适用）",
            "建议联系专业 gestoría/律师做一次专项审查（可作为决策版服务入口）",
        ],
        "risk_if_ignore": [
            "高额罚款与纠纷风险显著增加（尤其是用工与数据保护）",
            "严重情况下可能面临停业整顿或强制整改要求",
        ],
    },
}

# ---- 2) 行业"加成行动清单"模板：按 stage + industry ----
# 只放"差异化动作"，最终会与默认模板合并去重
INDUSTRY_ACTION_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    # retail
    "bazar": {
        "common": [
            "建立供应商清单：每个供应商对应发票/送货单/付款凭证存放位置",
            "对品牌/高风险 SKU 建立来源证明文件夹（授权/发票/合同）",
            "抽检商品标签（警示语/成分/CE/说明书）并拍照留档",
        ],
    },
    "supermarket": {
        "common": [
            "对高周转 SKU 建立'供货商-票据-标签'快速抽查清单",
            "库存与票据定期核对，避免长期差异",
        ],
    },
    "phone_shop": {
        "common": [
            "维修/销售记录与收款对应留档（工单/收据/聊天记录）",
            "若留存客户信息：建立最小化留存与删除流程（RGPD）",
        ],
    },
    # food
    "restaurant": {
        "common": [
            "建立食品卫生自检记录（清洁/温度/过敏原/消毒）并留档",
            "检查紧急出口标识与应急灯维护记录（如适用）",
            "如有露台：核对许可范围与实际摆放一致",
        ],
    },
    "bar": {
        "common": [
            "核对营业时间/噪音相关要求并留档（按所在城市）",
            "如有露台：核对许可与摆放范围，避免高频罚点",
            "应急灯与安全标识定期自检并保留维护凭证",
        ],
    },
    "takeaway": {
        "common": [
            "平台流水与开票/记账建立固定对账流程",
            "配送与食品包装合规要求做一次自检（如适用）",
        ],
    },
    # telecom
    "telecom_agent": {
        "common": [
            "客户身份证信息处理：禁止私聊转发/随意拍照留存，建立权限与删除流程",
            "张贴隐私说明（用途/保留期限/权利），并准备客户查询/删除流程",
        ],
    },
    "fiber_install": {
        "common": [
            "如有分包：核对分包资质、保险与 PRL 记录，明确责任边界",
            "入户施工：保留客户授权/工单签收记录（争议时关键）",
        ],
    },
    # repair
    "electronics_repair": {
        "common": [
            "配件进货票据归档，减少来源解释压力",
            "电子废弃物交接正规回收并保留凭证（如适用）",
            "提供书面收据/保修条款降低纠纷概率",
        ],
    },
    # beauty
    "beauty": {
        "common": [
            "客户记录最小化留存并保护存储（避免散落在个人手机/聊天）",
            "使用产品的说明/成分/安全信息留档（如适用）",
            "工具消毒与卫生记录留档（降低投诉/检查风险）",
        ],
    },
    # delivery
    "delivery": {
        "common": [
            "平台流水与收款记录留档，避免收入解释困难",
            "如长期高强度工作：确认保险覆盖与成本凭证完整",
        ],
    },
}


def merge_actions(base: List[str], extra: List[str], min_len: int = 5) -> List[str]:
    """合并行动清单并去重，确保最小长度"""
    seen = set()
    out: List[str] = []
    for x in (base + extra):
        s = (x or "").strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    # 确保最小长度（兜底填充）
    filler = [
        "每月做一次'流水 vs 记账/开票'对账并留档",
        "把合同/工单/聊天记录按客户或项目归档，便于解释收入来源",
        "准备一份'被检查时的资料清单'，确保 5 分钟内能找齐",
    ]
    for f in filler:
        if len(out) >= min_len:
            break
        if f not in seen:
            out.append(f)
            seen.add(f)
    return out


def normalize_tier(tier: str | None) -> PaywallTier:
    """标准化 tier 字符串，处理各种可能的格式"""
    if not tier:
        return "none"
    s = str(tier).lower().strip()
    if "expert" in s or "39" in s:
        return "expert_39"
    if "basic" in s or "15" in s:
        return "basic_15"
    return "none"


def apply_paywall(
    decision: dict,
    required_tier: PaywallTier | str,
    unlocked_tier: PaywallTier | str,
) -> dict:
    """未解锁/解锁不足时裁剪付费字段，保证免费区仍有 title/conclusion 等"""
    # 先 normalize 两个 tier，确保比较准确
    required_normalized = normalize_tier(required_tier) if isinstance(required_tier, str) else required_tier
    unlocked_normalized = normalize_tier(unlocked_tier) if isinstance(unlocked_tier, str) else unlocked_tier
    
    def tier_rank(t: PaywallTier) -> int:
        return {"none": 0, "basic_15": 1, "expert_39": 2}.get(t, 0)

    ok = tier_rank(unlocked_normalized) >= tier_rank(required_normalized)
    if ok or required_normalized == "none":
        # ✅ Part C: 即使解锁了，也要确保 expert_pack 只在 expert_39 时保留
        if unlocked_normalized != "expert_39":
            decision = dict(decision)
            decision["expert_pack"] = None
        return decision

    # 裁剪：付费字段清空，但保留免费区
    decision = dict(decision)
    decision["reasons"] = []
    decision["recommended_actions"] = []
    decision["risk_if_ignore"] = []
    decision["expert_pack"] = None
    return decision

