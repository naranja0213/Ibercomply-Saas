# 快速启动指南

## 1. 启动后端

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 Stripe 密钥（测试环境可先填 sk_test_xxx）
uvicorn app.main:app --reload --port 8000
```

## 2. 启动前端

```bash
cd apps/web
npm install
npm run dev
```

## 3. 访问应用

- 前端: http://localhost:3000/autonomo
- API 文档: http://localhost:8000/docs

## 4. 测试 API

### 测试合规评估接口

```bash
curl -X POST http://localhost:8000/api/v1/compliance/assess \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "bazar",
    "monthly_income": 3000,
    "employee_count": 0,
    "has_pos": true,
    "signals": {
      "sells_branded_goods": true,
      "keeps_supplier_invoices": false
    }
  }'
```

### 测试 Stripe 支付接口

```bash
curl -X POST http://localhost:8000/api/v1/stripe/create-checkout-session \
  -H "Content-Type: application/json"
```

## 5. 验证功能点

### 后端验证
- [x] `/api/v1/compliance/assess` 返回完整的风险评估结果
- [x] 风险分数计算正确（0-100）
- [x] Decision 等级正确（OK/OBSERVE/REGISTER_AUTONOMO/STRONG_REGISTER/CONSIDER_SL）
- [x] Findings 包含 pro_only 字段
- [x] Decision Summary 包含 confidence_level 和 next_review_window

### 前端验证
- [x] 行业卡片选择（2列布局）
- [x] 收入分段按钮（横向滚动）
- [x] 员工 stepper（+/- 按钮）
- [x] POS switch（开关）
- [x] Signals 折叠面板（按行业显示）
- [x] 结果展示（结论 → 解锁 → 分数 → top3 → findings）
- [x] 底部固定按钮（支持安全区）
- [x] 解锁弹窗（从底部滑出）

## 6. 移动端测试

在手机上访问 http://YOUR_IP:3000/autonomo，验证：
- [x] 单列布局，无横向滚动
- [x] 底部按钮不被遮挡（iPhone 安全区）
- [x] 表单控件易于点击
- [x] 微信浏览器兼容（可选）

## 注意事项

1. **Stripe 配置**：如果没有配置真实的 Stripe 密钥，支付功能会失败，但不影响风险评估功能
2. **CORS**：后端已配置允许 localhost:3000，如需其他域名需修改 `apps/api/app/main.py`
3. **环境变量**：前端使用 `NEXT_PUBLIC_API_BASE_URL` 环境变量，默认 `http://localhost:8000`

