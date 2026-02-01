# 需要手动修复：Result 页移除 session_id 处理

## 问题

`apps/web/app/assessment/result/page.tsx` 中还有旧的代码，需要移除 `handlePaymentCallback` 的调用。

## 修复

在 `useEffect` 中，移除以下代码：

```typescript
// 检查 URL 中是否有 session_id（支付成功回调）
const params = new URLSearchParams(window.location.search);
const sessionId = params.get("session_id");

if (sessionId) {
  // 如果有 session_id，验证支付状态并重新获取评估结果
  handlePaymentCallback(sessionId);
} else {
  // 从 sessionStorage 读取评估结果
  // ...
}
```

改为：

```typescript
// 从 sessionStorage 读取评估结果（不再处理 session_id，因为 success 页面已经处理了）
try {
  const raw = sessionStorage.getItem("assessment_result");
  const rawTier = sessionStorage.getItem("assessment_unlocked_tier") as PaywallTier | null;
  // ...
} catch {
  router.replace("/assessment/start");
}
```

原因：现在 `/payment/success` 页面负责处理支付回调，Result 页只需要从 sessionStorage 读取状态即可。

