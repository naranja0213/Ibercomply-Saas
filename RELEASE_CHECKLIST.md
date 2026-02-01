# 发布前检查清单

## 回归测试（必执行）

**⚠️ 重要：每次发版前必须执行以下测试项**

参考 `REGRESSION_TEST_CHECKLIST.md` 的详细测试步骤。

### 快速检查清单（5分钟版本）

- [ ] **测试 1**：`created_at = null` 时后端不报错，前端不显示复评卡片
- [ ] **测试 2**：`prefill_stage` 异常值（INVALID、空字符串、SQL注入尝试）不跳转、不报错
- [ ] **测试 3**：跨日边界版本号一致性（PDF 版本号与 `created_at` UTC 日期一致）
- [ ] **测试 4**：无效 `assessment_id` 显示友好错误页（不白屏、不报错）
- [ ] **测试 5**：支付完成但 webhook 延迟时，兜底逻辑能自动解锁

### 执行时机

1. **代码审查后、部署前**：执行所有回归测试
2. **测试结果记录**：在 GitHub Issue 或 Release Notes 中记录测试结果
3. **失败处理**：任何测试项失败，必须修复后才能发布

---

## 日志检查

检查日志中是否记录了以下关键操作：

- `[ASSESSMENT_GET]` - assessment_id 和 unlocked_tier
- `[PDF_GENERATE]` - PDF 生成成功/失败

**日志格式示例**：
```
[ASSESSMENT_GET] assessment_id=assessment_xxx, unlocked_tier=expert_39
[PDF_GENERATE] assessment_id=assessment_xxx, unlocked_tier=expert_39, success=true
```

---

## 功能验证

- [ ] 复评提示功能（超过30天显示提示）
- [ ] 支付问题自救入口（已支付但未解锁时显示）
- [ ] 友好错误页（无效 assessment_id）
- [ ] 支付兜底逻辑（webhook 延迟时自动解锁）

---

## 部署检查

- [ ] 环境变量配置正确（Stripe keys、Price IDs）
- [ ] 数据库迁移（如有）
- [ ] 前端构建成功
- [ ] 后端服务启动成功
- [ ] API 健康检查通过

