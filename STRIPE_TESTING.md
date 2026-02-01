# Stripe 支付测试指南

## 快速开始

### 1. 获取 Stripe 测试密钥

1. 访问 [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. 确保在 **Test mode**（测试模式）
3. 复制以下密钥：
   - **Publishable key** (pk_test_xxx) - 前端使用（可选）
   - **Secret key** (sk_test_xxx) - 后端使用（必需）

### 2. 配置环境变量

在 `docker-compose.yml` 或 `.env` 文件中设置：

```bash
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PRICE_BASIC=price_xxx  # 可选，如果使用自定义价格
STRIPE_PRICE_EXPERT=price_xxx  # 可选，如果使用自定义价格
FRONTEND_URL=http://localhost:3001
```

如果不想创建自定义价格，可以不设置 `STRIPE_PRICE_BASIC` 和 `STRIPE_PRICE_EXPERT`，系统会自动使用一次性价格（€15 或 €39）。

### 3. 重启服务

```bash
docker-compose down
docker-compose up -d
```

## 测试步骤

### 步骤 1: 完成评估

1. 访问 `http://localhost:3001/assessment/start`
2. 选择你的经营状态（PRE_AUTONOMO / AUTONOMO / SL）
3. 填写评估表单
4. 提交评估

### 步骤 2: 查看结果页

1. 查看免费评估结果
2. 如果触发付费解锁，会看到"解锁行业专属行动清单"卡片

### 步骤 3: 点击解锁按钮

1. 点击"解锁行动清单（€15，一次性）"按钮
2. 系统会创建 Stripe Checkout Session
3. 自动跳转到 Stripe 支付页面

### 步骤 4: 使用测试卡号支付

在 Stripe Checkout 页面使用以下测试卡号：

**成功支付卡号**:
```
卡号: 4242 4242 4242 4242
过期日期: 任意未来日期（如 12/34）
CVC: 任意 3 位数（如 123）
ZIP: 任意 5 位数（如 12345）
```

**其他测试场景**:

- **需要 3D Secure 验证**: `4000 0025 0000 3155`
- **支付失败**: `4000 0000 0000 0002`
- **需要重新授权**: `4000 0027 6000 3184`

### 步骤 5: 支付成功回调

1. 支付完成后，Stripe 会重定向到 `/assessment/result?session_id=xxx`
2. 前端自动检测 `session_id` 并验证支付状态
3. 如果验证成功，会重新请求评估结果并显示解锁内容

## 测试验证点

### 1. 检查支付会话创建

```bash
# 查看 API 日志
docker-compose logs api -f

# 应该看到创建 checkout session 的请求
```

### 2. 检查数据库记录

```bash
# 进入 API 容器
docker-compose exec api python3

# 在 Python 中检查数据库
>>> from app.database import SessionLocal
>>> from app.models import PaymentSession
>>> db = SessionLocal()
>>> sessions = db.query(PaymentSession).all()
>>> for s in sessions:
...     print(f"{s.session_id} - {s.tier} - {s.status}")
```

### 3. 验证支付状态

```bash
# 测试支付验证 API
curl "http://localhost:8000/api/v1/payment/verify?session_id=cs_test_xxx"
```

### 4. 检查解锁内容

支付成功后，结果页应该显示：
- ✅ 详细原因（reasons）
- ✅ 推荐行动（recommended_actions）
- ✅ 忽略风险后果（risk_if_ignore）
- ✅ 专家版内容（如果购买 expert tier）

## Stripe Dashboard 检查

1. 访问 [Stripe Dashboard > Payments](https://dashboard.stripe.com/test/payments)
2. 应该看到测试支付记录
3. 检查支付状态是否为 "Succeeded"

## Webhook 测试（可选）

### 使用 Stripe CLI

1. 安装 [Stripe CLI](https://stripe.com/docs/stripe-cli)

2. 登录 Stripe CLI
```bash
stripe login
```

3. 转发 webhook 到本地
```bash
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook
```

4. 复制显示的 webhook secret（whsec_xxx）
5. 添加到环境变量：`STRIPE_WEBHOOK_SECRET=whsec_xxx`
6. 重启服务

这样 webhook 会在支付成功时自动更新数据库状态。

## 常见问题

### 1. 支付失败

**问题**: 创建 checkout session 失败

**解决**:
- 检查 `STRIPE_SECRET_KEY` 是否正确
- 确保使用测试模式的密钥（sk_test_xxx）
- 查看 API 日志错误信息

### 2. 支付成功但未解锁

**问题**: 支付完成但内容未解锁

**解决**:
- 检查前端控制台是否有错误
- 验证 `session_id` 是否正确传递
- 检查 `/api/v1/payment/verify` 是否返回 `verified: true`
- 查看数据库中的支付状态是否为 "paid"

### 3. Webhook 不工作

**问题**: Webhook 未触发

**解决**:
- 确保 Stripe CLI 正在运行
- 检查 webhook endpoint URL 是否正确
- 查看 API 日志是否有 webhook 请求

## 调试技巧

### 查看 API 日志
```bash
docker-compose logs api -f
```

### 查看前端日志
打开浏览器开发者工具（F12）→ Console

### 测试支付验证端点
```bash
# 替换为实际的 session_id
curl "http://localhost:8000/api/v1/payment/verify?session_id=cs_test_xxx"
```

### 直接检查 Stripe Session
```bash
# 在 API 容器中
docker-compose exec api python3

>>> import stripe
>>> import os
>>> stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
>>> session = stripe.checkout.Session.retrieve("cs_test_xxx")
>>> print(session.payment_status)  # 应该显示 "paid"
```

## 生产环境准备

在生产环境部署前，需要：

1. **切换到生产模式**
   - 在 Stripe Dashboard 切换到 Live mode
   - 使用生产密钥（sk_live_xxx）

2. **配置 Webhook**
   - 在 Stripe Dashboard 创建 webhook endpoint
   - URL: `https://your-domain.com/api/v1/stripe/webhook`
   - 选择事件: `checkout.session.completed`
   - 复制 webhook secret 到环境变量

3. **测试生产流程**
   - 使用真实卡号进行小额测试
   - 验证 webhook 正常触发
   - 检查数据库记录

4. **安全考虑**
   - 确保 `STRIPE_WEBHOOK_SECRET` 已设置（用于验证签名）
   - 使用 HTTPS
   - 限制 API 访问权限

