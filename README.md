# HispanoComply v2

西班牙华人 Autónomo 合规风险评估平台（移动端优化版）

## 🎯 核心升级（v2）

### Risk + Decision 规则详细化

- ✅ **扩展输入 signals**：行业触发开关，支持细粒度风险评估
- ✅ **IndustryProfile 系统**：每个行业都有详细的画像、规则映射、checklist
- ✅ **评分模型升级**：权重上限、组合加成、扣分项机制
- ✅ **Findings 分层**：免费层/付费层（pro_only, legal_ref）
- ✅ **Decision Engine v2**：level、confidence_level、next_review_window、付费墙控制
- ✅ **通信行业拆分**：telecom_agent、fiber_install、phone_shop

### 移动端优化

- ✅ **单列布局**：完美适配手机屏幕
- ✅ **底部安全区**：支持 iPhone 刘海/手势条
- ✅ **表单控件移动化**：
  - 行业：卡片 grid（2列）
  - 收入：segmented buttons（横向滚动）
  - 员工：stepper（- / +）
  - POS：switch
- ✅ **Signals 折叠面板**：按行业显示，默认折叠
- ✅ **结果顺序优化**：结论 → 解锁 → 分数 → top3 → findings
- ✅ **BottomSheet 解锁弹窗**：手势关闭、大按钮
- ✅ **微信浏览器兼容**：fixed bottom fallback、滚动优化

## 📁 项目结构

```
hispanocomply/
├── apps/
│   ├── web/                      # Next.js 前端（移动端优化）
│   │   ├── app/
│   │   │   ├── autonomo/
│   │   │   │   ├── page.tsx      # 主页面
│   │   │   │   ├── constants.ts  # 行业和 signals 配置
│   │   │   │   └── components/   # 移动端组件
│   │   │   │       ├── IndustryGrid.tsx
│   │   │   │       ├── RevenueSegment.tsx
│   │   │   │       ├── Stepper.tsx
│   │   │   │       ├── Switch.tsx
│   │   │   │       └── SignalsPanel.tsx
│   │   │   └── globals.css       # 移动端样式 + 安全区
│   │   └── package.json
│   │
│   └── api/                      # FastAPI 后端
│       ├── app/
│       │   ├── main.py
│       │   ├── api/v1/routes/
│       │   │   ├── compliance.py  # v2 合规评估接口
│       │   │   ├── risk.py        # v1 兼容接口
│       │   │   └── stripe.py
│       │   ├── services/
│       │   │   ├── risk_engine.py      # Risk Engine v2
│       │   │   ├── decision_engine.py  # Decision Engine v2
│       │   │   └── stripe_service.py
│       │   └── schemas/
│       │       └── assessment.py  # 扩展 schemas
│       └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 1. 配置环境变量
cp apps/api/.env.example apps/api/.env
# 编辑 apps/api/.env，填入 Stripe 密钥

# 2. 启动服务
docker-compose up --build

# 或使用启动脚本
./start.sh
```

### 本地开发

**后端：**
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 然后编辑
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd apps/web
npm install
npm run dev
```

## 📱 访问地址

- 前端：http://localhost:3001
- API 文档：http://localhost:8000/docs
- API 健康检查：http://localhost:8000/health

## 🔌 API 端点

### 合规评估 v2

```
POST /api/v1/compliance/assess
Content-Type: application/json

{
  "industry": "bazar",
  "monthly_income": 3000,
  "employee_count": 0,
  "has_pos": true,
  "signals": {
    "sells_branded_goods": true,
    "keeps_supplier_invoices": false
  }
}
```

**返回：**
```json
{
  "risk_score": 75,
  "risk_level": "orange",
  "findings": [
    {
      "code": "BAZAR_BRAND",
      "title": "销售品牌商品风险",
      "detail": "...",
      "severity": "high",
      "legal_ref": "Real Decreto 1/2007",
      "pro_only": false
    }
  ],
  "decision_summary": {
    "level": "REGISTER_AUTONOMO",
    "title": "建议注册 Autónomo",
    "conclusion": "...",
    "confidence_level": "high",
    "next_review_window": "1个月",
    "reasons": [...],  // 付费墙控制
    "recommended_actions": [...],  // 付费墙控制
    "risk_if_ignore": [...]  // 付费墙控制
  }
}
```

### Stripe 支付

```
POST /api/v1/stripe/create-checkout-session
```

## 🏭 支持的行业

- `bazar` - 百元店/百货
- `restaurant` - 餐厅
- `bar` - 酒吧
- `telecom_agent` - 手机卡代理/套餐办理
- `fiber_install` - 光纤安装/Orange/Vodafone 代理
- `phone_shop` - 手机店/配件零售
- `electronics_repair` - 电子产品维修
- `beauty` - 美容美发
- `delivery` - 配送/外卖
- `other` - 其他

每个行业都有：
- 基础风险分
- 行业标签（tax, municipal, consumer, labor, data, environment）
- Signal 规则（触发条件和分数）
- 付费 checklist

## 🎨 移动端特性

- **单列布局**：所有内容垂直排列
- **底部固定按钮**：使用 sticky + safe-area
- **卡片选择**：行业、收入等使用卡片而非下拉框
- **Stepper 控件**：员工人数使用 +/- 按钮
- **Switch 控件**：POS 使用开关
- **Signals 折叠**：行业细节默认折叠，可选填写
- **结果顺序**：结论 → 解锁 → 分数 → top3 → findings
- **BottomSheet**：支付弹窗从底部滑出
- **微信兼容**：支持微信内置浏览器

## 🔒 付费墙逻辑

以下内容仅在支付后显示：
- `decision_summary.reasons`
- `decision_summary.recommended_actions`
- `decision_summary.risk_if_ignore`
- `findings` 中 `pro_only=true` 的项

解锁触发条件：
- `decision_summary.level` 为 `REGISTER_AUTONOMO`、`STRONG_REGISTER` 或 `CONSIDER_SL`

## 📊 风险评估模型

### 评分机制

1. **基础分**：行业基础风险分（10-30）
2. **Signals 分**：触发行业 signals（上限 22 分）
3. **组合加成**：特定组合增加风险（如：餐饮+露台+酒精）
4. **收入分**：基于月收入（8-30 分）
5. **员工分**：有员工 +25 分
6. **POS 分**：使用 POS +15 分
7. **扣分项**：做对的事情可以降低风险（如：有发票、有保险）

### Decision 等级

- `OK` - 风险分数 < 25
- `OBSERVE` - 风险分数 25-39
- `REGISTER_AUTONOMO` - 风险分数 40-59
- `STRONG_REGISTER` - 风险分数 ≥ 60 且无员工
- `CONSIDER_SL` - 风险分数 ≥ 60 且有员工

关键触发项会提升一个等级。

## 🔧 环境变量

```bash
# apps/api/.env
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PRICE_BASIC=price_xxx  # 可选，不提供则使用一次性价格（€15）
FRONTEND_URL=http://localhost:3001

# apps/web/.env.local（可选）
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📝 下一步

- [ ] 集成真实 Stripe 密钥和价格
- [ ] 添加用户认证
- [ ] 保存评估历史
- [ ] 发送评估报告邮件
- [ ] Webhook 处理支付成功
- [ ] 后端控制付费字段返回（没解锁不返回 reasons/actions）
- [ ] 与 gestoría 合作对接

## 🛠 技术栈

- **前端**: Next.js 14, React, TypeScript, Tailwind CSS
- **后端**: FastAPI, Python 3.11, Pydantic
- **支付**: Stripe Checkout
- **部署**: Docker Compose

## 📄 许可证

MIT
