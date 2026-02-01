# 快速修复指南（给 Cursor）

## 任务清单（按顺序执行）

### ✅ A. 修复后端 Schema（必须）

**文件**: `apps/api/app/schemas/assessment.py`

**改动**：在 `DecisionSummary` class 中添加三个字段

```python
class DecisionSummary(BaseModel):
    # ... 现有字段保持不变 ...
    
    # ✅ 新增字段（添加在 next_review_window 之后）
    paywall: Literal["none", "basic_15", "expert_39"] = "none"
    pay_reason: Optional[str] = None
    top_risks: List[Finding] = Field(default_factory=list)
    
    # ... 其他字段保持不变 ...
```

### ✅ B. 修复后端 Decision Engine（必须）

**文件**: `apps/api/app/services/decision_engine.py`

**改动位置 1**：PRE_AUTONOMO 分支（约第 160 行）

```python
# 在 return DecisionSummarySchema 之前添加：
if decision_level in ["REGISTER_AUTONOMO", "STRONG_REGISTER_AUTONOMO"]:
    paywall = "basic_15"
    pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
else:
    paywall = "none"
    pay_reason = None

return DecisionSummarySchema(
    level=decision_level,
    decision_intent=decision_intent,
    title=title,
    conclusion=conclusion,
    confidence_level=conf,
    next_review_window=next_review,
    paywall=paywall,  # ✅ 新增
    pay_reason=pay_reason,  # ✅ 新增
    top_risks=top3_findings,  # ✅ 新增（已在第115行计算）
    reasons=reasons,
    recommended_actions=actions,
    risk_if_ignore=risks_ignore,
    expert_pack=expert_pack,
    pro_brief=ProBrief(...),
)
```

**改动位置 2**：AUTONOMO 分支（约第 219 行）

```python
# 在 return DecisionSummarySchema 之前添加：
if decision_level in ["CONSIDER_SL", "RISK_AUTONOMO"]:
    paywall = "basic_15"
    pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
else:
    paywall = "none"
    pay_reason = None

return DecisionSummarySchema(
    # ... 其他字段
    paywall=paywall,  # ✅ 新增
    pay_reason=pay_reason,  # ✅ 新增
    top_risks=top3_findings,  # ✅ 新增
    # ...
)
```

**改动位置 3**：SL 分支（约第 276 行）

```python
# 在 return DecisionSummarySchema 之前添加：
if decision_level in ["RISK_SL_LOW", "RISK_SL_HIGH"]:
    paywall = "basic_15"
    pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
else:
    paywall = "none"
    pay_reason = None

return DecisionSummarySchema(
    # ... 其他字段
    paywall=paywall,  # ✅ 新增
    pay_reason=pay_reason,  # ✅ 新增
    top_risks=top3_findings,  # ✅ 新增
    # ...
)
```

### ✅ C. 替换 Result 页（必须）

**文件**: `apps/web/app/assessment/result/page.tsx`

**操作**：**完全替换**为用户提供的模板代码（已在对话中提供）

**关键点**：
- 使用 `decision_summary.paywall` 判断付费墙（不再用 `level`）
- 使用 `decision_summary.top_risks` 显示 Top 3（不再自己过滤）
- 移除所有业务判断逻辑
- 移除 `filterFindingsForDecision` 函数

### ✅ D. 修复表单提交（必须）

**文件**: `apps/web/app/assessment/form/page.tsx`

**改动位置**：在 `handleSubmit` 函数中，保存结果后（约第 85 行）

```typescript
// 在 sessionStorage.setItem("assessment_result", ...) 之后添加：
sessionStorage.setItem("assessment_unlocked_tier", "none");
```

完整代码块：
```typescript
const data = await response.json();

sessionStorage.setItem("assessment_result", JSON.stringify(data));
sessionStorage.setItem("assessment_input", JSON.stringify({
  stage,
  industry,
  monthly_income: monthlyIncome,
  employee_count: employeeCount,
  has_pos: hasPos,
  signals,
}));
sessionStorage.setItem("assessment_unlocked_tier", "none");  // ✅ 新增
router.push("/assessment/result");
```

---

## 验证步骤

1. **检查后端返回**：
```bash
curl -X POST http://localhost:8000/api/v1/compliance/assess \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "PRE_AUTONOMO",
    "industry": "bazar",
    "monthly_income": 3000,
    "employee_count": 0,
    "has_pos": true,
    "signals": {}
  }' | jq '.decision_summary | {paywall, pay_reason, top_risks: (.top_risks | length)}'
```

应该返回：
```json
{
  "paywall": "basic_15",
  "pay_reason": "解锁后可查看详细原因、行动清单和忽略风险后果",
  "top_risks": 3
}
```

2. **检查前端**：
- 访问 `/assessment/start` → 填写表单 → 提交
- 检查浏览器控制台的 `sessionStorage`：
  - `assessment_result` 存在
  - `assessment_unlocked_tier` = `"none"`
- 检查 Result 页是否使用 `decision_summary.paywall` 判断付费墙

---

## 文件清单

需要修改的文件：
1. ✅ `apps/api/app/schemas/assessment.py` - 添加字段
2. ✅ `apps/api/app/services/decision_engine.py` - 返回新字段
3. ✅ `apps/web/app/assessment/result/page.tsx` - 完全替换
4. ✅ `apps/web/app/assessment/form/page.tsx` - 添加 unlocked_tier 保存

---

## 注意事项

- ⚠️ 确保所有三个分支（PRE_AUTONOMO、AUTONOMO、SL）都添加了 `paywall`、`pay_reason`、`top_risks`
- ⚠️ `top3_findings` 已经在函数开头计算（第115行），直接使用即可
- ⚠️ 新的 Result 页模板已经包含了支付回调处理，不需要额外修改
- ⚠️ 如果新的 Result 页不再使用某些组件，可以后续删除

