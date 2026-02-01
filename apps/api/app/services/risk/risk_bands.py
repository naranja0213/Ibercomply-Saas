"""
风险分数区间定义
用于将风险分数转换为可理解的"状态标签"
"""

from typing import Dict, Any, Optional


class RiskBand:
    """风险区间"""
    def __init__(self, min_score: int, max_score: int, label: str, explanation: str):
        self.min = min_score
        self.max = max_score
        self.label = label
        self.explanation = explanation
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "min": self.min,
            "max": self.max,
            "label": self.label,
            "range": f"{self.min}–{self.max}" if self.max < 100 else f"{self.min}+",
            "explanation": self.explanation
        }


# 风险区间定义
RISK_BANDS = [
    RiskBand(0, 24, "安全区", "当前经营特征不明显，短期内被关注概率较低"),
    RiskBand(25, 39, "观察区", "已出现部分经营信号，建议关注变化趋势"),
    RiskBand(40, 59, "风险累积区", "多项信号叠加，进入税务关注常见范围"),
    RiskBand(60, 69, "高风险区", "已明显符合持续经营特征，存在被追溯风险"),
    RiskBand(70, 100, "极高风险区", "触发多重高危信号，执法介入概率较高"),
]


def get_risk_band(score: int) -> Dict[str, Any]:
    """
    根据风险分数获取对应的风险区间
    
    Args:
        score: 风险分数 (0-100)
    
    Returns:
        风险区间字典，包含 label, range, explanation
    """
    for band in RISK_BANDS:
        if band.min <= score <= band.max:
            return band.to_dict()
    
    # 兜底：返回最高风险区间
    return RISK_BANDS[-1].to_dict()

