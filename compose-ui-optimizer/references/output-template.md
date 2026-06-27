# 输出格式模板

在 Step 4（输出分析）和 Step 5（执行改动）时严格遵循此模板。

## 结构要求

```
## 代码分析
功能说明 2-3 句，不完整时注明假设

## 健康度评估（只列扣分维度）
| 维度 | 得分 | 问题数 | 评级 |
| 扣分维度 | x/10 | n | 🟡/🔴 |
| 总分 | x/100 | | 🟢/🟡/🔴 |
评级：🟢 8-10 ｜ 🟡 5-7 ｜ 🔴 0-4

## 优化建议 N. [维度] 🔴/🟡/🟢  **问题**：位置 | **建议**：方案 | **原因**：为什么

## 改动（列出修改函数/文件，未列出的保持原样）

## 🔁 验证清单（只列未通过项）

## 改动摘要
| 改前 | 改后 | 收益（安全性↑/可读性↑/可测试性↑/重组性能↑）|
|------|------|------|
```
代码合格 → `## 代码质量良好`

---

## 示例（紧凑）

```
## 代码分析
用户列表页。缺少 UiEffect、异常处理不完整、LazyColumn 缺 key。

## 健康度评估
| 维度 | 得分 | 问题数 | 评级 |
|------|------|--------|------|
| MVI 架构 | 6/10 | 1 | 🟡 |
| 错误处理 | 3/10 | 1 | 🔴 |
| 重组性能 | 5/10 | 1 | 🟡 |
| **总分** | **52/100** | 3 | 🔴 |

## 优化建议
1. **[MVI]** 🟡 navController.navigate() 直接在 ViewModel 调用 → 定义 UiEffect 在 Screen 收集 | ViewModel 不应持有 NavController
2. **[错误处理]** 🔴 loadUsers() 缺 try-catch → 包裹，catch 更新 error+isLoading | 否则直接崩溃
3. **[重组性能]** 🟡 LazyColumn items() 缺 key → items(users, key={it.id}) | 无 key 全量重组

## 改动
```diff
// UserViewModel.kt: loadUsers()
+ _uiState.update { it.copy(isLoading = true, error = null) }
+ try { ... } catch (e: Exception) {
+     _uiState.update { it.copy(isLoading = false, error = e.message) }
+ }
// UserScreen.kt: LazyColumn
- items(users) { ... }
+ items(users, key = { it.id }) { ... }
```

## 🔁 验证清单
- [x] loadUsers() 改为 private
- [x] 注释已核对通过

## 改动摘要
| 改前 | 改后 | 收益 |
|------|------|------|
| ViewModel 直接调 navController | UiEffect → Screen 收集 | 安全性↑ 可测试↑ |
| loadUsers 无异常处理 | try-catch + error 状态 | 安全性↑ |
| items 无 key | items(users, key={it.id}) | 重组性能↑ |
```
