# 显示解锁内容的代码位置

## 📍 文件位置

**文件**: `apps/web/app/assessment/result/page.tsx`

## 🔑 关键代码位置

### 1. 解锁状态判断逻辑

**位置**: 第 147-153 行

```typescript
// 3) 当前是否已经解锁了足够层级
const isUnlocked = useMemo(() => {
  if (!decision) return false;
  if (requiredTier === "none") return true;
  if (requiredTier === "basic_15") return unlockedTier === "basic_15" || unlockedTier === "expert_39";
  if (requiredTier === "expert_39") return unlockedTier === "expert_39";
  return false;
}, [decision, requiredTier, unlockedTier]);
```

**作用**: 判断用户是否已经解锁了足够的内容层级

### 2. 付费墙显示逻辑（未解锁时）

**位置**: 第 269-296 行

```typescript
{/* 付费墙：仅当 requiredTier != none 且未解锁 */}
{requiredTier !== "none" && !isUnlocked && pay && (
  <div className="mt-6 rounded-2xl border border-white/10 bg-gradient-to-b from-white/10 to-white/5 p-5">
    {/* 显示解锁按钮和说明 */}
  </div>
)}
```

**作用**: 当需要付费且未解锁时，显示付费墙和"解锁 €15"按钮

### 3. 解锁内容显示区域（核心）

**位置**: 第 298-400 行

```typescript
{/* 付费内容（解锁后展示） */}
<div id="paid-section" className="mt-6 space-y-4">
  {(requiredTier === "none" || isUnlocked) && (
    <>
      {/* €15 内容：原因 / 行动清单 / 忽视风险 */}
      
      {/* 1. 判断依据（reasons） */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="font-semibold">判断依据（简明）</div>
        <ul className="mt-3 list-disc pl-5 space-y-2 text-sm text-white/80">
          {decision.reasons?.slice(0, 3).map((r, idx) => (
            <li key={idx}>{r}</li>
          ))}
        </ul>
      </div>

      {/* 2. 可执行行动清单（recommended_actions） */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="font-semibold">可执行行动清单（建议按顺序做）</div>
        <div className="mt-3 space-y-2">
          {decision.recommended_actions?.map((a, idx) => (
            <label key={idx} className="flex gap-3 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white/85">
              <input type="checkbox" className="mt-0.5" />
              <span className="leading-relaxed">{a}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 3. 如果忽视，可能会发生（risk_if_ignore） */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="font-semibold">如果忽视，可能会发生</div>
        <ul className="mt-3 list-disc pl-5 space-y-2 text-sm text-white/80">
          {decision.risk_if_ignore?.slice(0, 3).map((r, idx) => (
            <li key={idx}>{r}</li>
          ))}
        </ul>
      </div>

      {/* 4. €39 专家包（只有 expert_39 解锁才展示） */}
      {unlockedTier === "expert_39" && decision.expert_pack && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          {/* 专家包内容：风险分组、30天计划、材料清单、自检表 */}
        </div>
      )}
    </>
  )}
</div>
```

**关键条件**: `(requiredTier === "none" || isUnlocked)`

**作用**: 
- 如果 `requiredTier === "none"`（不需要付费），直接显示
- 如果 `isUnlocked === true`（已解锁），显示所有付费内容
- 否则不显示（隐藏）

### 4. Findings 中的 pro_only 隐藏逻辑

**位置**: 第 414-442 行

```typescript
{data.findings.map((f, idx) => {
  const hiddenProOnly = !!f.pro_only && unlockedTier === "none" && requiredTier !== "none";
  return (
    <details>
      {/* ... */}
      <div>
        {hiddenProOnly ? (
          <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-white/75">
            此条为专业细节（解锁后可见）
          </div>
        ) : (
          f.detail
        )}
      </div>
    </details>
  );
})}
```

**作用**: 
- 如果 `f.pro_only === true` 且用户未解锁，显示"此条为专业细节（解锁后可见）"
- 否则显示完整的 finding 详情

## 🔍 解锁状态来源

解锁状态来自以下地方：

1. **初始状态**: `sessionStorage.getItem("assessment_unlocked_tier")`（第 122 行）
2. **状态更新**: `setUnlockedTier(rawTier)`（第 132 行）
3. **支付成功**: `/payment/success` 页面会更新 `sessionStorage.setItem("assessment_unlocked_tier", unlocked_tier)`

## 📋 显示内容清单

当 `isUnlocked === true` 或 `requiredTier === "none"` 时，会显示：

1. ✅ **判断依据（reasons）** - 来自 `decision.reasons`
2. ✅ **可执行行动清单（recommended_actions）** - 来自 `decision.recommended_actions`
3. ✅ **如果忽视，可能会发生（risk_if_ignore）** - 来自 `decision.risk_if_ignore`
4. ✅ **专家包内容（expert_pack）** - 只有 `unlockedTier === "expert_39"` 时显示

## 🎯 调试建议

如果解锁后内容没有显示，检查：

1. **sessionStorage 中的 unlocked_tier**:
   ```javascript
   console.log(sessionStorage.getItem("assessment_unlocked_tier"));
   ```

2. **isUnlocked 的值**:
   ```javascript
   console.log("isUnlocked:", isUnlocked);
   console.log("requiredTier:", requiredTier);
   console.log("unlockedTier:", unlockedTier);
   ```

3. **后端返回的 decision_summary**:
   ```javascript
   console.log("decision:", decision);
   console.log("reasons:", decision?.reasons);
   console.log("recommended_actions:", decision?.recommended_actions);
   ```

