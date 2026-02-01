# Stripe 配置指南

## 快速配置（推荐）

### 方法 1: 使用配置脚本

```bash
# 运行配置脚本
./setup_stripe.sh

# 按提示输入你的 Stripe Secret Key
# 脚本会自动创建 .env 文件
```

### 方法 2: 手动配置

1. **获取 Stripe 测试密钥**

   - 访问：https://dashboard.stripe.com/test/apikeys
   - **重要**：确保在 **Test mode**（测试模式），不是 Live mode
   - 点击 "Reveal test key token" 或直接复制 Secret key
   - 格式：`sk_test_51...`（以 `sk_test_` 开头）

2. **编辑 .env 文件**

   ```bash
   # 复制模板文件
   cp .env.example .env
   
   # 编辑 .env 文件，替换 STRIPE_SECRET_KEY
   # 可以使用你喜欢的编辑器，或使用以下命令：
   ```

   在 `.env` 文件中，将：
   ```
   STRIPE_SECRET_KEY=sk_test_请替换为你的真实密钥
   ```
   
   替换为：
   ```
   STRIPE_SECRET_KEY=sk_test_你的真实密钥
   ```

3. **重启服务**

   ```bash
   docker-compose down
   docker-compose up -d
   ```

## 配置说明

### 必需配置

- `STRIPE_SECRET_KEY`: Stripe 测试密钥（必需）
  - 获取地址：https://dashboard.stripe.com/test/apikeys
  - 格式：`sk_test_...`

### 可选配置

- `STRIPE_PRICE_BASIC`: 标准版价格 ID（可选）
  - 如果不设置，系统会自动创建一次性价格（€15）
  - 如需自定义，在 Stripe Dashboard 创建产品后获取 Price ID

- `STRIPE_PRICE_EXPERT`: 专家版价格 ID（可选）
  - 如果不设置，系统会自动创建一次性价格（€39）
  - 如需自定义，在 Stripe Dashboard 创建产品后获取 Price ID

- `STRIPE_WEBHOOK_SECRET`: Webhook 签名密钥（可选）
  - 用于验证 webhook 请求的合法性
  - 获取方式：配置 webhook 后从 Stripe Dashboard 复制
  - 开发环境可以不设置（不安全，仅用于测试）

- `FRONTEND_URL`: 前端地址（默认：http://localhost:3001）
  - 用于 Stripe 支付成功后的回调地址

- `DATABASE_URL`: 数据库连接（默认：sqlite:///./payments.db）
  - 默认使用 SQLite，无需额外配置

## 验证配置

配置完成后，可以验证：

```bash
# 1. 检查 .env 文件是否存在
cat .env

# 2. 检查服务是否正常启动
docker-compose ps

# 3. 检查 API 健康状态
curl http://localhost:8000/health

# 4. 查看 API 日志（看是否有 Stripe 相关错误）
docker-compose logs api | grep -i stripe
```

## 测试支付

配置完成后，按照 `STRIPE_TEST_QUICK_START.md` 中的步骤进行测试。

### 快速测试命令

```bash
# 测试创建支付会话（应该返回 checkout_url 和 session_id）
curl -X POST http://localhost:8000/api/v1/stripe/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{"tier": "basic"}'
```

如果配置正确，应该返回类似：
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

## 常见问题

### Q: 我没有 Stripe 账户怎么办？

**A:** 
- Stripe 账户是免费的
- 访问 https://dashboard.stripe.com/register 注册
- 注册后即可使用测试模式，无需验证银行卡

### Q: 测试密钥和真实密钥有什么区别？

**A:**
- **测试密钥**（`sk_test_...`）：用于开发和测试，不会产生真实费用
- **真实密钥**（`sk_live_...`）：用于生产环境，会产生真实交易
- **当前配置使用测试密钥**，完全安全

### Q: 可以不配置价格 ID 吗？

**A:** 
- 可以！如果不配置 `STRIPE_PRICE_BASIC` 和 `STRIPE_PRICE_EXPERT`
- 系统会自动使用一次性价格（€15 或 €39）
- 这是最简单的配置方式

### Q: 配置后还是报错？

**A:** 检查：
1. `.env` 文件是否在项目根目录
2. 密钥格式是否正确（应该以 `sk_test_` 开头）
3. 是否重启了服务（`docker-compose down && docker-compose up -d`）
4. 查看 API 日志：`docker-compose logs api -f`

## 下一步

配置完成后，查看：
- `STRIPE_TEST_QUICK_START.md` - 测试步骤
- `STRIPE_TESTING.md` - 详细测试指南
- `PAYMENT_SYSTEM.md` - 系统架构说明

