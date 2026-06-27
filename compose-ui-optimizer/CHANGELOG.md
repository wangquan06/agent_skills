# Changelog

## [1.14.0] - 2026-06-19
### Changed
- 新增「核心理念」章节，解释规则背后的 WHY（sealed interface、Screen/Content 分层、SharedFlow replay=0、modifier 参数、UiState val），提升模型泛化能力
- evals/evals.json：新增 eval #16（基线测试），验证 skill 对规范代码不产生误报
- 将「核心理念」独立为顶层章节，保持「执行原则」只含操作规则

## [1.13.0] - 2026-06-19
### Changed
- SKILL.md：删除 frontmatter `version` 字段（Skill 系统不识别，版本管理由 CHANGELOG.md 承担）
- SKILL.md：删除注意事项 §5「修改范围」（内容与 Step 2 完全重复）
- SKILL.md：检查清单标题「每项 10 分」→「各维度满分 10 分」（原描述与实际扣分结构脱节）
- SKILL.md：安全性检查 `!!` 规则标题「用 `?.let`」→「按上下文选择安全处理」（与下方三种细则保持一致）
- SKILL.md：Step 6 描述「grep 原文件与新文件注释对比」→「运行 `validate-comments.py` 对比」（与实际操作一致）
- scripts/validate-comments.py：注释比较改为只对比内容集合（去掉行号），避免代码行数变化导致误报；输出改为列出缺失注释条目
- scripts/validate-comments.py：删除不再使用的 `format_comments` 函数
- scripts/check-self.py：`check_screen_calls` 函数补充变量别名盲区说明，提醒需人工核查
- references/validation-scripts.md：Step 6 补充脚本失败后的处理行为（停止 Step 7-8，补回缺失注释后重新验证）
- evals/evals.json：修正 4 处（id 3/5/8/12）将 `@Immutable` 与 `@Stable` 视为等价/可互换的错误期望。规则明确：裸 `List<T>` 字段应标 `@Stable`，`@Immutable` 仅在配合 `ImmutableList` 时成立。id 5/8 原代码自带的 `@Immutable` 标注实为错误用法，原 eval 期望"保留/不视为问题"，已改为期望模型识别并修正该错误
- references/api-compatibility.md：修正 Compose Lifecycle 章节中自相矛盾的示例。原内容声称 commonMain 下 Compose 2.x 用 `by` 委托读取 `collectAsStateWithLifecycle()` 会编译错误，与官方文档及多个真实项目示例不符（均统一用 `by`），已修正为正确用法
- scripts/validate-comments.py：删除未使用的 `import re`（已改用手写字符遍历替代正则）
- scripts/check-self.py：删除 `check_visibility` 中未被使用的 `full_line` 赋值（死代码）

## [1.12.0] - 2026-06-18
### Changed
- `scripts/validate-comments.sh` → `scripts/validate-comments.py`：重写为 Python 脚本，消除 BSD/GNU sed 兼容性问题；精确处理字符串字面量中的 `//` 误判
- `scripts/check-self.sh` → `scripts/check-self.py`：重写为 Python 脚本，消除跨平台兼容性问题；修复 Preview brace 检测逻辑（`@Composable` 空行导致过早退出的 bug）
- `references/output-template.md`：补充完整输出示例，帮助模型理解模板在实际场景中的呈现方式

### Removed
- `scripts/validate-comments.sh`：已由 Python 版本替代
- `scripts/check-self.sh`：已由 Python 版本替代

## [1.11.0] - 2026-06-18
### Added
- evals.json eval #12：输出格式合规性测试，验证输出严格遵循 output-template.md 模板
- evals.json eval #13：大文件处理测试，验证 >500 行文件使用精准 diff 块
- evals.json eval #14：注释保留测试，验证行注释和块注释均被完整保留
- evals.json eval #15：编译验证测试，验证输出包含编译验证相关提示

### Changed
- `scripts/validate-comments.sh`：增强注释提取能力——先删除字符串内容再提取注释，支持块注释（`/* */`），添加 trap 清理临时文件
- `scripts/check-self.sh`：增强假阳性抑制——检查前先删除注释和字符串内容，7.2 过滤 `viewModel::` 方法引用，7.3 用 awk 检查空列表前先删除注释和字符串

### Fixed
- CHANGELOG.md：消除 v1.2.0 与 v1.3.0 的重复条目（v1.2.0 内容合并入 v1.3.0）
- CHANGELOG.md：消除 v1.9.1 中重复的 `### Added` 段落

## [1.10.0] - 2026-06-18
### Changed
- **输出格式**：将内联模板外移到 `references/output-template.md`，SKILL.md 改为按需读取引用，减少上下文占用
- **validation-scripts.md**：Step 6 和 Step 7.1-7.3 的内联 bash 命令替换为调用 `scripts/validate-comments.sh` 和 `scripts/check-self.sh`，减少 shell 拼写错误

### Added
- `scripts/validate-comments.sh`：Step 6 注释核对脚本，接收原文件和新文件参数，输出 diff
- `scripts/check-self.sh`：Step 7 自检套件，合并 7.1（可见性）+ 7.2（事件调用）+ 7.3（Preview 数据检查）

### Fixed
- SKILL.md Compose 组件化：清除 L74-75 `suspend` 回调说明的完全重复行

## [1.9.2] - 2026-06-18
### Fixed
- **Preview 覆盖**：明确"整体 Content Preview"的层级定义——必须针对**顶层无状态 Composable**（接收完整 UiState + onEvent），而非页面内子组件（如仅表单区域）；层级错误等同无 Preview，同扣 -5
- **Compose 组件化 / Screen-Content 分层**：补充说明 Content 层须承载完整页面 UI（标题栏 + 错误提示 + 主内容 + 所有 Dialog），不得将 Dialog 或标题拆散至 Screen 层单独渲染

## [1.9.1] - 2026-06-18
### Fixed
- validation-scripts.md §7.1：预期输出描述去除 `onEvent` 硬编码，改为"唯一公开入口方法（命名不限）"
- validation-scripts.md §7.2：grep 命令修复假阳性——过滤 `viewModel.uiState` / `viewModel.uiEffect` 等合法属性访问；`PUBLIC_METHOD` 变量化，支持 `onEvent`/`onIntent` 等不同命名
- SKILL.md MVI检查清单：`onEvent` 硬编码 → 描述为"唯一公开入口方法（常见 `onEvent`/`onIntent`）"
- SKILL.md Compose检查清单：Screen callback 规则同步去除 `onEvent` 硬编码
- SKILL.md 输出格式：`## 验证清单` → `## 🔁 验证清单`，与 evals.json 期望字符串保持一致

### Added
- evals.json eval #11：监听器生命周期行为变更场景，验证优化后不得删除 unregisterStatusListener 调用
- validation-scripts.md §7.4：行为变更等价性核查新增三类变更场景——副作用变更（监听器注册/注销等）、数据来源变更、控制流变更（含 init 事件路由调整）
- validation-scripts.md §7.5：逻辑变更回归核查——当 7.4 发现行为不等价改动时，强制输出手工回归清单，等待用户确认后才能放行或回滚

### Changed
- 执行原则 `modifier` 规则：`private` Composable **禁止添加** modifier 参数，措辞从"不适用"改为"禁止"
- Step 2 边界判断：共用文件规则升级为"立即暂停，列出文件名与改动原因，等待明确授权"
- 可见性与作用域（通用规则）：明确适用于所有声明（class/fun/val，包括 `@Composable` 函数），移除 Compose 组件化中的冗余 Composable 可见性条目
- 注意事项 #3：补充 modifier 链、副作用、监听器生命周期均属"业务逻辑"保护范围

## [1.8.1] - 2026-06-18
### Changed
- Preview 覆盖规则补充：列表元素依赖编译期资源（`DrawableResource`/`StringResource`）时，须引用真实常量填充，禁止留 `emptyList()`，并在输出中说明引用了哪些常量
- validation-scripts.md §7.3 补充同步说明

## [1.8.0] - 2026-06-18
### Added
- 执行原则（横切规则）：批量改动前逐项确认，附典型误区（`@Stable` 误加、`modifier` 不适用场景）
- 安全性检查 `!!` 替换细化：区分普通函数体 / launch 内 / updateState reducer 内三种场景，禁止把读取移出 reducer 破坏 CAS 原子性边界
- validation-scripts.md §7.4：控制流改动等价性核查（null 处理、try-catch 增减、变量捕获位置变更）
- 编译验证补充 WARNING 基准原则：不得新增 WARNING，不要求清零原有警告
- Compose 组件化补充 suspend 回调转 onEvent 的处理方式
- 可读性新增注释风格规范：语言与原文件一致，禁止装饰性符号
- 可读性新增驼峰命名规则（camelCase），禁止字段小写连写
- Preview 覆盖：多状态 Preview 须用户明确要求后追加，不主动生成
- 注意事项新增第7条：发现 bug/逻辑问题须先通知用户确认，等待确认后再修正

### Changed
- Step 5 改动输出规则：大文件（>500 行）无论改动数量始终用精准 diff，小文件（≤500 行）保持原规则
- validation-scripts.md §7.3：Preview 数据完整性脚本从 `grep -A 5`（仅检查 5 行）改为 `awk` 提取完整 Preview 函数体后检查，修复大型 Preview 函数漏检问题

### Fixed
- 重组性能/@Stable 规则修正：全 `val` 且字段为稳定类型的 `data class` 由编译器自动推断，无需手动标注；含 `List<T>` 时才需手动处理
- data object 判断标准改为「参数无实际业务意义」，而非字面上有无参数
- evals.json id=3：移除"主动补充多状态 Preview"期望，与新规则保持一致
- 移除安全性维度中重复的 "Effect SharedFlow replay=0" 扣分项（已在 MVI 架构维度覆盖）
- template.md §1：修正 UserUiState 错误使用 @Immutable（含 List<T> 应用 @Stable）
- evals.json id=8：将 "@Immutable" 期望改为更准确的"含不稳定字段时才需标注"

## [1.6.0] - 2026-06-17
### Added
- 执行流程 Step 8 编译验证（原 Step 6.5 升级为正式步骤）

### Changed
- version 从 1.5.0 升至 1.6.0

## [1.5.0] - 2026-06-17
### Added
- Preview Anonymous Object stub 原则：val 属性不可用 error("stub")（构造时执行），函数可以用（调用时执行）
- 可读性"保留原始注释"增加条件说明（附着代码未删除则注释不得丢失）
- 可读性"硬编码提取"增加放置位置说明（companion object 内或文件顶层 const val）
- 注意事项"说明取舍"增加第二个示例（引入 Intent 增加代码量但改善可测试性）

### Changed
- description 从 7 行压缩至 3 行
- 执行流程 Step 2 边界判断合并为单行
- 输出格式精简：去掉 emoji 图标、合并完整 10 维度表格为单行
- 注意事项 #7 Preview 数据完整性移入检查清单（消除重复）
- 注意事项 #9 保留注释移入可读性检查项（消除重复）

### Removed
- 输出格式中的 emoji 图标（🔍📊⚠️✅🔁📝）和完整 10 维度表格模板

## [1.4.0] - 2026-06-16
### Added
- Step 3 要求记录违规的具体文件:行号+代码片段（生成证据链，避免打勾了事）
- Step 7 自我验证扩展：grep 命令核查 ViewModel 所有 public 方法 + Screen 层 callback 逐行审查
- Compose 组件化新项：Screen 通过 onEvent 交互，不直接调 ViewModel public 方法（-4）
- MVI 第6项违规说明增加 grep 检查指引

### Changed
- MVI 第6项惩罚从 -3 升至 -5

## [1.3.0] - 2026-06-16
### Changed
- SKILL.md 从 ~258 行精简至 ~147 行，消除冗余描述
- 输出格式从 ~80 行压缩到 ~20 行，去除冗余 diff 代码块

### Added
- Effect 要求 `sealed interface`（MVI 架构检查）
- Event/Effect 未使用参数→`data object` 简化检查
- 死代码（无读取字段）检测
- Screen→Content→Preview 流程固化（依赖 ViewModel 时先提 Content）
- Step 7 自检包含新增代码的参数完整性验证

### Fixed
- `!!` 警告附带 `?.let` 替代写法
- 边界判断补回：用户只要建议→跳过 Step 5、代码已达标→输出"代码质量良好"

## [1.1.0] - 2026-06-16
### Changed
- Step 5: 从"完整输出代码"改为"输出改动 diff"，节省 token
- Preview 检查: 从"强制四状态 + 子组件"改为"至少 1 个整体 Preview"
- 注意事项第2条: 从"完整输出代码"改为"省 token 输出"
- 可读性检查: 从"关键逻辑有注释，无冗余注释"改为"保留原始注释"

### Added
- Step 6.5: 编译验证环节（可选）
- 注意事项: 签名变更安全原则、保留原始注释原则、硬编码→常量提取原则
- 可读性检查: 硬编码→常量提取
- MVI 架构检查: ViewModel 唯一公开方法应为 onIntent()、init 块通过 Intent 触发加载、Screen 层 LaunchedEffect 收集 Effect
- 可见性与作用域: 方法可见性最小化（含 MVI ViewModel 场景）
- CHANGELOG.md: 版本管理

## [1.0.0] - 2026-06-16
### Added
- 初始版本: Kotlin + Compose MVI 代码优化与审查 skill
