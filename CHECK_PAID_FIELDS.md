# 检查 decision_summary 付费区字段

## 📋 付费区字段定义

根据 Schema 定义，付费区字段包括：
- `reasons: List[str]` - 判断依据（付费墙控制）
- `recommended_actions: List[str]` - 可执行行动清单（付费墙控制）
- `risk_if_ignore: List[str]` - 如果忽视，可能会发生（付费墙控制）
- `expert_pack: Optional[ExpertPack]` - €39 专家版内容

## 🔍 问题发现

### 1. 后端逻辑（decision_engine.py）

当 `unlocked_tier == "none"` 时，这些字段会被清空：

```python
# 根据 unlocked_tier 决定是否返回付费内容
if unlocked_tier == "none":
    reasons = []
    actions = []
    risks_ignore = []
    expert_pack = None
elif unlocked_tier == "basic_15":
    expert_pack = None
else:  # expert_39
    expert_pack = _expert_pack(stage, industry, decision_level, meta)
```

**问题**：即使字段存在，但如果 `get_actions()` 返回空列表，`recommended_actions` 也会是空的。

### 2. 前端显示逻辑（result/page.tsx）

前端使用了可选链 `?.`，所以空数组不会报错，但会显示空白：

```typescript
{decision.reasons?.slice(0, 3).map((r, idx) => (
  <li key={idx}>{r}</li>
))}
```

**如果 `reasons` 是空数组 `[]`**：
- `decision.reasons?.slice(0, 3)` 返回 `[]`
- `[].map(...)` 返回 `[]`
- 结果：显示空的 `<ul>`，没有内容

## ⚠️ 潜在问题

1. **如果 `get_actions()` 没有找到模板**，会返回空列表
2. **即使解锁了，如果后端没有正确设置 `unlocked_tier`**，字段仍然是空的
3. **前端没有处理空数组的情况**，会显示空的卡片

## ✅ 建议修复

### 方案 1：前端添加空数组检查（推荐）

在显示付费内容前，检查字段是否有内容：

```typescript
{/* €15 内容：原因 / 行动清单 / 忽视风险 */}
{decision.reasons && decision.reasons.length > 0 && (
  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
    <div className="font-semibold">判断依据（简明）</div>
    <ul className="mt-3 list-disc pl-5 space-y-2 text-sm text-white/80">
      {decision.reasons.slice(0, 3).map((r, idx) => (
        <li key={idx}>{r}</li>
      ))}
    </ul>
  </div>
)}

{decision.recommended_actions && decision.recommended_actions.length > 0 && (
  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
    <div className="font-semibold">可执行行动清单（建议按顺序做）</div>
    {/* ... */}
  </div>
)}

{decision.risk_if_ignore && decision.risk_if_ignore.length > 0 && (
  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
    <div className="font-semibold">如果忽视，可能会发生</div>
    {/* ... */}
  </div>
)}
```

### 方案 2：后端确保字段不为空

检查 `get_actions()` 是否总是返回非空列表，如果没有模板，返回默认值。

