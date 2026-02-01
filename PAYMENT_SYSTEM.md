# 付费解锁系统实现说明

## 概述

已实现完整的付费解锁系统，包括数据库持久化、Stripe 支付集成、Webhook 验证和后端安全验证。

## 核心功能

### 1. 数据库持久化

- **数据库**: SQLite（简单，无需额外配置）
- **表结构**: `payment_sessions`
  - `session_id`: Stripe Checkout Session ID（唯一索引）
  - `assessment_id`: 评估结果标识（可选）
  - `tier`: "basic" 或 "expert"
  - `status`: "pending", "paid", "failed"
  - `amount`: 金额（分）
  - `currency`: 货币
  - `paid_at`: 支付完成时间
  - `created_at`, `updated_at`: 时间戳

### 2. 支付流程

#### 步骤 1: 创建支付会话
```
POST /api/v1/stripe/create-checkout-session
Body: { tier: "basic" | "expert", assessment_id?: string }
→ 返回: { checkout_url, session_id }
```

- 创建 Stripe Checkout Session
- 保存 session 信息到数据库（status: "pending"）
- 设置 success_url: `/assessment/result?session_id={CHECKOUT_SESSION_ID}`

#### 步骤 2: 用户支付
- 跳转到 Stripe Checkout 页面
- 用户完成支付

#### 步骤 3: Stripe Webhook（可选，推荐）
```
POST /api/v1/stripe/webhook
Headers: stripe-signature (用于验证)
Body: Stripe Event (checkout.session.completed)
→ 更新数据库 status: "paid"
```

#### 步骤 4: 支付成功回调
- Stripe 重定向到: `/assessment/result?session_id=xxx`
- 前端检测到 `session_id` 参数
- 调用 `/api/v1/payment/verify?session_id=xxx` 验证支付状态
- 如果已验证，使用 `session_id` 重新请求评估结果

### 3. 后端验证（安全）

#### 验证支付状态
```
GET /api/v1/payment/verify?session_id=xxx
→ 返回: { verified: true/false, tier: "basic"/"expert", status: "paid"/"pending" }
```

#### 获取评估结果（带解锁）
```
POST /api/v1/compliance/assess?session_id=xxx
Body: { stage, industry, monthly_income, ... }
→ 返回: RiskAssessmentResponse（根据 session_id 自动解锁对应层级）
```

**安全机制**:
- 后端根据 `session_id` 从数据库验证支付状态
- 如果数据库中状态为 "paid"，自动解锁对应层级
- 如果数据库中没有记录，会尝试从 Stripe API 验证
- **不再依赖前端 header**，无法被绕过

### 4. 解锁层级

| 层级 | unlocked_tier | 解锁内容 |
|------|---------------|----------|
| 免费 | `none` | Decision、风险分数、Top 3 风险点、Findings（部分） |
| €15 标准版 | `basic_15` | 以上 + reasons + recommended_actions + risk_if_ignore |
| €39 专家版 | `expert_39` | 以上 + expert_pack（风险分组、30天路线图、材料清单、自检表） |

## 文件结构

### 后端

```
apps/api/app/
├── database.py              # 数据库配置（SQLite + SQLAlchemy）
├── models.py                # 数据模型（PaymentSession）
├── services/
│   └── stripe_service.py    # Stripe 服务（创建 session、验证支付）
└── api/v1/routes/
    ├── stripe.py            # Stripe 路由（创建 session、webhook）
    ├── payment.py           # 支付验证路由
    └── compliance.py        # 评估路由（根据 session_id 解锁）
```

### 前端

```
apps/web/app/assessment/
├── form/page.tsx            # 表单页（保存 assessment_input 到 sessionStorage）
└── result/page.tsx          # 结果页（处理 session_id 回调、显示解锁内容）
```

## 环境变量

```bash
# Stripe 配置
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PRICE_BASIC=price_xxx
STRIPE_PRICE_EXPERT=price_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx  # 可选，用于验证 webhook 签名

# 数据库
DATABASE_URL=sqlite:///./payments.db  # 默认

# 前端 URL
FRONTEND_URL=http://localhost:3001
```

## 安全特性

✅ **后端验证**: 根据 session_id 从数据库验证支付状态  
✅ **Webhook 验证**: 支持 Stripe webhook 签名验证  
✅ **数据库持久化**: 支付状态保存在数据库，刷新不丢失  
✅ **双重验证**: 数据库 + Stripe API 双重验证  
✅ **移除前端 header**: 不再依赖 `X-Unlocked-Tier` header，无法被绕过

## 使用流程

1. **用户完成评估** → 查看结果页（免费内容）

2. **点击解锁按钮** → 
   - 调用 `/api/v1/stripe/create-checkout-session`
   - 跳转到 Stripe 支付页面

3. **完成支付** → 
   - Stripe 重定向到 `/assessment/result?session_id=xxx`
   - Webhook 同时更新数据库状态（可选，更可靠）

4. **前端处理回调** → 
   - 检测到 `session_id` 参数
   - 调用 `/api/v1/payment/verify` 验证
   - 使用 `session_id` 重新请求评估结果

5. **显示解锁内容** → 
   - 后端根据 `session_id` 验证并返回解锁内容
   - 前端显示完整的 reasons、actions、expert_pack 等

## 注意事项

1. **Webhook 配置**:
   - 在 Stripe Dashboard 中配置 webhook endpoint: `https://your-domain.com/api/v1/stripe/webhook`
   - 选择事件: `checkout.session.completed`
   - 复制 webhook secret 到环境变量 `STRIPE_WEBHOOK_SECRET`

2. **开发环境**:
   - 可以使用 Stripe CLI 转发 webhook: `stripe listen --forward-to localhost:8000/api/v1/stripe/webhook`
   - 或使用测试模式，不验证 webhook 签名（不安全，仅开发）

3. **数据库文件**:
   - SQLite 文件会保存在容器内的 `/app/payments.db`
   - 如果需要持久化，可以在 docker-compose.yml 中添加 volume

4. **测试支付**:
   - 使用 Stripe 测试卡号: `4242 4242 4242 4242`
   - 任意未来日期、任意 CVC

## 下一步优化

- [ ] 添加用户系统（关联支付到用户账户）
- [ ] 添加支付历史查询 API
- [ ] 支持退款处理
- [ ] 添加支付统计和报表

