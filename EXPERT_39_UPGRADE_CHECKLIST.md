# €39 专家版升级功能完成度检查清单

## ✅ 1. 前端升级入口

### 1.1 升级卡片（付费内容区域内）
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 713-734 行
- ✅ **显示条件**: `unlockedTier === "basic_15"`
- ✅ **按钮行为**: `onClick={() => handleUnlockConfirm("expert_39")}`
- ✅ **状态**: 已实现

### 1.2 底部固定 CTA
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 1152-1164 行
- ✅ **显示条件**: `unlockedTier === "basic_15" && isUnlocked`
- ✅ **按钮行为**: `onClick={() => handleUnlockConfirm("expert_39")}`
- ✅ **状态**: 已实现

### 1.3 已解锁专家版提示
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 857-864 行
- ✅ **显示条件**: `unlockedTier === "expert_39"`
- ✅ **状态**: 已实现

## ✅ 2. 支付流程

### 2.1 前端支付调用
- ✅ **函数**: `handleUnlockConfirm("expert_39")`
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 474-516 行
- ✅ **参数**: `tier: "expert_39"`, `assessment_id`, `user_id`
- ✅ **状态**: 已实现

### 2.2 后端创建 Checkout Session
- ✅ **端点**: `POST /api/v1/stripe/create-checkout-session`
- ✅ **位置**: `apps/api/app/api/v1/routes/stripe.py` 第 29-68 行
- ✅ **金额设置**: `amount = 3900` (€39)
- ✅ **Tier 标准化**: `normalize_tier("expert_39")` → `"expert_39"`
- ✅ **Metadata**: `tier: "expert_39"` 正确写入
- ✅ **状态**: 已实现

### 2.3 Stripe Service
- ✅ **函数**: `create_checkout_session`
- ✅ **位置**: `apps/api/app/services/stripe_service.py` 第 26-142 行
- ✅ **金额映射**: `tier == "expert_39"` → `amount = 3900`
- ✅ **Price ID**: `STRIPE_PRICE_EXPERT_39`
- ✅ **状态**: 已实现

## ✅ 3. Webhook 处理

### 3.1 Webhook 端点
- ✅ **端点**: `POST /api/v1/stripe/webhook`
- ✅ **位置**: `apps/api/app/api/v1/routes/stripe.py` 第 71-220 行
- ✅ **Tier 读取**: 从 `metadata.tier` 读取并标准化
- ✅ **升级逻辑**: `tier_rank(new_tier) > tier_rank(old_tier)` 只升级不降级
- ✅ **数据库更新**: `assessment.unlocked_tier = "expert_39"`
- ✅ **状态**: 已实现

### 3.2 升级保护
- ✅ **函数**: `tier_rank` (第 114-116 行)
- ✅ **逻辑**: `{"none": 0, "basic_15": 1, "expert_39": 2}`
- ✅ **行为**: 支持从 `basic_15` → `expert_39` 升级
- ✅ **状态**: 已实现

## ✅ 4. 支付成功处理

### 4.1 支付成功页面
- ✅ **页面**: `apps/web/app/payment/success/page.tsx`
- ✅ **验证接口**: `GET /api/v1/payment/status?session_id=xxx`
- ✅ **Tier 标准化**: `normalizeTier(unlocked_tier)`
- ✅ **刷新结果**: `POST /api/v1/compliance/assess?assessment_id=xxx`
- ✅ **状态**: 已实现

### 4.2 兜底解锁逻辑
- ✅ **端点**: `GET /api/v1/payment/status`
- ✅ **位置**: `apps/api/app/api/v1/routes/payment.py` 第 84-147 行
- ✅ **修复**: 已修复 tier 标准化失败时的 fallback 逻辑
- ✅ **升级保护**: 使用 `tier_rank` 确保只升级不降级
- ✅ **状态**: 已实现并修复

## ✅ 5. 专家包内容生成

### 5.1 Expert Pack 生成
- ✅ **函数**: `_expert_pack`
- ✅ **位置**: `apps/api/app/services/decision_engine.py` 第 75-135 行
- ✅ **触发条件**: `unlocked_tier == "expert_39"`
- ✅ **包含内容**:
  - ✅ `score_breakdown` (分数构成)
  - ✅ `enforcement_path` (执法路径)
  - ✅ `risk_groups` (风险分组)
  - ✅ `roadmap_30d` (30天路线图)
  - ✅ `documents_pack` (材料清单)
  - ✅ `self_audit_checklist` (自检表)
- ✅ **状态**: 已实现

### 5.2 Score Breakdown
- ✅ **来源**: `meta.score_breakdown` (从 `risk_engine.py` 传入)
- ✅ **位置**: `apps/api/app/services/risk_engine.py` 第 1217-1234 行
- ✅ **包含**: `industry_base`, `signals`, `income`, `employee`, `pos`, `deductions`
- ✅ **状态**: 已实现

### 5.3 Enforcement Path
- ✅ **位置**: `apps/api/app/services/decision_engine.py` 第 90-107 行
- ✅ **结构**: 3 步执法路径（信号识别 → 补申报 → 行政处罚）
- ✅ **状态**: 已实现

## ✅ 6. 前端内容显示

### 6.1 专家包展示
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 867-1010 行
- ✅ **显示条件**: `unlockedTier === "expert_39" && decision.expert_pack`
- ✅ **模块展示**:
  - ✅ ① 分数构成 (`score_breakdown`)
  - ✅ ② 执法路径 (`enforcement_path`)
  - ✅ ③ 30天路线图 (`roadmap_30d`)
  - ✅ ④ 材料清单 (`documents_pack`)
  - ✅ 自检表 (`self_audit_checklist`)
- ✅ **状态**: 已实现

### 6.2 TypeScript 类型定义
- ✅ **位置**: `apps/web/app/assessment/result/page.tsx` 第 163-178 行
- ✅ **字段**: `confidence_reason`, `expert_pack.score_breakdown`, `expert_pack.enforcement_path`
- ✅ **状态**: 已实现

## ⚠️ 7. BottomSheet Tier 选择器（可选功能）

### 7.1 当前状态
- ⚠️ **状态**: `selectedTier` 状态已定义但未使用
- ⚠️ **UI**: BottomSheet 中没有 tier 选择器（两个选项按钮）
- ⚠️ **行为**: 直接使用 `paySheetTier`，通过外部按钮设置

### 7.2 建议
- 当前实现：通过外部按钮（升级卡片、底部 CTA）直接调用 `handleUnlockConfirm("expert_39")`，无需在 BottomSheet 中选择
- 这是**更简洁的实现方式**，符合当前需求
- 如果需要，可以添加 BottomSheet 内的 tier 选择器，但当前实现已足够

## ✅ 8. 数据库模型

### 8.1 Assessment 模型
- ✅ **字段**: `unlocked_tier` (String, default="none")
- ✅ **位置**: `apps/api/app/models.py` 第 11-28 行
- ✅ **支持值**: `"none"`, `"basic_15"`, `"expert_39"`
- ✅ **状态**: 已实现

### 8.2 PaymentSession 模型
- ✅ **字段**: `tier` (String, nullable=False)
- ✅ **位置**: `apps/api/app/models.py` 第 31-50 行
- ✅ **状态**: 已实现

## ✅ 9. Schema 定义

### 9.1 ExpertPack Schema
- ✅ **位置**: `apps/api/app/schemas/assessment.py` 第 24-30 行
- ✅ **新增字段**: `score_breakdown`, `enforcement_path`
- ✅ **状态**: 已实现

### 9.2 DecisionSummary Schema
- ✅ **位置**: `apps/api/app/schemas/assessment.py` 第 41-63 行
- ✅ **新增字段**: `confidence_reason`
- ✅ **状态**: 已实现

## 📊 总结

### ✅ 已完成的功能
1. ✅ 前端升级入口（卡片 + 底部 CTA）
2. ✅ 支付流程（前端 → Stripe → Webhook）
3. ✅ 数据库更新（支持升级逻辑）
4. ✅ 专家包内容生成（包含所有新字段）
5. ✅ 前端内容展示（完整的专家包 UI）
6. ✅ 类型定义（TypeScript + Pydantic）
7. ✅ 兜底解锁逻辑（已修复）

### ⚠️ 可选功能
- BottomSheet 内的 tier 选择器（当前通过外部按钮直接调用，已足够）

### 🎯 结论
**€39 专家版升级功能已全部完成！** ✅

所有核心功能都已实现，包括：
- 升级入口
- 支付流程
- 内容生成
- 内容显示
- 升级保护

当前实现方式简洁高效，无需额外修改。

