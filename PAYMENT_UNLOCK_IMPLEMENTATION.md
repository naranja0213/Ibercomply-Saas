# 支付解锁闭环实现总结

## ✅ 已实现的功能

### 1. 后端数据库模型

**文件**: `apps/api/app/models.py`

- ✅ **Assessment 模型**：存储评估结果的解锁状态
  - `assessment_id`: 评估结果唯一标识
  - `user_id`: 用户 ID（可选）
  - `unlocked_tier`: 解锁级别（"none", "basic_15", "expert_39"）
  - `unlocked_at`: 解锁时间
  - `stripe_session_id`: 最后一次支付的 session_id（防重复）

### 2. 后端 API

#### A. 创建支付会话

**文件**: `apps/api/app/api/v1/routes/stripe.py`

**端点**: `POST /api/v1/stripe/create-checkout-session`

**功能**:
- 接收 `assessment_id`, `user_id`, `tier`
- 创建 Stripe Checkout Session
- 在 metadata 中包含：`user_id`, `assessment_id`, `tier`
- `success_url` 指向 `/payment/success?session_id={CHECKOUT_SESSION_ID}`
- 保存 PaymentSession 到数据库

#### B. Webhook 处理

**文件**: `apps/api/app/api/v1/routes/stripe.py`

**端点**: `POST /api/v1/stripe/webhook`

**功能**:
- 监听 `checkout.session.completed` 事件
- 从 metadata 中提取 `user_id`, `assessment_id`, `tier`
- 更新 PaymentSession 状态为 "paid"
- **关键**：更新 Assessment 表的 `unlocked_tier` 字段
  - `tier == "expert"` → `unlocked_tier = "expert_39"`
  - `tier == "basic"` → `unlocked_tier = "basic_15"`
- 记录 `stripe_session_id` 防止重复处理

#### C. 支付状态查询

**文件**: `apps/api/app/api/v1/routes/payment.py`

**端点**: `GET /api/v1/payment/status?session_id=...`

**功能**:
- 根据 session_id 查询支付状态
- 返回：
  - `paid`: 是否已支付
  - `assessment_id`: 评估 ID
  - `unlocked_tier`: 解锁级别

### 3. 前端页面

#### A. 支付成功页面

**文件**: `apps/web/app/payment/success/page.tsx`

**功能**:
1. 从 URL 获取 `session_id`
2. 调用 `/api/v1/payment/status` 查询支付状态
3. 如果已支付：
   - 保存 `unlocked_tier` 到 `sessionStorage`
   - （可选）重新获取完整的评估结果
   - 显示成功消息
   - 跳转到 `/assessment/result`

#### B. 结果页面

**文件**: `apps/web/app/assessment/result/page.tsx`

**改动**:
- `handleUnlockConfirm()` 现在传递 `assessment_id` 和 `user_id`
- 移除 `handlePaymentCallback`（由 success 页面处理）
- 从 `sessionStorage` 读取 `assessment_unlocked_tier`

#### C. 表单页面

**文件**: `apps/web/app/assessment/form/page.tsx`

**改动**:
- 提交评估时生成 `assessment_id` 并保存到 `sessionStorage`

## 🔄 完整支付流程

```
1. 用户完成评估
   → Form 页生成 assessment_id
   → 保存到 sessionStorage

2. 用户点击"解锁 €15"
   → Result 页调用 handleUnlockConfirm()
   → 获取/生成 assessment_id 和 user_id
   → 调用 POST /api/v1/stripe/create-checkout-session
   → 跳转到 Stripe Checkout

3. 用户在 Stripe 完成支付
   → Stripe 重定向到 /payment/success?session_id=...
   → 同时 Stripe 调用 POST /api/v1/stripe/webhook

4. Webhook 处理（后端）
   → 验证支付成功
   → 更新 Assessment.unlocked_tier = "basic_15" 或 "expert_39"
   → 更新 PaymentSession.status = "paid"

5. Success 页面处理（前端）
   → 调用 GET /api/v1/payment/status?session_id=...
   → 获取 unlocked_tier
   → 保存到 sessionStorage.setItem("assessment_unlocked_tier", unlocked_tier)
   → 跳转到 /assessment/result

6. Result 页面显示解锁内容
   → 从 sessionStorage 读取 assessment_unlocked_tier
   → 如果 unlocked_tier !== "none"，显示付费内容
```

## 🔍 验证步骤

### 1. 检查数据库

```bash
# 进入 API 容器
docker-compose exec api python3

# 检查 Assessment 表
>>> from app.database import SessionLocal
>>> from app.models import Assessment, PaymentSession
>>> db = SessionLocal()
>>> assessments = db.query(Assessment).all()
>>> for a in assessments:
...     print(f"{a.assessment_id} - {a.unlocked_tier} - {a.stripe_session_id}")
```

### 2. 检查 Webhook

```bash
# 使用 Stripe CLI 转发 webhook
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook

# 查看日志
docker-compose logs api -f | grep webhook
```

### 3. 检查支付流程

1. ✅ 完成评估
2. ✅ 点击解锁按钮
3. ✅ 使用测试卡号支付（4242 4242 4242 4242）
4. ✅ 检查是否跳转到 /payment/success
5. ✅ 检查是否跳转回 /assessment/result
6. ✅ 检查是否显示解锁内容

### 4. 检查 Stripe Dashboard

- 访问 https://dashboard.stripe.com/test/payments
- 查看支付记录状态是否为 "Succeeded"
- 查看 Session 的 metadata 是否包含 `assessment_id` 和 `user_id`

## ⚠️ 注意事项

1. **Webhook Secret**（生产环境必需）：
   - 开发环境可以不设置（不安全）
   - 生产环境必须设置 `STRIPE_WEBHOOK_SECRET`

2. **数据库迁移**：
   - 重启服务后会自动创建 `assessments` 表
   - 如果已有数据库，可能需要删除重建或手动迁移

3. **评估 ID 持久化**：
   - 目前使用 `sessionStorage`（页面关闭后丢失）
   - 未来可以改为后端生成并返回，存储在数据库

4. **用户 ID**：
   - 目前使用 `localStorage` 生成（每次访问保持不变）
   - 未来可以改为后端生成，存储在数据库

## 🐛 常见问题排查

### 问题 1: 支付成功但未解锁

**检查**:
1. Webhook 是否收到事件？（Stripe Dashboard → Webhooks → Events）
2. Webhook 是否成功写入数据库？（检查 Assessment 表）
3. Success 页面是否调用了 `/api/v1/payment/status`？
4. `sessionStorage` 中是否有 `assessment_unlocked_tier`？

### 问题 2: Webhook 未触发

**检查**:
1. `STRIPE_WEBHOOK_SECRET` 是否设置？
2. Stripe Dashboard 中 Webhook 端点是否配置正确？
3. 开发环境是否使用 Stripe CLI 转发？

### 问题 3: assessment_id 不匹配

**检查**:
1. Form 提交时是否正确生成并保存 `assessment_id`？
2. Unlock 时是否使用了相同的 `assessment_id`？
3. Webhook 中的 `assessment_id` 是否正确？

