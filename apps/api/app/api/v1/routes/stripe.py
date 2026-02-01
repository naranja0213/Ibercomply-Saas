from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import Literal, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import stripe
import os
import logging
import sentry_sdk
from app.services.stripe_service import create_checkout_session
from app.database import get_db
from app.models import PaymentSession, Assessment, WebhookEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化 Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutSessionRequest(BaseModel):
    tier: Literal["basic_15", "expert_39"]  # A. tier 统一：只能 "basic_15" | "expert_39"
    assessment_id: str  # B. 强制必填
    user_id: str  # B. 强制必填

    model_config = {
        "json_schema_extra": {
            "example": {
                "tier": "expert_39",
                "assessment_id": "assessment_abc123_1700000000",
                "user_id": "user_001",
            }
        }
    }


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_123",
                "session_id": "cs_test_123",
            }
        }
    }


def _process_checkout_completed(event: dict, db: Session, allow_duplicate: bool = False) -> dict:
    event_id = event.get("id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")

    session = event.get("data", {}).get("object", {})
    session_id = session.get("id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session id")

    existing_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing_event:
        if existing_event.status in ("processed", "processing"):
            if allow_duplicate:
                return {"status": "already_processed"}
            return {"status": "duplicate"}
        existing_event.status = "processing"
    else:
        existing_event = WebhookEvent(
            event_id=event_id,
            event_type=event.get("type", ""),
            session_id=session_id,
            status="processing"
        )
        db.add(existing_event)
    db.commit()

    metadata = session.get("metadata", {})
    logger.info("[WEBHOOK] checkout.session.completed received: session_id=%s", session_id)

    assessment_id = metadata.get("assessment_id")
    tier_raw = metadata.get("tier", "basic_15")
    from app.services.decision_templates import normalize_tier

    def tier_rank(t: str) -> int:
        normalized = normalize_tier(t)
        return {"none": 0, "basic_15": 1, "expert_39": 2}.get(normalized, 0)

    tier = normalize_tier(tier_raw)
    user_id = metadata.get("user_id", "")

    if not assessment_id or not user_id:
        raise HTTPException(status_code=400, detail="Missing assessment_id or user_id in metadata")

    if session.get("payment_status") != "paid":
        raise HTTPException(status_code=400, detail="Payment not completed")

    expected_amounts = {
        "basic_15": 1500,
        "expert_39": 3900,
    }
    amount_total = session.get("amount_total")
    currency = (session.get("currency") or "").lower()
    expected_amount = expected_amounts.get(tier)
    if amount_total is None or expected_amount is None:
        raise HTTPException(status_code=400, detail="Invalid payment amount or tier")
    if currency != "eur":
        raise HTTPException(status_code=400, detail=f"Invalid currency: {currency}")
    if int(amount_total) != int(expected_amount):
        raise HTTPException(status_code=400, detail=f"Amount mismatch: {amount_total} != {expected_amount}")

    logger.info("[WEBHOOK] tier normalized: %s -> %s", tier_raw, tier)

    try:
        payment_session = db.query(PaymentSession).filter(
            PaymentSession.session_id == session_id
        ).first()

        if payment_session:
            payment_session.status = "paid"
            payment_session.paid_at = datetime.utcnow()
        else:
            payment_session = PaymentSession(
                session_id=session_id,
                assessment_id=assessment_id,
                tier=tier,
                status="paid",
                amount=session.get("amount_total", 0),
                currency=session.get("currency", "eur"),
                paid_at=datetime.utcnow()
            )
            db.add(payment_session)

        if assessment_id:
            logger.info("[WEBHOOK] updating assessment unlock status")

            assessment = db.query(Assessment).filter(
                Assessment.assessment_id == assessment_id
            ).first()

            if assessment:
                old_tier = normalize_tier(assessment.unlocked_tier or "none")
                new_tier = tier

                if tier_rank(new_tier) > tier_rank(old_tier):
                    assessment.unlocked_tier = new_tier
                    assessment.unlocked_at = datetime.utcnow()
                    assessment.stripe_session_id = session_id

                    if user_id and not assessment.user_id:
                        assessment.user_id = user_id

                    db.commit()
                    db.refresh(assessment)

                    logger.info(
                        "[WEBHOOK] assessment upgraded: old=%s new=%s session_id=%s",
                        old_tier,
                        new_tier,
                        session_id,
                    )
                else:
                    logger.warning(
                        "[WEBHOOK] tier not upgraded: old=%s new=%s",
                        old_tier,
                        new_tier,
                    )

                verify_assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
                if verify_assessment:
                    logger.info(
                        "[WEBHOOK] verification confirmed: unlocked_tier=%s",
                        verify_assessment.unlocked_tier,
                    )
                else:
                    logger.warning("[WEBHOOK] verification failed: assessment not found")
            else:
                logger.info("[WEBHOOK] assessment not found, creating new record")
                assessment = Assessment(
                    assessment_id=assessment_id,
                    user_id=user_id,
                    unlocked_tier=tier,
                    unlocked_at=datetime.utcnow(),
                    stripe_session_id=session_id
                )
                db.add(assessment)
                db.commit()
                db.refresh(assessment)

                logger.info(
                    "[WEBHOOK] assessment created: unlocked_tier=%s session_id=%s",
                    assessment.unlocked_tier,
                    session_id,
                )

                verify_assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
                if verify_assessment:
                    logger.info(
                        "[WEBHOOK] verification confirmed: unlocked_tier=%s",
                        verify_assessment.unlocked_tier,
                    )
                else:
                    logger.warning("[WEBHOOK] verification failed: assessment not found")
        else:
            logger.warning("[WEBHOOK] missing assessment_id in metadata, skip update")

        existing_event.status = "processed"
        existing_event.processed_at = datetime.utcnow()
        existing_event.error = None
        db.commit()
        return {"status": "success"}
    except HTTPException as e:
        existing_event.status = "failed"
        existing_event.error = str(e.detail)
        db.commit()
        sentry_sdk.capture_message(f"Stripe webhook failed: {e.detail}", level="error")
        raise
    except Exception as e:
        existing_event.status = "failed"
        existing_event.error = str(e)
        db.commit()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))


def _process_refund(event: dict, db: Session, allow_duplicate: bool = False) -> dict:
    event_id = event.get("id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")

    charge = event.get("data", {}).get("object", {})
    payment_intent = charge.get("payment_intent")
    if not payment_intent:
        return {"status": "ignored", "reason": "missing_payment_intent"}

    existing_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing_event:
        if existing_event.status in ("processed", "processing"):
            if allow_duplicate:
                return {"status": "already_processed"}
            return {"status": "duplicate"}
        existing_event.status = "processing"
    else:
        existing_event = WebhookEvent(
            event_id=event_id,
            event_type=event.get("type", ""),
            session_id=None,
            status="processing"
        )
        db.add(existing_event)
    db.commit()

    try:
        sessions = stripe.checkout.Session.list(payment_intent=payment_intent, limit=1)
        session_id = sessions.data[0].id if sessions.data else None
        if not session_id:
            existing_event.status = "failed"
            existing_event.error = "No checkout session found for payment_intent"
            db.commit()
            return {"status": "failed", "reason": "session_not_found"}

        payment_session = db.query(PaymentSession).filter(
            PaymentSession.session_id == session_id
        ).first()
        if payment_session:
            payment_session.status = "refunded"

        assessment = db.query(Assessment).filter(
            Assessment.stripe_session_id == session_id
        ).first()
        if assessment:
            assessment.unlocked_tier = "none"
            assessment.unlocked_at = None

        existing_event.status = "processed"
        existing_event.processed_at = datetime.utcnow()
        existing_event.error = None
        db.commit()
        return {"status": "success"}
    except Exception as e:
        existing_event.status = "failed"
        existing_event.error = str(e)
        db.commit()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session_endpoint(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db)
):
    """
    创建 Stripe Checkout Session
    返回支付链接，并保存 session 信息到数据库
    """
    # B. 强制必填已在 stripe_service.create_checkout_session 中检查
    # 这里不再重复检查，直接调用
    
    try:
        # 确保 assessment 记录存在（如果不存在则创建）
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == request.assessment_id
        ).first()
        
        if not assessment:
            assessment = Assessment(
                assessment_id=request.assessment_id,
                user_id=request.user_id,
                unlocked_tier="none"
            )
            db.add(assessment)
            db.commit()
        
        # ✅ 尝试获取 decision_code（如果 assessment 有相关数据）
        # 注意：Assessment 模型可能不直接存储 decision_code，这里先留空
        # 未来可以通过扩展 Assessment 模型或从其他来源获取
        decision_code = ""  # 暂时留空，未来可以扩展
        
        # A. tier 统一：直接传递 tier（已经是 "basic_15" 或 "expert_39"）
        result = create_checkout_session(
            tier=request.tier,
            assessment_id=request.assessment_id,
            user_id=request.user_id,
            db=db,
            decision_code=decision_code  # ✅ 传递 decision_code
        )
        return CheckoutSessionResponse(
            checkout_url=result["checkout_url"],
            session_id=result["session_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe Webhook 端点
    处理支付成功事件
    注意：在生产环境中需要验证 webhook 签名
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET is not set")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        # 验证 webhook 签名
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        return _process_checkout_completed(event, db, allow_duplicate=False)
    if event_type in ("charge.refunded", "charge.refund.updated"):
        return _process_refund(event, db, allow_duplicate=False)

    return {"status": "ignored", "event_type": event_type}


@router.post("/webhook/retry/{event_id}")
async def retry_webhook_event(
    event_id: str,
    x_admin_token: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    手动重试 Stripe Webhook（需配置 WEBHOOK_RETRY_TOKEN）
    """
    admin_token = os.getenv("WEBHOOK_RETRY_TOKEN")
    if not admin_token or x_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        event = stripe.Event.retrieve(event_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve event: {e}")

    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        return _process_checkout_completed(event, db, allow_duplicate=True)
    if event_type in ("charge.refunded", "charge.refund.updated"):
        return _process_refund(event, db, allow_duplicate=True)

    return {"status": "ignored", "event_type": event_type}


@router.post("/webhook/retry/{event_id}")
async def retry_webhook_event(
    event_id: str,
    x_admin_token: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    手动重试 Stripe Webhook（需配置 WEBHOOK_RETRY_TOKEN）
    """
    admin_token = os.getenv("WEBHOOK_RETRY_TOKEN")
    if not admin_token or x_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        event = stripe.Event.retrieve(event_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve event: {e}")

    if event.get("type") != "checkout.session.completed":
        return {"status": "ignored", "event_type": event.get("type")}

    return _process_checkout_completed(event, db, allow_duplicate=True)

