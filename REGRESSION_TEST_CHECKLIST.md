# 复评提示功能回归测试清单

## 测试项

### 1. assessment.created_at = null 的老数据测试

**测试目标**：确保 GET 接口在 `created_at` 为 `null` 时不会报错，前端不显示复评卡片

**测试步骤**：
1. 在数据库中手动将某个 `assessment` 记录的 `created_at` 设置为 `NULL`
2. 调用 `GET /api/v1/compliance/assessments/{assessment_id}`
3. 检查返回的 JSON：
   - `created_at` 字段应为 `null`（不是报错）
   - 响应状态码应为 200
4. 前端访问该评估结果页
5. 检查前端：
   - 不显示复评提示卡片
   - 页面正常渲染，无错误

**预期结果**：
- ✅ 后端返回 `{"created_at": null, ...}`
- ✅ 前端不显示复评卡片
- ✅ 页面正常显示，控制台无错误

---

### 2. prefill_stage 参数异常值测试

**测试目标**：确保 `prefill_stage` 参数为异常值时，start 页不跳转、不报错

**测试场景**：

#### 场景 A：无效的 stage 值
```
URL: /assessment/start?prefill_stage=INVALID_STAGE
预期：不跳转，显示正常的选择页面
```

#### 场景 B：空字符串
```
URL: /assessment/start?prefill_stage=
预期：不跳转，显示正常的选择页面
```

#### 场景 C：SQL 注入尝试
```
URL: /assessment/start?prefill_stage=' OR '1'='1
预期：不跳转，显示正常的选择页面，不报错
```

#### 场景 D：正常值（确认功能正常）
```
URL: /assessment/start?prefill_stage=AUTONOMO
预期：自动跳转到 /assessment/form，且 URL 中不再包含 prefill_stage 参数
```

**测试步骤**：
1. 访问上述各个 URL
2. 检查浏览器控制台是否有错误
3. 检查是否发生跳转（只有场景 D 应该跳转）
4. 对于场景 D，检查跳转后的 URL 是否不包含 `prefill_stage` 参数

**预期结果**：
- ✅ 场景 A-C：不跳转，页面正常显示，无错误
- ✅ 场景 D：自动跳转到表单页，URL 干净（无 query 参数）

---

### 3. 跨日边界版本号一致性测试

**测试目标**：确认 PDF 封面版本号与 `created_at` 显示日期一致

**测试步骤**：
1. 在数据库中手动修改某个 `assessment` 记录的 `created_at`：
   - 设置为 `2026-01-02T23:30:00+00:00`（UTC 时间 23:30，对应西班牙时间 2026-01-03 00:30）
2. 下载该评估的 PDF 报告
3. 检查 PDF 封面页：
   - "评估日期" 显示的日期
   - "评估版本" 显示的版本号（例如 `v2026.01.02` 或 `v2026.01.03`）
4. 检查前端结果页：
   - 复评提示卡片中显示的评估日期（如果有）

**预期结果**：
- ✅ PDF 版本号使用 UTC 日期：`v2026.01.02`（因为 created_at 是 2026-01-02 23:30 UTC）
- ✅ PDF "评估日期" 显示：`2026年01月02日`（UTC 日期）
- ✅ 前端显示的日期也应与 UTC 日期一致

**验证逻辑**：
- 版本号基于 `created_at` 的 UTC 日期（`YYYY.MM.DD`）
- 如果 `created_at` 是 `2026-01-02T23:30:00+00:00`，版本号应为 `v2026.01.02`
- 如果 `created_at` 是 `2026-01-03T00:30:00+00:00`，版本号应为 `v2026.01.03`

---

### 4. assessment_id 无效 / 找不到测试

**测试目标**：访问不存在的 assessment_id 时，显示友好错误页，不报错

**测试步骤**：
1. 访问 `/assessment/result?assessment_id=不存在的ID`（例如：`assessment_invalid_12345`）
2. 检查前端：
   - 不显示白屏
   - 不显示 console error
   - 显示友好错误提示页面

**预期结果**：
- ✅ 显示友好错误页
- ✅ 错误文案："没找到这次评估记录。你可以重新评估一次（约 10 秒）。"
- ✅ 提供"重新评估"按钮，跳转到 `/assessment/start`
- ✅ 控制台无错误

---

### 5. 解锁状态"已支付但 tier 未更新"的兜底测试

**测试目标**：确认支付完成但 webhook 延迟时，系统仍能正确解锁

**测试步骤**：
1. 模拟 webhook 延迟场景：
   - 在数据库中手动将 `PaymentSession.status` 设置为 `"paid"`
   - 但 `Assessment.unlocked_tier` 仍为 `"none"`（模拟 webhook 未触发）
2. 访问评估结果页（使用对应的 `assessment_id`）
3. 检查：
   - 前端能否正常获取到 `unlocked_tier = "expert_39"`（或 `basic_15`）
   - 付费内容是否正常显示

**预期结果**：
- ✅ 后端 `/payment/status` 接口能检测到 `paid=true` 但 `unlocked_tier=none`
- ✅ 后端自动更新 `Assessment.unlocked_tier`（兜底逻辑）
- ✅ 前端能正常获取解锁状态
- ✅ 付费内容正常显示

**验证方法**：
```sql
-- 1. 找到一个已支付的 PaymentSession
SELECT * FROM payment_sessions WHERE status = 'paid' LIMIT 1;

-- 2. 手动将对应的 Assessment.unlocked_tier 设为 'none'（模拟 webhook 延迟）
UPDATE assessments 
SET unlocked_tier = 'none' 
WHERE assessment_id = 'your_assessment_id';

-- 3. 访问结果页，应该自动解锁
```

---

## 快速测试脚本

### 测试 1：created_at = null

```bash
# 1. 修改数据库（使用 PostgreSQL）
psql -d your_database -c "UPDATE assessments SET created_at = NULL WHERE assessment_id = 'your_test_assessment_id';"

# 2. 测试 API
curl http://localhost:8000/api/v1/compliance/assessments/your_test_assessment_id

# 预期：返回 {"created_at": null, ...}
```

### 测试 2：prefill_stage 异常值

```bash
# 在浏览器中访问以下 URL：
# http://localhost:3001/assessment/start?prefill_stage=INVALID
# http://localhost:3001/assessment/start?prefill_stage=
# http://localhost:3001/assessment/start?prefill_stage=AUTONOMO

# 检查：
# - 前两个不应跳转
# - 第三个应自动跳转到 /assessment/form（且 URL 干净）
```

### 测试 3：跨日边界版本号

```sql
-- 修改数据库
UPDATE assessments 
SET created_at = '2026-01-02T23:30:00+00:00'::timestamptz
WHERE assessment_id = 'your_test_assessment_id';

-- 然后下载 PDF，检查版本号是否为 v2026.01.02
```

---

### 测试 4：assessment_id 无效

```bash
# 在浏览器中访问：
# http://localhost:3001/assessment/result?assessment_id=不存在的ID

# 检查：
# - 显示友好错误页
# - 有"重新评估"按钮
# - 控制台无错误
```

### 测试 5：支付兜底逻辑

```sql
-- 1. 找到已支付的 PaymentSession
SELECT session_id, assessment_id, tier, status 
FROM payment_sessions 
WHERE status = 'paid' 
LIMIT 1;

-- 2. 手动将对应 Assessment 的 unlocked_tier 设为 'none'
UPDATE assessments 
SET unlocked_tier = 'none' 
WHERE assessment_id = 'your_assessment_id';

-- 3. 访问结果页，应该自动解锁
```

---

## 发布流程集成

**⚠️ 重要：每次发版前必须执行回归测试**

建议在发布流程中加入以下步骤：

1. **代码审查后、部署前**：执行回归测试清单中的所有测试项
2. **测试结果记录**：在 GitHub Issue 或 Release Notes 中记录测试结果
3. **失败处理**：任何测试项失败，必须修复后才能发布

**快速检查清单（5分钟版本）**：
- [ ] 测试 1：`created_at = null` 不报错
- [ ] 测试 2：`prefill_stage` 异常值不跳转
- [ ] 测试 3：PDF 版本号一致性
- [ ] 测试 4：无效 `assessment_id` 友好错误页
- [ ] 测试 5：支付兜底逻辑正常工作

---

## 验收标准

- [x] `created_at = null` 时后端不报错，返回 `null`
- [x] `created_at = null` 时前端不显示复评卡片，页面正常
- [x] `prefill_stage` 无效值时 start 页不跳转，不报错
- [x] `prefill_stage` 有效值时自动跳转，URL 干净（无 query 参数）
- [x] PDF 版本号与 `created_at` UTC 日期一致
- [x] 无效 `assessment_id` 显示友好错误页，不白屏
- [x] 支付完成但 webhook 延迟时，兜底逻辑能自动解锁
- [x] 代码通过 linter 检查

