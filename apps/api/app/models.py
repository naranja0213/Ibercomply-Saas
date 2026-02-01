"""
数据库模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from .database import Base
import uuid
import json


class Assessment(Base):
    """
    评估结果表
    存储评估结果的解锁状态和完整评估数据
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, index=True, nullable=False)  # 评估结果唯一标识
    user_id = Column(String, index=True, nullable=True)  # 用户 ID（可选，localStorage 生成）
    unlocked_tier = Column(String, default="none")  # "none", "basic_15", "expert_39"
    unlocked_at = Column(DateTime, nullable=True)  # 解锁时间
    stripe_session_id = Column(String, nullable=True, index=True)  # 最后一次支付的 session_id（防重复）
    
    # ✅ 新增：保存评估结果（JSON 格式）
    result_data = Column(JSON, nullable=True)  # 保存 risk_score, risk_level, findings, meta
    decision_summary_data = Column(JSON, nullable=True)  # 保存 decision_summary（完整对象）
    input_data = Column(JSON, nullable=True)  # 保存原始请求数据（用于重新生成）
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Assessment(assessment_id={self.assessment_id}, unlocked_tier={self.unlocked_tier})>"


class PaymentSession(Base):
    """
    支付会话表
    存储 Stripe Checkout Session 信息和支付状态
    """
    __tablename__ = "payment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)  # Stripe session_id
    assessment_id = Column(String, index=True, nullable=True)  # 评估结果唯一标识（用于关联）
    tier = Column(String, nullable=False)  # "basic" 或 "expert"
    status = Column(String, nullable=False, default="pending")  # "pending", "paid", "failed"
    amount = Column(Integer, nullable=True)  # 金额（分）
    currency = Column(String, default="eur")
    paid_at = Column(DateTime, nullable=True)  # 支付完成时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PaymentSession(session_id={self.session_id}, tier={self.tier}, status={self.status})>"


class WebhookEvent(Base):
    """
    Stripe Webhook 事件表（用于去重）
    """
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    session_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="processing")  # processing/processed/failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<WebhookEvent(event_id={self.event_id}, status={self.status})>"

