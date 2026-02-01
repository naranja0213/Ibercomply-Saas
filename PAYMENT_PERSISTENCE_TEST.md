# 支付状态持久化测试说明

## 测试场景

**用户评估后付费 €39，然后退出网站重新进入，是否需要再付费才能看到结果？**

## 预期行为

**✅ 不应该需要再付费** - 支付状态应该持久保存在数据库中。

## 系统工作原理

### 1. 支付成功后（payment/success 页面）

1. 调用 `/api/v1/payment/status?session_id=xxx` 验证支付
2. **后端自动更新数据库**（`payment.py` 第117-149行）：
   ```python
   # ✅ 兜底解锁：paid=true 但 unlocked_tier 还是 none/空，就立刻写入
   assessment.unlocked_tier = "expert_39"  # 根据 payment_session.tier
   assessment.unlocked_at = datetime.utcnow()
   db.commit()
   ```
3. **前端保存状态**（`payment/success/page.tsx` 第84-96行）：
   ```typescript
   // 保存到 localStorage 和 sessionStorage
   sessionStorage.setItem("assessment_id", assessmentId);
   localStorage.setItem("assessment_id", assessmentId);
   const tierKey = `assessment_unlocked_tier:${assessmentId}`;
   sessionStorage.setItem(tierKey, "expert_39");
   localStorage.setItem(tierKey, "expert_39");
   ```
4. 跳转回结果页：`/assessment/result?assessment_id=xxx`

### 2. 重新访问结果页时（result/page.tsx 第304-345行）

1. **从 URL 或存储获取 assessment_id**
2. **从数据库获取权威的 unlocked_tier**（第307-317行）：
   ```typescript
   // 调用 GET /api/v1/compliance/assessments/{assessment_id}
   const a = await r.json();
   const tier = normalizeTier(a.unlocked_tier);  // 从数据库读取
   setUnlockedTier(tier);
   ```
3. **重新请求完整结果**（第336-345行）：
   ```typescript
   // POST /api/v1/compliance/assess?assessment_id=xxx
   // 后端会从数据库读取最新的 unlocked_tier 并返回完整内容
   ```

### 3. 后端验证逻辑（compliance.py 第44-50行）

```python
# ✅ 优先：如果提供了 assessment_id，从数据库获取最新的 unlocked_tier（权威来源）
if assessment_id:
    assessment_db = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    if assessment_db:
        unlocked_tier_value = normalize_tier(assessment_db.unlocked_tier)
```

## 测试步骤

### 准备：确保数据库表存在

```bash
# 检查数据库
docker-compose exec api python -c "
from app.database import engine, Base
from app.models import Assessment, PaymentSession
Base.metadata.create_all(bind=engine)
print('✅ 数据库表已创建')
"
```

### 测试流程

1. **首次评估**
   - 访问 http://localhost:3001/assessment/start
   - 填写评估表单并提交
   - 记录 `assessment_id`（浏览器控制台或 Network 面板）

2. **付费 €39**
   - 在结果页点击"解锁完整分析 €39"
   - 完成 Stripe 支付（测试卡号：4242 4242 4242 4242）
   - 等待支付成功页面跳转回结果页
   - **验证**：应该能看到完整的专家版内容（reasons, actions, risk_if_ignore, expert_pack）

3. **清除浏览器状态（模拟退出网站）**
   - 打开浏览器开发者工具
   - Application → Storage → Clear site data
   - 或者手动清除：
     - Application → Local Storage → Clear All
     - Application → Session Storage → Clear All
   - 关闭浏览器标签页

4. **重新访问（模拟重新进入）**
   - 打开新标签页
   - 访问：`http://localhost:3001/assessment/result?assessment_id={之前记录的assessment_id}`
   - **验证点**：
     - ✅ 页面应该自动加载评估结果
     - ✅ 应该能看到完整的专家版内容（不需要再付费）
     - ✅ 不应该显示"解锁完整分析"按钮

### 调试检查

如果重新访问时仍显示需要付费，检查：

1. **数据库中的状态**
   ```bash
   docker-compose exec api python -c "
   from app.database import SessionLocal
   from app.models import Assessment
   db = SessionLocal()
   # 替换为实际的 assessment_id
   assessment = db.query(Assessment).filter(
       Assessment.assessment_id == '你的assessment_id'
   ).first()
   if assessment:
       print(f'Assessment ID: {assessment.assessment_id}')
       print(f'Unlocked Tier: {assessment.unlocked_tier}')
       print(f'Unlocked At: {assessment.unlocked_at}')
       print(f'Stripe Session ID: {assessment.stripe_session_id}')
   else:
       print('Assessment not found')
   db.close()
   "
   ```

2. **浏览器控制台日志**
   - 打开开发者工具 → Console
   - 查看是否有错误信息
   - 查看 `unlockedTier` 的值

3. **Network 请求**
   - 打开开发者工具 → Network
   - 检查 `GET /api/v1/compliance/assessments/{assessment_id}` 的响应
   - 检查 `POST /api/v1/compliance/assess?assessment_id=xxx` 的请求和响应

## 可能的问题

### 问题1：数据库未创建表

**症状**：重新访问时找不到 assessment

**解决**：
```bash
docker-compose exec api python -c "
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
"
```

### 问题2：支付状态未更新到数据库

**症状**：数据库中的 `unlocked_tier` 仍然是 "none"

**检查**：
- 查看 `/api/v1/payment/status` 端点日志
- 确认支付是否真的成功（Stripe Dashboard）

### 问题3：assessment_id 不匹配

**症状**：重新访问时找不到对应的 assessment

**检查**：
- 确认 URL 中的 `assessment_id` 是否正确
- 确认数据库中的 `assessment_id` 是否匹配

## 预期结果

✅ **用户不需要再付费** - 系统通过以下机制保证：

1. ✅ **数据库持久化**：支付状态保存在 `assessments` 表的 `unlocked_tier` 字段
2. ✅ **权威验证**：前端通过 `GET /api/v1/compliance/assessments/{assessment_id}` 从数据库获取最新状态
3. ✅ **自动解锁**：后端在支付成功时自动更新数据库（无需 webhook）
4. ✅ **URL 参数传递**：`assessment_id` 通过 URL 参数传递，即使清除存储也能访问

