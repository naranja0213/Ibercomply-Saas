# 🚀 Stripe 配置快速开始

## ⚡ 3 步完成配置

### 1️⃣ 获取 Stripe 测试密钥

访问：**https://dashboard.stripe.com/test/apikeys**

- 确保在 **Test mode**（不是 Live mode）
- 复制 **Secret key**（格式：`sk_test_...`）
- 如果没有账户，免费注册：https://dashboard.stripe.com/register

### 2️⃣ 配置密钥

**选项 A: 使用配置脚本（推荐）**

```bash
./setup_stripe.sh
# 按提示输入你的 Stripe Secret Key
```

**选项 B: 手动编辑 .env 文件**

```bash
# 编辑 .env 文件
# 将 STRIPE_SECRET_KEY=sk_test_请替换为你的真实密钥
# 改为：STRIPE_SECRET_KEY=sk_test_你的真实密钥
```

### 3️⃣ 重启服务

```bash
docker-compose down
docker-compose up -d
```

## ✅ 验证配置

```bash
# 检查服务状态
docker-compose ps

# 测试 API
curl http://localhost:8000/health

# 测试创建支付会话（应该返回 checkout_url）
curl -X POST http://localhost:8000/api/v1/stripe/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{"tier": "basic"}'
```

## 🧪 开始测试

1. 访问：http://localhost:3001/assessment/start
2. 完成评估
3. 点击"解锁行动清单"
4. 使用测试卡号：`4242 4242 4242 4242`
5. 查看解锁内容

详细测试步骤：查看 `STRIPE_TEST_QUICK_START.md`

## 📚 更多文档

- `SETUP_STRIPE.md` - 详细配置说明
- `STRIPE_TEST_QUICK_START.md` - 测试步骤
- `STRIPE_TESTING.md` - 完整测试指南
- `PAYMENT_SYSTEM.md` - 系统架构

