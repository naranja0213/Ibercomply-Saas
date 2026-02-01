import os
import stripe
import logging
from typing import Optional, Literal
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import PaymentSession
from fastapi import HTTPException

# 初始化 Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
logger = logging.getLogger(__name__)

# Tier 类型定义
TierType = Literal["basic_15", "expert_39"]


def normalize_tier(t: str) -> str:
    """✅ B1: 标准化 tier（basic → basic_15，expert → expert_39）"""
    x = (t or "").strip().lower().replace("-", "_")
    if x in ["basic", "basic15", "basic_15"]:
        return "basic_15"
    if x in ["expert", "expert39", "expert_39", "pro"]:
        return "expert_39"
    return "basic_15"  # 兜底


def create_checkout_session(
    tier: str,  # 接受字符串，内部 normalize
    assessment_id: str,  # 评估结果唯一标识（必需）
    user_id: str,  # 用户 ID（必需）
    price_id: Optional[str] = None,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    db: Optional[Session] = None,
    decision_code: Optional[str] = None  # ✅ 新增：决策代码（用于 metadata）
) -> dict:
    """
    创建 Stripe Checkout Session 并保存到数据库
    """
    # ✅ B1: 先 normalize tier
    tier = normalize_tier(tier)
    logger.info("[CHECKOUT] tier normalized: %s", tier)
    
    # B. 强制必填：assessment_id 和 user_id 必须提供
    if not assessment_id:
        raise HTTPException(status_code=400, detail="assessment_id is required")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # ✅ B1: tier 统一：金额映射（使用 normalized tier）
    if tier == "basic_15":
        amount = 1500
        if not price_id:
            # 兼容两种命名：先尝试 STRIPE_PRICE_BASIC_15，再尝试 STRIPE_PRICE_BASIC
            price_id = os.getenv("STRIPE_PRICE_BASIC_15") or os.getenv("STRIPE_PRICE_BASIC", "")
    elif tier == "expert_39":
        amount = 3900
        if not price_id:
            # 兼容两种命名：先尝试 STRIPE_PRICE_EXPERT_39，再尝试 STRIPE_PRICE_EXPERT
            price_id = os.getenv("STRIPE_PRICE_EXPERT_39") or os.getenv("STRIPE_PRICE_EXPERT", "")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}. Must be 'basic_15' or 'expert_39'")
    
    # C. URL 带回 assessment_id
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
    if not success_url:
        success_url = f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&assessment_id={assessment_id}"
    
    if not cancel_url:
        cancel_url = f"{frontend_url}/assessment/result?assessment_id={assessment_id}"

    try:
        # 准备 line_items
        line_items = []
        
        if price_id:
            # 使用现有的 price_id
            line_items.append({
                "price": price_id,
                "quantity": 1,
            })
        else:
            # 如果没有 price_id，直接使用金额创建一次性价格
            # ✅ 更新产品名称和描述
            if tier == "basic_15":
                product_name = "HispanoComply · 合规风险完整分析"
                product_description = "解锁本次评估的完整判断依据、行动建议，以及在当前情况下税务部门的常见执法路径。"
            else:  # expert_39
                product_name = "HispanoComply · 决策版合规行动方案"
                product_description = "包含完整阶段解释、材料清单/自检表与 30/90 天节奏，并提供是否需要专业人士的决策提示。"
            
            line_items.append({
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": product_name,
                        "description": product_description,
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            })
        
        # D. metadata 不允许空：必须包含 assessment_id/user_id/tier，且非空
        if not assessment_id or not user_id or not tier:
            raise HTTPException(status_code=400, detail="assessment_id, user_id, and tier are required in metadata")
        
        # ✅ 准备 metadata（添加 includes 和 decision_code）
        metadata = {
            "product": "hispanocomply",
            "tier": tier,
            "assessment_id": assessment_id,
            "user_id": user_id,
            # ✅ 新增：includes 字段（expert_39 包含 basic_15）
            "includes": "basic_15" if tier == "expert_39" else "",
            # ✅ 新增：decision_code（从调用参数传入）
            "decision_code": decision_code or "",
        }
        
        logger.info("[CHECKOUT] creating checkout session")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        logger.info("[CHECKOUT] checkout session created: session_id=%s", session.id)
        
        # 保存到数据库（如果提供了 db session）
        if db:
            payment_session = PaymentSession(
                session_id=session.id,
                assessment_id=assessment_id,
                tier=tier,
                status="pending",
                amount=amount,
                currency="eur"
            )
            db.add(payment_session)
            db.commit()
            db.refresh(payment_session)
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
    except Exception as e:
        raise Exception(f"Failed to create checkout session: {str(e)}")


def verify_payment_session(session_id: str, db: Session) -> Optional[PaymentSession]:
    """
    验证支付会话状态
    如果已支付，返回 PaymentSession 对象，否则返回 None
    
    ✅ 关键修复：只要 Stripe Session paid，就把 metadata 写回 DB（assessment_id、user_id、tier）
    """
    payment_session = db.query(PaymentSession).filter(
        PaymentSession.session_id == session_id
    ).first()

    # ✅ 先从 Stripe 拿权威状态
    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.warning("[verify_payment_session] Stripe retrieve error: %s", e)
        return payment_session  # 如果 Stripe 查询失败，返回数据库记录（如果有）

    meta = stripe_session.metadata or {}
    meta_assessment_id = (meta.get("assessment_id") or "").strip() or None
    meta_user_id = (meta.get("user_id") or "").strip() or None
    meta_tier = (meta.get("tier") or "").strip() or None

    logger.info(
        "[verify_payment_session] status=%s",
        stripe_session.payment_status,
    )

    # ✅ 如果 Stripe 没付钱，直接返回 DB 记录（或 None）
    if stripe_session.payment_status != "paid":
        return payment_session

    # ✅ Stripe 已支付：确保 DB 有记录 + 写齐字段
    if payment_session:
        payment_session.status = "paid"
        payment_session.paid_at = datetime.utcnow()

        # ✅ 补齐关键字段（关键修复：确保 assessment_id 被写入）
        if not getattr(payment_session, "assessment_id", None) and meta_assessment_id:
            payment_session.assessment_id = meta_assessment_id
            logger.info("[verify_payment_session] updated assessment_id")
        
        if hasattr(payment_session, "user_id") and not getattr(payment_session, "user_id", None) and meta_user_id:
            payment_session.user_id = meta_user_id
            logger.info("[verify_payment_session] updated user_id")
        
        if meta_tier:
            payment_session.tier = meta_tier
            logger.info("[verify_payment_session] updated tier")

    else:
        # ✅ 如果数据库中没有，创建一个新记录，必须包含 assessment_id
        payment_session = PaymentSession(
            session_id=session_id,
            assessment_id=meta_assessment_id,  # ✅ 必填
            tier=meta_tier or "basic_15",
            status="paid",
            amount=stripe_session.amount_total,
            currency=stripe_session.currency,
            paid_at=datetime.utcnow()
        )
        db.add(payment_session)
        logger.info("[verify_payment_session] created PaymentSession")

    db.commit()
    db.refresh(payment_session)
    
    logger.info("[verify_payment_session] payment session ready")
    
    return payment_session

