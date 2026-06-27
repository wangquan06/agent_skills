# 验证脚本参考

## Step 6: 注释核对

```bash
python3 scripts/validate-comments.py OriginalFile.kt NewFile.kt
```

**要求**：所有注释必须迁移，禁止删除/简化/改写/翻译

**失败处理**：脚本返回非零退出码时，停止执行 Step 7-8，将缺失注释列表输出给用户，补回后重新运行验证通过再继续。

---

## Step 7: 自检验证

### 7.1-7.3 综合检查
```bash
python3 scripts/check-self.py XxxViewModel.kt XxxScreen.kt
```

> 若列表元素依赖编译期资源（`DrawableResource`/`StringResource`），须引用真实常量填充，不得留 `emptyList()`。

---

### 7.4 行为变更等价性核查

改动涉及以下类型时，逐处用一句话声明等价性：
- null 处理调整（`!!` 替换、新增 null 分支）
- 异常捕获增减（新增/删除 `try-catch`）
- 变量捕获位置变更（从 lambda 内移到外）
- **副作用变更**（新增/移除函数调用，包括监听器注册/注销、日志、统计等）
- **数据来源变更**（字段引用替换、API 方法替换、计算逻辑改写）
- **控制流变更**（条件分支重构、`init` 事件路由调整、调用顺序变更）

对每处改动说明：
1. 原始代码在该路径的行为
2. 改后代码在同路径的行为
3. 业务语义是否等价；若不等价，是有意改善还是需用户确认

---

### 7.5 逻辑变更回归核查

**当 7.4 存在任何行为不等价改动时**，须输出手工回归清单（无 UT 时的最后防线）：

```
⚠️ 行为变更 — 手工回归清单
| 改动点 | 测试场景 | 预期行为 |
|--------|---------|---------|
| 示例：移除 unregisterStatusListener | 退出页面后再进入，蓝牙状态回调 | 不再触发旧监听器的 UI 更新 |
```

输出后等待用户确认：
- 业务等价的改动 → 直接放行
- 行为有意变更（修复 bug、优化逻辑）→ 标注说明，由用户确认
- 用户拒绝的改动 → **回滚至原始代码**

---

## Step 8: 编译验证

### KMP 项目
```bash
./gradlew :<module>:compileKotlin<Target>

# 示例
./gradlew :features:home:compileKotlinIosArm64
./gradlew :features:home:compileKotlinAndroid
```

### Android 项目
```bash
./gradlew :<module>:compileDebugKotlin

# 示例
./gradlew :app:compileDebugKotlin
```

### 失败处理策略
- **≤3 次错误**：提取错误信息，回 Step 3 修复
- **>3 次错误**：输出诊断报告（错误类型、可能原因、建议方案），等待用户决策
