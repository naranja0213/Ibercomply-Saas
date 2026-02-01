# Debug 信息查看位置

## 📍 位置

Debug 信息显示在 **Result 页（/assessment/result）的顶部**。

## 🔍 查看方式

1. **访问 Result 页**：
   - 完成评估后会自动跳转到 Result 页
   - 或直接访问：http://localhost:3001/assessment/result

2. **找到 Debug 信息框**：
   - 在页面最顶部（标题和摘要卡片之前）
   - 是一个灰色/黑色的信息框（`bg-black/30`）
   - 使用等宽字体显示（`whitespace-pre-wrap`）

3. **显示条件**：
   - 只有在**开发环境**（`NODE_ENV === "development"`）才会显示
   - 生产环境不会显示此信息

## 📋 Debug 信息内容

Debug 信息框会显示以下内容：

```
requiredTier: basic_15 | expert_39 | none
unlockedTier(state): basic_15 | expert_39 | none
sessionStorage: basic_15 | expert_39 | none
localStorage: basic_15 | expert_39 | none
decision_code: REGISTER_AUTONOMO | RISK_AUTONOMO | ...
assessment_id: assessment_xxx...
isUnlocked: true | false
paid_reasons_len: 3 | 0
paid_actions_len: 5 | 0
paid_ignore_len: 2 | 0
```

## 🎯 如何判断问题

### 情况 1：解锁状态正常，但内容为空
```
isUnlocked: true
paid_reasons_len: 0
paid_actions_len: 0
paid_ignore_len: 0
```
**原因**：Success 页没有正确重新获取 assessment_result，或者后端返回了空数组。

### 情况 2：解锁状态为 false
```
isUnlocked: false
unlockedTier(state): none
sessionStorage: none
```
**原因**：解锁状态没有正确保存到 sessionStorage，或 Success 页没有正确处理。

### 情况 3：解锁状态正常，内容也有数据
```
isUnlocked: true
paid_reasons_len: 3
paid_actions_len: 5
paid_ignore_len: 2
```
**正常**：应该能看到付费内容了。

## 💡 如果看不到 Debug 信息

如果看不到 debug 信息框，可能的原因：

1. **不是开发环境**：
   - 检查 `NODE_ENV` 环境变量
   - 开发环境应该是 `development`

2. **还没有访问 Result 页**：
   - 需要先完成评估或访问 `/assessment/result`

3. **浏览器缓存**：
   - 尝试硬刷新（Ctrl+Shift+R 或 Cmd+Shift+R）
   - 或清除缓存

