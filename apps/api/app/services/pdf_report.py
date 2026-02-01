"""
PDF 报告生成器
使用 ReportLab 生成合规评估 PDF 报告
支持中文显示
"""

from io import BytesIO
from datetime import datetime, timezone
from typing import Dict, Any, List
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from .risk.industry_catalog import INDUSTRY_LABELS

logger = logging.getLogger(__name__)

# ✅ 中文字体配置
# 尝试注册中文字体（按优先级尝试多个路径）
CHINESE_FONT_NAME = "ChineseFont"
_font_registered = False

def _register_chinese_font():
    """注册中文字体"""
    global _font_registered
    if _font_registered:
        return CHINESE_FONT_NAME
    
    # 常见中文字体路径（按优先级）
    font_paths = [
        # Linux (常见中文字体) - Debian/Ubuntu 实际路径
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        # Windows (如果在 Windows 上运行)
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    
    # 也可以从环境变量指定字体路径
    custom_font_path = os.getenv("PDF_CHINESE_FONT_PATH")
    if custom_font_path:
        font_paths.insert(0, custom_font_path)
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(CHINESE_FONT_NAME, font_path))
                _font_registered = True
                return CHINESE_FONT_NAME
        except Exception:
            continue
    
    # 如果找不到中文字体，使用默认字体（可能不支持中文，但至少不会报错）
    # 用户需要提供字体文件或安装系统字体
    logger.warning(
        "未找到中文字体，PDF 中文可能显示为方块。请设置 PDF_CHINESE_FONT_PATH 环境变量指定字体路径。"
    )
    _font_registered = True  # 标记为已尝试，避免重复警告
    return "Helvetica"  # 回退到默认字体


# 初始化字体
_register_chinese_font()


# 阶段中文映射
STAGE_LABELS: Dict[str, str] = {
    "PRE_AUTONOMO": "还没注册 Autónomo",
    "AUTONOMO": "已注册 Autónomo",
    "SL": "已注册 SL 公司",
}


def _get_chinese_font_name():
    """获取中文字体名称"""
    return CHINESE_FONT_NAME if _font_registered else "Helvetica"


def generate_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    生成 PDF 报告
    
    Args:
        report_data: 报告数据字典（由 report_builder 生成）
    
    Returns:
        PDF 文件的 bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 构建内容
    story = []
    
    # 1. 封面页
    story.extend(_build_cover_page(report_data))
    story.append(PageBreak())
    
    # 2. 结论摘要 + 判断依据（合并到一页，basic_15+）
    story.extend(_build_summary_section(report_data))
    if report_data.get("unlocked_tier") in ("basic_15", "expert_39"):
        story.append(Spacer(1, 0.3*cm))
        story.extend(_build_reasons_section(report_data, skip_title=True))
    story.append(Spacer(1, 0.3*cm))
    story.extend(_build_dont_do_section(report_data))
    
    # 如果内容太多，才分页
    story.append(PageBreak())
    
    # 3. 行动清单 + 忽视后果（合并到一页，basic_15+）
    if report_data.get("unlocked_tier") in ("basic_15", "expert_39"):
        story.extend(_build_actions_section(report_data))
        story.append(Spacer(1, 0.3*cm))
        story.extend(_build_risks_section(report_data, skip_title=True))
        story.append(PageBreak())
    
    # 4. 决策版内容（expert_39）
    if report_data.get("unlocked_tier") == "expert_39":
        story.extend(_build_expert_section(report_data))
        story.append(PageBreak())
    
    # 5. 免责声明页（所有报告最后都有）
    story.extend(_build_disclaimer_page(report_data))
    
    # 生成 PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _get_styles():
    """获取支持中文的样式表"""
    styles = getSampleStyleSheet()
    font_name = _get_chinese_font_name()
    
    # ✅ 统一设置所有样式的字体名称
    for style_name in styles.byName:
        style = styles[style_name]
        style.fontName = font_name
        style.wordWrap = 'CJK'  # ✅ 中文自动换行
    
    return styles, font_name


def _build_cover_page(report_data: Dict[str, Any]) -> List:
    """构建封面页（专业咨询报告风格）"""
    story = []
    styles, font_name = _get_styles()
    
    # 顶部品牌名称（小字号）
    brand_style = ParagraphStyle(
        'Brand',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=0.5*cm,
        wordWrap='CJK'
    )
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("IberComply", brand_style))
    
    # 主标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=26,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=0.4*cm,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )
    
    # 主标题
    story.append(Paragraph("合规风险暴露评估报告", title_style))
    
    # 副标题（核心说明，一句话）
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=1.5*cm,
        wordWrap='CJK'
    )
    story.append(Paragraph("本报告评估的是当前经营状态下的合规风险暴露程度，而非违法或处罚认定", subtitle_style))
    
    # 评估对象概况模块
    input_data = report_data.get("input", {})
    stage_key = input_data.get('stage', '')
    industry_key = input_data.get('industry', '')
    
    # 获取阶段和行业的中文名称
    stage_label = STAGE_LABELS.get(stage_key, stage_key)
    industry_label = INDUSTRY_LABELS.get(industry_key, industry_key)
    
    # 获取用户输入的评估条件
    monthly_income = input_data.get('monthly_income', 0)
    employee_count = input_data.get('employee_count', 0)
    has_pos = input_data.get('has_pos', False)
    
    # ✅ 生成评估版本号（基于 created_at 或当前 UTC 时间）
    created_at_str = report_data.get("created_at")
    if created_at_str:
        try:
            created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            # 使用 UTC 日期（确保版本号与 created_at 一致）
            assessment_date = created_at_dt.astimezone(timezone.utc) if created_at_dt.tzinfo else created_at_dt.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            assessment_date = datetime.now(timezone.utc)
    else:
        assessment_date = datetime.now(timezone.utc)
    assessment_version = f"v{assessment_date.strftime('%Y.%m.%d')}"
    
    # 评估对象概况模块（居中布局）
    overview_label_style = ParagraphStyle(
        'OverviewLabel',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=0.4*cm,
        wordWrap='CJK'
    )
    
    overview_style = ParagraphStyle(
        'Overview',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=0.18*cm,
        wordWrap='CJK'
    )
    
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("<b>评估对象概况</b>", overview_label_style))
    
    # 评估对象信息（居中排列）
    overview_items = [
        f"阶段：{stage_label}",
        f"行业：{industry_label}",
        f"月收入：€{monthly_income:.0f}",
        f"员工人数：{employee_count} 人",
        f"使用POS机：{'是' if has_pos else '否'}",
        f"评估日期：{assessment_date.strftime('%Y年%m月%d日')}",
        f"评估版本：{assessment_version}"
    ]
    
    for item in overview_items:
        story.append(Paragraph(item, overview_style))
    
    # ✅ 适用性说明（封面页底部）
    story.append(Spacer(1, 0.3*cm))
    applicability_style = ParagraphStyle(
        'ApplicabilityNote',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER,
        spaceAfter=0.2*cm,
    )
    applicability_text = f"本报告基于 {assessment_date.strftime('%Y年%m月%d日')} 的输入生成。若经营情况发生变化，建议重新评估。"
    story.append(Paragraph(applicability_text, applicability_style))
    
    # 页脚参考说明（简短，不超过一行）
    story.append(Spacer(1, 2.5*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        wordWrap='CJK'
    )
    story.append(Paragraph("基于当前输入信息的合规风险评估，仅供参考", footer_style))
    
    return story


def _build_summary_section(report_data: Dict[str, Any]) -> List:
    """构建结论摘要部分"""
    story = []
    styles, font_name = _get_styles()
    
    # 标题
    story.append(Paragraph("结论摘要", styles['Heading1']))
    story.append(Spacer(1, 0.3*cm))
    
    # 风险阶段（A/B/C/D）与分数（带防误读说明）
    risk_score = report_data.get("risk_score", 0)
    risk_band = report_data.get("risk_band", {})
    risk_explain = report_data.get("risk_explain", {}) or {}
    risk_stage = risk_explain.get("risk_stage")
    risk_stage_label = risk_explain.get("label")

    if risk_stage:
        stage_text = f"<b>风险阶段：</b>{risk_stage}"
        if risk_stage_label:
            stage_text += f"（{risk_stage_label}）"
        story.append(Paragraph(stage_text, styles['Normal']))
        story.append(Spacer(1, 0.15*cm))

    score_text = f"<b>风险暴露分数：</b>{risk_score}"
    if risk_band:
        score_text += f"（{risk_band.get('label', '')} {risk_band.get('range', '')}）"
    story.append(Paragraph(score_text, styles['Normal']))
    
    # 防误读说明（优化为更清晰的表达）
    score_note_style = ParagraphStyle(
        'ScoreNote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_LEFT,
        leftIndent=0.5*cm,
        wordWrap='CJK'
    )
    score_note = "注：该分数反映的是当前经营状态的「合规暴露度」，不代表违法程度或处罚结论。"
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(score_note, score_note_style))
    story.append(Spacer(1, 0.2*cm))
    
    # 决策标题
    decision = report_data.get("decision_summary", {})
    if decision.get("title"):
        story.append(Paragraph(f"<b>{decision.get('title')}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
    
    # 结论
    if decision.get("conclusion"):
        story.append(Paragraph(decision.get("conclusion"), styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # 置信度原因（强化咨询语气）
    if decision.get("confidence_reason"):
        story.append(Paragraph("<b>为什么我们对这个判断有信心？</b>", styles['Heading3']))
        story.append(Spacer(1, 0.15*cm))
        confidence_text = decision.get("confidence_reason")
        # 添加咨询语气补充（经验型表达）
        confidence_enhanced = f"{confidence_text} 这些问题在实际检查中非常常见，也最容易通过补齐材料与流程得到明显改善。"
        story.append(Paragraph(confidence_enhanced, styles['Normal']))
        
        # ✅ 补充"人话解释"（增强信任）
        enhanced_note_style = ParagraphStyle(
            'EnhancedNote',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            textColor=colors.grey,
            wordWrap='CJK',
            fontStyle='italic'
        )
        story.append(Spacer(1, 0.15*cm))
        story.append(Paragraph("在实际检查中，类似情况下通常需要更多材料，才能确认是否存在被低估的风险点。", enhanced_note_style))
        story.append(Spacer(1, 0.3*cm))
    
    # Top 3 风险点（添加动态放大条件）
    top_risks = report_data.get("top_risks", [])
    input_data = report_data.get("input", {})
    monthly_income = input_data.get('monthly_income', 0)
    employee_count = input_data.get('employee_count', 0)
    
    if top_risks:
        # 在所有风险点之后添加动态放大条件说明（统一提示）
        warning_note_style = ParagraphStyle(
            'WarningNote',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            textColor=colors.grey,
            leftIndent=0.5*cm,
            wordWrap='CJK',
            fontStyle='italic'
        )
        
        story.append(Paragraph("<b>最需要注意的 3 个风险点：</b>", styles['Heading3']))
        story.append(Spacer(1, 0.15*cm))
        for i, risk in enumerate(top_risks[:3], 1):
            risk_text = f"{i}. {risk.get('title', 'N/A')}"
            if risk.get('detail'):
                risk_text += f"：{risk.get('detail')}"
            story.append(Paragraph(risk_text, styles['Normal']))
            if risk.get("explain_difficulty") or risk.get("trigger_sources"):
                extra = []
                if risk.get("explain_difficulty"):
                    extra.append(f"解释难度：{risk.get('explain_difficulty')}")
                if risk.get("trigger_sources"):
                    sources = " / ".join(risk.get("trigger_sources")[:3])
                    extra.append(f"常见触发来源：{sources}")
                story.append(Paragraph("；".join(extra), warning_note_style))
            story.append(Spacer(1, 0.15*cm))
        
        # 动态风险提示（通用提醒，不依赖当前状态）
        warning_note = "提示：如果接下来 30 天内收入继续上升、新增员工或新增 POS / 平台收款，该风险点可能会被明显放大，建议提前准备。"
        story.append(Paragraph(warning_note, warning_note_style))
    
    return story


def _build_dont_do_section(report_data: Dict[str, Any]) -> List:
    """构建不该做的事模块（合规护身符）"""
    story = []
    styles, font_name = _get_styles()

    dont_do = report_data.get("dont_do", []) or []
    if not dont_do:
        return story

    story.append(Paragraph("你现在最不该做的事", styles['Heading2']))
    story.append(Spacer(1, 0.15*cm))

    note_style = ParagraphStyle(
        'DontDoNote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        wordWrap='CJK',
        fontStyle='italic'
    )
    story.append(Paragraph("只提示“不要做什么”，不提供任何规避或操作细节。", note_style))
    story.append(Spacer(1, 0.15*cm))

    for item in dont_do[:4]:
        story.append(Paragraph(f"• {item}", styles['Normal']))
        story.append(Spacer(1, 0.12*cm))

    return story


def _build_reasons_section(report_data: Dict[str, Any], skip_title: bool = False) -> List:
    """构建判断依据部分"""
    story = []
    styles, font_name = _get_styles()
    
    if not skip_title:
        story.append(Paragraph("判断依据", styles['Heading1']))
        story.append(Spacer(1, 0.3*cm))
    else:
        story.append(Paragraph("判断依据", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
    
    reasons = report_data.get("reasons", [])
    if reasons:
        story.append(Paragraph("<b>为什么会得出这个结论：</b>", styles['Heading3']))
        story.append(Spacer(1, 0.15*cm))
        for reason in reasons:
            story.append(Paragraph(f"• {reason}", styles['Normal']))
            story.append(Spacer(1, 0.15*cm))
    
    return story


def _build_actions_section(report_data: Dict[str, Any]) -> List:
    """构建行动清单部分（咨询师风格：3个时间层级）"""
    story = []
    styles, font_name = _get_styles()
    
    story.append(Paragraph("行动清单", styles['Heading1']))
    story.append(Spacer(1, 0.2*cm))
    
    actions = report_data.get("recommended_actions", [])
    if actions:
        # 行动目标说明（放在标题下方）
        purpose_style = ParagraphStyle(
            'Purpose',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            wordWrap='CJK',
            spaceAfter=0.4*cm
        )
        story.append(Paragraph("这些动作的目标是：让你在被询问时，5 分钟内能拿出解释材料。", purpose_style))
        
        # 将行动清单按时间层级分类
        urgent_actions = []  # ① 现在就该做（1小时内）
        short_term_actions = []  # ② 接下来几天内完成
        long_term_actions = []  # ③ 长期保持
        
        # 根据关键词分类（简单启发式分类）
        urgent_keywords = ["优先", "立即", "从今天开始", "快速", "立刻", "马上", "先做", "首先"]
        long_term_keywords = ["保持", "定期", "每月", "持续", "建立习惯", "固定", "确保", "对比"]
        
        for action in actions:
            action_lower = action.lower()
            if any(keyword in action_lower for keyword in urgent_keywords):
                urgent_actions.append(action)
            elif any(keyword in action_lower for keyword in long_term_keywords):
                long_term_actions.append(action)
            else:
                short_term_actions.append(action)
        
        # Fallback逻辑：如果分类后某个类别为空，进行智能分配
        total = len(actions)
        if not urgent_actions and not long_term_actions:
            # 如果完全没有匹配关键词，按照位置平均分配
            if total <= 3:
                urgent_actions = actions[:1] if total > 0 else []
                short_term_actions = actions[1:] if total > 1 else []
            elif total <= 6:
                urgent_actions = actions[:2]
                short_term_actions = actions[2:4] if total > 4 else actions[2:]
                long_term_actions = actions[4:] if total > 4 else []
            else:
                urgent_actions = actions[:2]
                mid_point = total // 2
                short_term_actions = actions[2:mid_point+1]
                long_term_actions = actions[mid_point+1:]
        else:
            # 如果部分匹配了关键词，确保三个类别都有内容（如果actions足够多）
            if total >= 3:
                if not urgent_actions and short_term_actions:
                    urgent_actions = short_term_actions[:1]
                    short_term_actions = short_term_actions[1:]
                if not long_term_actions and short_term_actions and len(short_term_actions) > 1:
                    long_term_actions = short_term_actions[-1:]
                    short_term_actions = short_term_actions[:-1]
        
        # 样式定义
        tier_title_style = ParagraphStyle(
            'TierTitle',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=0.2*cm,
            wordWrap='CJK'
        )
        
        tier_subtitle_style = ParagraphStyle(
            'TierSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=0.15*cm,
            wordWrap='CJK',
            fontStyle='italic'
        )
        
        action_item_style = ParagraphStyle(
            'ActionItem',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=0.3*cm,
            spaceAfter=0.12*cm,
            wordWrap='CJK'
        )
        
        # ① 现在就该做（1小时内）
        if urgent_actions:
            story.append(Paragraph("① 现在就该做（1 小时内）", tier_title_style))
            story.append(Paragraph("目标：立刻降低暴露", tier_subtitle_style))
            for action in urgent_actions:
                story.append(Paragraph(f"• {action}", action_item_style))
            story.append(Spacer(1, 0.3*cm))
        
        # ② 接下来几天内完成
        if short_term_actions:
            story.append(Paragraph("② 接下来几天内完成", tier_title_style))
            story.append(Paragraph("目标：补齐关键材料，避免被要求补件时慌乱", tier_subtitle_style))
            for action in short_term_actions:
                story.append(Paragraph(f"• {action}", action_item_style))
            story.append(Spacer(1, 0.3*cm))
        
        # ③ 长期保持
        if long_term_actions:
            story.append(Paragraph("③ 长期保持", tier_title_style))
            story.append(Paragraph("目标：把风险变成可控状态", tier_subtitle_style))
            for action in long_term_actions:
                story.append(Paragraph(f"• {action}", action_item_style))
            story.append(Spacer(1, 0.3*cm))
        
        # 正向闭环提示
        story.append(Spacer(1, 0.2*cm))
        closing_note_style = ParagraphStyle(
            'ClosingNote',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            wordWrap='CJK'
        )
        story.append(Paragraph("完成以上步骤后，建议进行一次复评，以确认整体风险是否已明显下降。", closing_note_style))
    
    return story


def _build_risks_section(report_data: Dict[str, Any], skip_title: bool = False) -> List:
    """构建忽视后果/执法路径部分（弱化视觉权重，中性表达）"""
    story = []
    styles, font_name = _get_styles()
    
    # 弱化标题样式（较小字号，中性语气）
    weak_title_style = ParagraphStyle(
        'WeakTitle',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=0.2*cm,
        wordWrap='CJK'
    )
    
    weak_subtitle_style = ParagraphStyle(
        'WeakSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=0.15*cm,
        wordWrap='CJK'
    )
    
    weak_content_style = ParagraphStyle(
        'WeakContent',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        spaceAfter=0.12*cm,
        wordWrap='CJK'
    )
    
    if not skip_title:
        story.append(Paragraph("如果长期忽视，可能出现的结果（供参考）", weak_title_style))
        story.append(Spacer(1, 0.2*cm))
    else:
        story.append(Paragraph("如果长期忽视，可能出现的结果（供参考）", weak_title_style))
        story.append(Spacer(1, 0.15*cm))
    
    # 忽视后果（弱化表达）
    risk_if_ignore = report_data.get("risk_if_ignore", [])
    if risk_if_ignore:
        for risk in risk_if_ignore:
            story.append(Paragraph(f"• {risk}", weak_content_style))
        story.append(Spacer(1, 0.2*cm))
    
    # 执法路径（弱化表达，中性标题）
    enforcement_path = report_data.get("enforcement_path", [])
    if enforcement_path:
        story.append(Paragraph("税务局常见处理流程（了解为什么材料闭环重要）", weak_subtitle_style))
        story.append(Spacer(1, 0.1*cm))
        for step in enforcement_path:
            step_num = step.get("step", "")
            title = step.get("title", "")
            desc = step.get("description", "")
            step_text = f"步骤 {step_num}：{title} — {desc}"
            story.append(Paragraph(step_text, weak_content_style))
    
    return story


def _build_expert_section(report_data: Dict[str, Any]) -> List:
    """构建决策版部分"""
    story = []
    styles, font_name = _get_styles()
    
    story.append(Paragraph("决策版详细分析", styles['Heading1']))
    story.append(Spacer(1, 0.3*cm))
    
    # 分数构成
    score_breakdown = report_data.get("score_breakdown")
    if score_breakdown:
        story.append(Paragraph("<b>① 风险分数构成：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
        
        # 构建表格
        table_data = [["项目", "分数", "说明"]]
        if score_breakdown.get("industry_base"):
            base = score_breakdown["industry_base"]
            table_data.append(["行业基础", str(base.get("score", 0)), base.get("reason", "")])
        if score_breakdown.get("income"):
            income = score_breakdown["income"]
            table_data.append(["收入", str(income.get("score", 0)), income.get("reason", "")])
        if score_breakdown.get("employee"):
            emp = score_breakdown["employee"]
            table_data.append(["员工", str(emp.get("score", 0)), emp.get("reason", "")])
        
        # ✅ 使用 Paragraph 包装表格内容，支持中文和自动换行
        def _make_table_cell(text):
            return Paragraph(str(text), ParagraphStyle(
                'TableCell',
                fontName=font_name,  # ✅ 表格也使用中文字体
                fontSize=9,
                wordWrap='CJK'  # ✅ 中文自动换行
            ))
        
        # 转换表格数据为 Paragraph
        table_data_para = []
        for row in table_data:
            table_data_para.append([_make_table_cell(cell) for cell in row])
        
        table = Table(table_data_para, colWidths=[4*cm, 2*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # ✅ 顶部对齐，支持多行
            ('FONTNAME', (0, 0), (-1, -1), font_name),  # ✅ 表格也使用中文字体
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # 表头字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 9),  # 内容字体大小
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*cm))
    
    # 30天路线图
    roadmap = report_data.get("roadmap_30d", [])
    if roadmap:
        story.append(Paragraph("<b>② 30 天合规路线图：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))

    # 决策提示（是否需要专业人士）
    decision_guidance = report_data.get("decision_guidance") or {}
    if decision_guidance:
        story.append(Paragraph("<b>③ 是否需要专业人士：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.15*cm))
        need = decision_guidance.get("need_professional", "")
        roles = decision_guidance.get("suggested_roles", [])
        reason = decision_guidance.get("reason", "")
        guidance_text = f"建议程度：{need}"
        if roles:
            guidance_text += f"；建议角色：{' / '.join(roles)}"
        if reason:
            guidance_text += f"。原因：{reason}"
        story.append(Paragraph(guidance_text, styles['Normal']))
        story.append(Spacer(1, 0.2*cm))

    # 30/90 天节奏
    cadence = report_data.get("cadence_90d", [])
    if cadence:
        story.append(Paragraph("<b>④ 30/90 天节奏：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.15*cm))
        for item in cadence:
            story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 0.12*cm))
        for item in roadmap:
            week = item.get("week", "")
            tasks = item.get("tasks", [])
            if isinstance(tasks, list):
                tasks_text = "、".join(tasks)
            else:
                tasks_text = str(tasks)
            roadmap_text = f"<b>{week}：</b>{tasks_text}"
            story.append(Paragraph(roadmap_text, styles['Normal']))
            story.append(Spacer(1, 0.15*cm))
        story.append(Spacer(1, 0.2*cm))
    
    # 材料清单
    documents = report_data.get("documents_pack", [])
    if documents:
        story.append(Paragraph("<b>⑤ 所需材料清单：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
        for doc in documents:
            story.append(Paragraph(f"• {doc}", styles['Normal']))
            story.append(Spacer(1, 0.12*cm))
        story.append(Spacer(1, 0.2*cm))
    
    # 自检表
    checklist = report_data.get("self_audit_checklist", [])
    if checklist:
        story.append(Paragraph("<b>⑥ 自检清单：</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
        for item in checklist:
            story.append(Paragraph(f"□ {item}", styles['Normal']))
            story.append(Spacer(1, 0.12*cm))
    
    return story


def _build_disclaimer_page(report_data: Dict[str, Any]) -> List:
    """构建免责声明页（放在报告最后）"""
    story = []
    styles, font_name = _get_styles()
    
    # ✅ 生成评估版本号（基于 created_at 或当前 UTC 时间，与封面页保持一致）
    created_at_str = report_data.get("created_at")
    if created_at_str:
        try:
            created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            assessment_date = created_at_dt.astimezone(timezone.utc) if created_at_dt.tzinfo else created_at_dt.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            assessment_date = datetime.now(timezone.utc)
    else:
        assessment_date = datetime.now(timezone.utc)
    assessment_version = f"v{assessment_date.strftime('%Y.%m.%d')}"
    
    # 免责声明标题
    story.append(Paragraph("免责声明与使用说明", styles['Heading1']))
    story.append(Spacer(1, 0.4*cm))
    
    # 免责声明正文
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=0.3*cm,
        wordWrap='CJK'
    )
    
    disclaimer_text = (
        "本报告为基于当前输入信息的合规风险暴露评估，仅供参考，不构成法律、税务或财务建议。"
        "本平台不提供任何关于既往未申报收入/现金的处理建议，不提供规避监管、逃税或洗钱的方案或操作指导。"
        "如需正式结论或个案处理，请咨询具备执业资格的专业人士。"
        "数字化服务一经交付不支持退款。"
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 复评说明
    story.append(Paragraph("<b>复评建议</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*cm))
    reassessment_text = f"本报告基于评估当时的经营信息与输入数据（评估版本：{assessment_version}）。如果你的收入、员工数量或经营方式发生变化，建议进行一次新的复评。"
    story.append(Paragraph(reassessment_text, disclaimer_style))
    
    return story
