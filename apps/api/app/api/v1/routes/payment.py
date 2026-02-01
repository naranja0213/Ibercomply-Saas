"""
支付相关 API
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import stripe
import os
import logging
from app.database import get_db
from app.services.stripe_service import verify_payment_session
from app.services.decision_templates import normalize_tier
from app.models import PaymentSession, Assessment

# 初始化 Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

router = APIRouter()
logger = logging.getLogger(__name__)


class PaymentVerificationRequest(BaseModel):
    session_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "cs_test_123"
            }
        }
    }


class PaymentVerificationResponse(BaseModel):
    verified: bool
    tier: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "verified": True,
                "tier": "basic_15",
            }
        }
    }


class PaymentStatusResponse(BaseModel):
    paid: bool
    assessment_id: Optional[str] = None
    unlocked_tier: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "paid": True,
                "assessment_id": "assessment_abc123_1700000000",
                "unlocked_tier": "expert_39",
            }
        }
    }


@router.get("/verify", response_model=PaymentVerificationResponse)
async def verify_payment_endpoint(
    session_id: str = Query(..., description="Stripe Checkout Session ID"),
    db: Session = Depends(get_db)
):
    """
    验证支付状态
    根据 session_id 检查支付是否成功
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    payment_session = verify_payment_session(session_id, db)
    
    if payment_session and payment_session.status == "paid":
        return PaymentVerificationResponse(
            verified=True,
            tier=payment_session.tier
        )
    else:
        # 检查是否存在未支付的记录
        payment_session = db.query(PaymentSession).filter(
            PaymentSession.session_id == session_id
        ).first()
        
        if payment_session:
            return PaymentVerificationResponse(
                verified=False,
                tier=payment_session.tier
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")


def normalize_paid_tier(t: Optional[str]) -> Optional[str]:
    """标准化 tier（basic → basic_15，expert → expert_39）"""
    if not t:
        return None
    t = t.strip().lower()
    if t in ("basic", "basic_15", "basic15"):
        return "basic_15"
    if t in ("expert", "expert_39", "expert39"):
        return "expert_39"
    return t


@router.get("/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    session_id: str = Query(..., description="Stripe Checkout Session ID"),
    db: Session = Depends(get_db)
):
    """
    查询支付状态（给 success 页面使用）
    返回支付状态、assessment_id 和 unlocked_tier
    
    ✅ 兜底解锁逻辑：只要 paid=True，就必须把 Assessment 解锁写进去（不要靠 webhook）
    """
    logger.info("[PAYMENT_STATUS] query payment status")
    
    payment_session = verify_payment_session(session_id, db)

    if not payment_session or payment_session.status != "paid":
        logger.info("[PAYMENT_STATUS] payment not found or not paid")
        return PaymentStatusResponse(paid=False, assessment_id=None, unlocked_tier=None)

    # ✅ 关键：必须有 assessment_id（来自 metadata 回写）
    if not payment_session.assessment_id:
        logger.warning("[PAYMENT_STATUS] paid but missing assessment_id in PaymentSession")
        return PaymentStatusResponse(paid=True, assessment_id=None, unlocked_tier=None)

    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == payment_session.assessment_id
    ).first()

    # 如果 assessment 不存在，也要返回 assessment_id 方便排查
    if not assessment:
        logger.warning("[PAYMENT_STATUS] assessment not found for paid session")
        return PaymentStatusResponse(paid=True, assessment_id=payment_session.assessment_id, unlocked_tier=None)

    # ✅ 兜底解锁：paid=true 但 unlocked_tier 还是 none/空，就立刻写入
    # ⚠️ 关键修复：必须从 payment_session.tier 读取，不能默认 basic_15
    desired = normalize_paid_tier(payment_session.tier)
    if not desired:
        # 如果无法标准化，尝试从 payment_session.tier 原始值判断
        raw_tier = (payment_session.tier or "").strip().lower()
        if "expert" in raw_tier or "39" in raw_tier:
            desired = "expert_39"
        else:
            desired = "basic_15"  # 最后兜底
        logger.warning("[PAYMENT_STATUS] tier normalization failed, using fallback")
    
    current = (assessment.unlocked_tier or "none").strip().lower()

    logger.info("[PAYMENT_STATUS] current=%s desired=%s", current, desired)

    # ✅ 关键修复：使用 tier_rank 确保只升级不降级
    def tier_rank(t: str) -> int:
        return {"none": 0, "basic_15": 1, "expert_39": 2}.get(t or "none", 0)
    
    if current in ("none", "") or tier_rank(desired) > tier_rank(current):
        logger.info("[PAYMENT_STATUS] unlocking/upgrading: %s -> %s", current, desired)
        assessment.unlocked_tier = desired
        assessment.unlocked_at = datetime.utcnow()
        if not assessment.stripe_session_id:
            assessment.stripe_session_id = session_id
        db.commit()
        db.refresh(assessment)
        logger.info("[PAYMENT_STATUS] assessment unlocked")

    final_tier = normalize_paid_tier(assessment.unlocked_tier)
    
    logger.info("[PAYMENT_STATUS] returning paid status: unlocked_tier=%s", final_tier)

    return PaymentStatusResponse(
        paid=True,
        assessment_id=assessment.assessment_id,
        unlocked_tier=final_tier
    )
