# v2 规则实现总结

## ✅ 已完成实现

### 1. Risk Engine v2 (`apps/api/app/services/risk_engine.py`)

#### A. 风险权重总规则
- ✅ **Signals 加分上限**：`SIGNALS_POINTS_CAP = 22`
- ✅ **Critical triggers 计数**：每个 critical signal 增加 `critical_count`
- ✅ **组合加成**：实现了所有行业的 combo rules

#### B. 行业 Signals 规则表
已实现以下行业的完整规则：

1. **零售行业**（bazar / supermarket / phone_shop）
   - 8 个 signals
   - 2 个 combo rules（COMBO_BRAND_SOURCE, COMBO_IMPORT_LABEL）

2. **餐饮行业**（restaurant / bar / takeaway）
   - 8 个 signals
   - 2 个 combo rules（COMBO_MUNICIPAL_NOISE, COMBO_RECORDS）

3. **通信代理**（telecom_agent）
   - 4 个 signals
   - 1 个 combo rule（COMBO_DATA_PROTECTION）

4. **光纤安装**（fiber_install）
   - 4 个 signals
   - 1 个 combo rule（COMBO_SUBCONTRACT_PRL）

5. **维修**（electronics_repair）
   - 6 个 signals
   - 1 个 combo rule（COMBO_EWASTE_TRACE）

6. **美业**（beauty）
   - 6 个 signals
   - 1 个 combo rule（COMBO_CLIENT_DATA）

7. **配送**（delivery）
   - 5 个 signals
   - 1 个 combo rule（COMBO_PLATFORM_LABOR）

#### C. 评分逻辑
- 基础分（行业 base）
- Signals 分（有上限 22）
- 组合加成（combo rules）
- 收入分（8/18/30）
- 员工分（+25）
- POS 分（+15）
- 最终得分上限 100

### 2. Decision Engine v2 (`apps/api/app/services/decision_engine.py`)

#### C. Decision 触发规则
- ✅ **基础映射**：score < 25 → OK, < 40 → OBSERVE, < 60 → REGISTER_AUTONOMO, ≥ 60 → STRONG_REGISTER/CONSIDER_SL
- ✅ **Bump 1**：critical_count ≥ 1 OR revenue_range == "7000+" OR employees ≥ 2
- ✅ **Bump 2**：critical_count ≥ 2 OR (employees ≥ 1 AND critical_count ≥ 1) OR score ≥ 70
- ✅ **CONSIDER_SL 触发**：
  - employees ≥ 1 AND (score ≥ 60 OR critical_count ≥ 1)
  - revenue_range == "7000+" AND score ≥ 55
  - 行业标签包含 "labor" 且 employees ≥ 1

#### D. 付费墙字段控制
- ✅ **免费必给**：level, title, conclusion, confidence_level, next_review_window
- ✅ **付费解锁**：reasons (最多 3 条), recommended_actions (8-12 条), risk_if_ignore (2-3 条)

### 3. API 路由 (`apps/api/app/api/v1/routes/compliance.py`)

- ✅ `/api/v1/compliance/assess` 接口
- ✅ 返回结构：risk_score, risk_level, findings, decision_summary
- ✅ Meta 信息：critical_count, tags（在内部计算使用）

### 4. 前端配置 (`apps/web/app/autonomo/constants.ts`)

- ✅ 更新了所有行业的 signals 配置
- ✅ 添加了 supermarket 和 takeaway 行业
- ✅ 更新了收入选项（包含 7000+ 档位）
- ✅ 添加了 INDUSTRY_LABELS 映射

## 📋 实现细节

### Signals 规则结构
```python
SignalRule(
    points: int,           # 分数（可为负）
    severity: str,         # info/low/medium/high
    critical: bool,        # 是否为关键触发
    finding: Finding       # 对应的 finding
)
```

### Combo Rules 结构
```python
ComboRule(
    condition: Dict[str, bool],  # 需要同时满足的 signals
    points: int,                 # 额外加分
    finding: Finding             # combo finding
)
```

### Critical Combo Codes
以下 combo findings 会增加 critical_count：
- COMBO_BRAND_SOURCE
- COMBO_MUNICIPAL_NOISE
- COMBO_DATA_PROTECTION
- COMBO_SUBCONTRACT_PRL
- COMBO_CLIENT_DATA
- COMBO_PLATFORM_LABOR

## 🧪 测试建议

### 测试用例 1：零售 + 品牌商品 + 无发票
```json
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
预期：触发 COMBO_BRAND_SOURCE，critical_count = 1

### 测试用例 2：餐饮 + 露台 + 酒精 + 深夜
```json
{
  "industry": "restaurant",
  "monthly_income": 4000,
  "employee_count": 2,
  "has_pos": true,
  "signals": {
    "has_terrace": true,
    "serves_alcohol": true,
    "late_opening_hours": true
  }
}
```
预期：触发 COMBO_MUNICIPAL_NOISE，critical_count = 1，bump 2 档

### 测试用例 3：通信代理 + 处理身份证 + 保存照片 + 无流程
```json
{
  "industry": "telecom_agent",
  "monthly_income": 2500,
  "employee_count": 0,
  "has_pos": false,
  "signals": {
    "handles_customer_ids": true,
    "stores_id_photos": true,
    "no_data_policy": true
  }
}
```
预期：触发 COMBO_DATA_PROTECTION，critical_count = 1

## 🚀 下一步

1. **安装依赖并测试**：
   ```bash
   cd apps/api
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **测试 API**：
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

3. **前端测试**：启动前端，测试 signals 选择和组合加成效果

4. **付费墙测试**：验证 reasons/actions/risk_if_ignore 是否正确控制显示

## 📝 注意事项

1. **Signals 上限**：已经实现 22 分上限，防止 signals 过多导致分数爆炸
2. **Critical Count**：只在 signal rules 和 critical combo 中增加
3. **Bump 逻辑**：最多 bump 2 档，CONSIDER_SL 有特殊触发条件
4. **Revenue Range**：自动计算（low/medium/high/7000+），用于 bump 判断

