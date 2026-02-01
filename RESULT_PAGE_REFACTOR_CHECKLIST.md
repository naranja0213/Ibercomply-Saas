# Result 页重构检查清单

## ✅ 检查结果

### 🔴 问题 1: 前端仍在做业务判断

**文件**: `apps/web/app/assessment/result/page.tsx`

**问题位置**:
- 第 195 行：`shouldShowUnlock` 在前端判断是否需要显示解锁按钮
  ```typescript
  const shouldShowUnlock = result && ["REGISTER_AUTONOMO", "STRONG_REGISTER", "CONSIDER_SL"].includes(result.decision_summary.level);
  ```
  **❌ 错误**：前端不应该根据 `decision_summary.level` 来判断是否显示付费墙

- 第 256-292 行：`filterFindingsForDecision` 函数在修改 findings 的文案
  ```typescript
  const filterFindingsForDecision = (findings: Finding[]): Finding[] => {
    if (result.decision_summary.level === "CONSIDER_SL") {
      // 替换文案...
    }
  }
  ```
  **❌ 错误**：前端不应该修改后端返回的数据，所有文案应该在 Risk Engine 中已经是正确的

### 🔴 问题 2: 后端 Schema 缺少关键字段

**文件**: `apps/api/app/schemas/assessment.py`

**问题**：`DecisionSummary` schema 缺少以下字段：
- `paywall: Literal["none", "basic_15", "expert_39"]` - 用于前端判断是否需要付费墙
- `top_risks: List[Finding]` - 用于前端显示 Top 3 风险（免费部分）
- `pay_reason: Optional[str]` - 用于解释为什么需要付费

### 🔴 问题 3: 后端 Decision Engine 计算了但未返回

**文件**: `apps/api/app/services/decision_engine.py`

**问题**：
- 第 115 行：计算了 `top3_findings = _top_risks(findings)`
- 但在返回 `DecisionSummarySchema` 时（第 160、219、276 行）**没有包含 `top_risks` 字段**

### 🟡 问题 4: 表单提交缺少 unlocked_tier

**文件**: `apps/web/app/assessment/form/page.tsx`

**问题**：第 85-94 行保存结果时，没有保存 `assessment_unlocked_tier` 到 sessionStorage
- ✅ 已保存 `assessment_result`
- ✅ 已保存 `assessment_input`
- ❌ 缺少 `assessment_unlocked_tier: "none"`

---

## ✅ 修复步骤（按优先级）

### 🔴 优先级 1: 修复后端 Schema 和 Decision Engine

#### 步骤 1.1: 更新 `DecisionSummary` Schema

**文件**: `apps/api/app/schemas/assessment.py`

**改动**：
```python
class DecisionSummary(BaseModel):
    level: Literal[...]  # 保持不变
    decision_intent: Literal[...]  # 保持不变
    title: str  # 保持不变
    conclusion: str  # 保持不变
    confidence_level: Literal[...]  # 保持不变
    next_review_window: str  # 保持不变
    paywall: Literal["none", "basic_15", "expert_39"]  # ✅ 新增
    pay_reason: Optional[str] = None  # ✅ 新增
    top_risks: List[Finding] = Field(default_factory=list)  # ✅ 新增
    reasons: List[str]  # 保持不变
    recommended_actions: List[str]  # 保持不变
    risk_if_ignore: List[str]  # 保持不变
    expert_pack: Optional[ExpertPack] = None  # 保持不变
    pro_brief: Optional[ProBrief] = None  # 保持不变
```

#### 步骤 1.2: 更新 `compute_decision_summary` 函数

**文件**: `apps/api/app/services/decision_engine.py`

**改动点**：

1. **在 PRE_AUTONOMO 分支**（约第 160 行）：
```python
# 计算 paywall（根据 decision_level）
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
    top_risks=top3_findings,  # ✅ 新增（已计算）
    reasons=reasons,
    recommended_actions=actions,
    risk_if_ignore=risks_ignore,
    expert_pack=expert_pack,
    pro_brief=ProBrief(...),
)
```

2. **在 AUTONOMO 分支**（约第 219 行）：
```python
# 计算 paywall
if decision_level == "CONSIDER_SL":
    paywall = "basic_15"
    pay_reason = "解锁后可查看详细原因、行动清单和忽略风险后果"
elif decision_level == "RISK_AUTONOMO":
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

3. **在 SL 分支**（约第 276 行）：
```python
# 计算 paywall
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

### 🔴 优先级 2: 替换 Result 页（完全按模板）

#### 步骤 2.1: 替换 `result/page.tsx`

**文件**: `apps/web/app/assessment/result/page.tsx`

**操作**：**完全替换**为用户提供的模板代码

**关键改动点**：
1. ✅ 使用 `decision_summary.paywall` 判断是否需要付费墙（不再用 `level` 判断）
2. ✅ 使用 `decision_summary.top_risks` 显示 Top 3 风险（不再自己过滤）
3. ✅ 移除 `filterFindingsForDecision` 函数（不再修改后端数据）
4. ✅ 移除 `shouldShowUnlock` 的业务判断（完全依赖后端 `paywall`）
5. ✅ 解锁状态使用 `sessionStorage.getItem("assessment_unlocked_tier")`
6. ✅ 支付成功后更新 `sessionStorage.setItem("assessment_unlocked_tier", newTier)`

### 🟡 优先级 3: 修复表单提交

#### 步骤 3.1: 在表单提交时保存 `assessment_unlocked_tier`

**文件**: `apps/web/app/assessment/form/page.tsx`

**改动位置**：第 85-94 行

**改动前**：
```typescript
sessionStorage.setItem("assessment_result", JSON.stringify(data));
sessionStorage.setItem("assessment_input", JSON.stringify({...}));
router.push("/assessment/result");
```

**改动后**：
```typescript
sessionStorage.setItem("assessment_result", JSON.stringify(data));
sessionStorage.setItem("assessment_input", JSON.stringify({...}));
sessionStorage.setItem("assessment_unlocked_tier", "none");  // ✅ 新增
router.push("/assessment/result");
```

## ✅ 验证清单

修复后，请验证：

- [ ] 后端 `/api/v1/compliance/assess` 返回的 `decision_summary` 包含 `paywall` 字段
- [ ] 后端 `/api/v1/compliance/assess` 返回的 `decision_summary` 包含 `top_risks` 字段（List[Finding]）
- [ ] 后端 `/api/v1/compliance/assess` 返回的 `decision_summary` 包含 `pay_reason` 字段（可选）
- [ ] 前端 Result 页不再使用 `shouldShowUnlock` 的业务判断
- [ ] 前端 Result 页使用 `decision_summary.paywall` 判断是否显示付费墙
- [ ] 前端 Result 页使用 `decision_summary.top_risks` 显示 Top 3 风险
- [ ] 前端 Result 页不再有 `filterFindingsForDecision` 函数
- [ ] 表单提交后，`sessionStorage` 中有 `assessment_unlocked_tier: "none"`
- [ ] 支付成功后，`sessionStorage` 中更新 `assessment_unlocked_tier` 为 `"basic_15"` 或 `"expert_39"`
- [ ] 解锁后，付费内容正确显示（reasons、recommended_actions、risk_if_ignore）

---

## 📝 注意事项

1. **不要在前端做业务判断**：所有"是否需要付费墙"的判断都应由后端 `paywall` 字段决定

2. **不要修改后端数据**：前端只负责渲染，不修改 findings 或其他后端返回的数据

3. **保持向后兼容**：如果前端还有其他地方使用旧的 Result 页组件，需要先确认并更新

4. **测试支付流程**：修复后需要完整测试支付流程，确保解锁状态正确保存和读取

