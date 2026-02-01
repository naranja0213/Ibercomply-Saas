# Stripe 测试快速指南

## 当前状态

✅ API 和前端服务都在运行  
⚠️ 需要配置真实的 Stripe 测试密钥才能进行支付测试

## 快速配置（3 步）

### 步骤 1: 获取 Stripe 测试密钥

1. 访问 https://dashboard.stripe.com/test/apikeys
2. 确保在 **Test mode**（测试模式，不是 Live mode）
3. 复制 **Secret key**（格式：`sk_test_...`）

### 步骤 2: 配置环境变量

有两种方式：

#### 方式 A: 创建 .env 文件（推荐）

```bash
# 在项目根目录创建 .env 文件
cat > .env << EOF
STRIPE_SECRET_KEY=sk_test_你的真实密钥
FRONTEND_URL=http://localhost:3001
# STRIPE_PRICE_BASIC=price_xxx  # 可选，不设置会使用一次性价格
# STRIPE_PRICE_EXPERT=price_xxx  # 可选，不设置会使用一次性价格
EOF
```

#### 方式 B: 直接导出环境变量

```bash
export STRIPE_SECRET_KEY=sk_test_你的真实密钥
export FRONTEND_URL=http://localhost:3001
```

### 步骤 3: 重启服务

```bash
docker-compose down
docker-compose up -d
```

## 开始测试

### 1. 访问评估页面

```
http://localhost:3001/assessment/start
```

### 2. 完成评估流程

1. 选择经营状态（例如：我还没注册 Autónomo）
2. 填写表单：
   - 行业：选择任意行业（建议选择"百元店"或"餐厅"，更容易触发付费）
   - 月收入：选择较高收入（如 €3000+）
   - 员工：可以选择有员工
   - POS：可以选择有 POS
3. 提交评估

### 3. 查看结果并点击解锁

如果风险分数较高，会显示"解锁行业专属行动清单"卡片

点击 **"解锁行动清单（€15，一次性）"** 按钮

### 4. 使用 Stripe 测试卡号

在 Stripe Checkout 页面使用以下测试卡号：

```
卡号: 4242 4242 4242 4242
过期日期: 任意未来日期（如 12/34）
CVC: 任意 3 位数（如 123）
邮编: 任意 5 位数（如 12345）
姓名: 任意
```

点击"Pay"完成支付

### 5. 验证解锁内容

支付成功后，会自动跳转回结果页，你应该看到：

✅ **详细原因**（reasons）  
✅ **推荐行动**（recommended_actions）  
✅ **忽略风险后果**（risk_if_ignore）  
✅ 如果购买专家版，还会看到 **专家包内容**

## 验证支付状态

### 方法 1: 查看 Stripe Dashboard

访问 https://dashboard.stripe.com/test/payments

应该能看到刚才的测试支付记录，状态为 "Succeeded"

### 方法 2: 检查数据库

```bash
# 进入 API 容器
docker-compose exec api python3

# 在 Python 中检查
>>> from app.database import SessionLocal
>>> from app.models import PaymentSession
>>> db = SessionLocal()
>>> sessions = db.query(PaymentSession).all()
>>> for s in sessions:
...     print(f"Session: {s.session_id[:20]}... | Tier: {s.tier} | Status: {s.status}")
```

### 方法 3: 查看 API 日志

```bash
docker-compose logs api -f
```

## 其他测试卡号（不同场景）

| 场景 | 卡号 | 说明 |
|------|------|------|
| 成功支付 | `4242 4242 4242 4242` | 标准测试卡 |
| 需要 3D Secure | `4000 0025 0000 3155` | 需要额外验证 |
| 支付失败 | `4000 0000 0000 0002` | 测试支付被拒绝 |
| 需要重新授权 | `4000 0027 6000 3184` | 需要重新授权 |

## 常见问题

### Q: 点击解锁按钮后没有跳转到支付页面？

**A:** 检查：
1. `STRIPE_SECRET_KEY` 是否正确配置
2. 查看浏览器控制台（F12）是否有错误
3. 查看 API 日志：`docker-compose logs api -f`

### Q: 支付成功但内容没有解锁？

**A:** 检查：
1. 浏览器控制台是否有错误
2. URL 中是否有 `session_id` 参数
3. 调用验证 API：
   ```bash
   curl "http://localhost:8000/api/v1/payment/verify?session_id=cs_test_xxx"
   ```
   替换为实际的 session_id

### Q: 不需要真实的 Stripe 密钥可以测试吗？

**A:** 不可以。Stripe API 需要真实的密钥（即使是测试密钥）才能创建支付会话。但你可以：
- 使用免费的 Stripe 测试账户
- 测试密钥可以随意创建和删除
- 测试模式下不会产生真实费用

## 快速测试命令

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 查看 API 日志
docker-compose logs api -f

# 3. 测试 API 健康
curl http://localhost:8000/health

# 4. 测试创建支付会话（需要先配置密钥）
curl -X POST http://localhost:8000/api/v1/stripe/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{"tier": "basic"}'
```

## 下一步

测试成功后，你可以：

1. **配置 Webhook**（可选但推荐）
   - 使用 Stripe CLI 转发 webhook
   - 更可靠的支付状态更新

2. **查看完整文档**
   - 查看 `STRIPE_TESTING.md` 获取详细说明
   - 查看 `PAYMENT_SYSTEM.md` 了解系统架构

3. **准备生产环境**
   - 切换到 Stripe Live mode
   - 配置生产密钥
   - 设置真实的 Webhook endpoint

