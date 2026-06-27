# Kotlin + Compose MVI 完整标准模板

> 本文件是完整可运行的参考模板，包含所有层的标准写法。
> 各规则说明在 SKILL.md，此处只提供"标准长什么样"的代码参考。

## 目录
1. State / Intent / Effect
2. ViewModel
3. Koin Module
4. Screen（有状态层）
5. Content（无状态层）
6. 子组件
7. Preview
8. 重组性能优化
9. 可测试性标准写法
10. 可见性与作用域

---

## 1. State / Intent / Effect

```kotlin
// 全 val 且字段均为稳定类型：编译器自动推断，无需标注
data class User(val id: String, val name: String)

// 含 List<T> 等不稳定类型：手动标注 @Stable（弱承诺，不保证 List 内容不变）
// 如需强不可变性，改用 kotlinx.collections.immutable 的 ImmutableList + @Immutable
@Stable
data class UserUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

sealed interface UserUiIntent {
    data object LoadUsers : UserUiIntent
    data class OnUserClick(val userId: String) : UserUiIntent
    data object Refresh : UserUiIntent
}

sealed interface UserUiEffect {
    data class NavigateToDetail(val userId: String) : UserUiEffect
    data class ShowToast(val message: String) : UserUiEffect
}
```

---

## 2. ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    private val _uiEffect = MutableSharedFlow<UserUiEffect>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val uiEffect: SharedFlow<UserUiEffect> = _uiEffect.asSharedFlow()

    init { onEvent(UserUiIntent.LoadUsers) }

    fun onEvent(intent: UserUiIntent) {
        when (intent) {
            is UserUiIntent.LoadUsers   -> loadUsers()
            is UserUiIntent.OnUserClick -> navigateToDetail(intent.userId)
            is UserUiIntent.Refresh     -> loadUsers()
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }  // 新请求：重置 error，防止上次错误残留
            try {
                val users = withContext(Dispatchers.IO) { repository.getUsers() }
                _uiState.update { it.copy(isLoading = false, users = users) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    private fun navigateToDetail(userId: String) {
        viewModelScope.launch {
            _uiEffect.emit(UserUiEffect.NavigateToDetail(userId))
        }
    }
}
```

---

## 3. Koin Module

```kotlin
val userModule = module {
    single<UserRepository> { UserRepositoryImpl(get()) }
    viewModel { UserViewModel(get()) }   // ViewModel 用 viewModel{}，不用 single{}
}

class App : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@App)
            modules(userModule)
        }
    }
}
```

---

## 4. Screen（有状态，❌ 不可 Preview）

```kotlin
@Composable
fun UserScreen(
    onNavigateToDetail: (String) -> Unit,
    viewModel: UserViewModel = koinViewModel()   // DI 唯一入口
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    // Effect 处理：导航/Toast 统一在 Screen 层
    LaunchedEffect(Unit) {
        viewModel.uiEffect.collect { effect ->
            when (effect) {
                is UserUiEffect.NavigateToDetail ->
                    onNavigateToDetail(effect.userId)
                is UserUiEffect.ShowToast ->
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
            }
        }
    }

    UserContent(uiState = uiState, onEvent = viewModel::onEvent)
}
```

---

## 5. Content（无状态，✅ 必须可 Preview）

```kotlin
@Composable
fun UserContent(
    uiState: UserUiState,
    onEvent: (UserUiIntent) -> Unit,
    modifier: Modifier = Modifier
) {
    Box(modifier = modifier.fillMaxSize()) {
        when {
            uiState.isLoading       -> UserLoadingState()
            uiState.error != null   -> UserErrorState(
                message = uiState.error,
                onRetry = { onEvent(UserUiIntent.Refresh) }
            )
            uiState.users.isEmpty() -> UserEmptyState()
            else -> UserList(
                users = uiState.users,
                onUserClick = { onEvent(UserUiIntent.OnUserClick(it)) }
            )
        }
    }
}
```

---

## 6. 子组件（✅ 每个独立 Preview）

```kotlin
@Composable
fun UserList(
    users: List<User>,
    onUserClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier) {
        items(users, key = { it.id }) { user ->
            UserCard(name = user.name, onClick = { onUserClick(user.id) })
        }
    }
}

@Composable
fun UserCard(
    name: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(onClick = onClick, modifier = modifier.fillMaxWidth()) {
        Text(text = name)
    }
}

@Composable
fun UserLoadingState(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
fun UserEmptyState(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("暂无数据")
    }
}

@Composable
fun UserErrorState(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = message, color = MaterialTheme.colorScheme.error)
        Button(onClick = onRetry) { Text("重试") }
    }
}
```

---

## 7. Preview（至少 1 个整体，多状态须用户明确要求才追加）

至少 1 个整体 Content Preview，假数据覆盖所有主要 UI 元素。多状态（Loading/Empty/Error）Preview **不主动生成**，仅在用户明确要求时追加。

### 7.1 基础示例

```kotlin
@Preview(showBackground = true, name = "UserContent")
@Composable
private fun UserContentPreview_Success() {
    AppTheme {
        UserContent(
            uiState = UserUiState(
                users = listOf(User("1", "张三"), User("2", "李四")),
            ),
            onEvent = {}
        )
    }
}
```

### 7.2 数据完整性要求

**列表字段**：至少 2-3 个元素，避免空列表
```kotlin
// ✅ 正确：显示列表项，可检测 UI 问题
items = listOf(
    Item(id = "1", name = "样例1", status = Status.ACTIVE),
    Item(id = "2", name = "样例2", status = Status.INACTIVE)
)

// ❌ 错误：空列表，UI 不显示任何内容
items = emptyList()
```

**枚举/Nullable 字段**：提供有效值
```kotlin
// ✅ 正确
currentMode = Mode.ADVANCED,
userName = "测试用户",

// ❌ 错误
currentMode = null,
userName = null,
```

### 7.3 Anonymous Object Stub（接口实现）

**规则**：`val` 属性构造时求值（必须具体值），函数调用时求值（可用 `error()`）

```kotlin
@Preview
@Composable
private fun SwitchListPreview() {
    val sampleSwitches = listOf(
        object : WirelessSwitchUnit {
            // val 属性：构造时执行，不能用 error()
            override val unitName: String = "SW-EN600-L"
            override val productSerialNo: String? = "W12345678"
            override val lastConnectedTime: Long = 1704067200000L
            override val switchButtonInfo: List<SwitchButtonInfo> = emptyList()
            override val componentBrand: String? = "SHIMANO"
            override val isThirdPartyUnit: ThirdPartyInfo = ThirdPartyInfo(
                isThirdPartyUnit = false,
                categoryName = null,
                isSupportedWarrantyService = true
            )
            
            // 函数：调用时执行，可用 error()（Preview 渲染时不会调用）
            override fun getBatteryLevels() = WirelessBatteryLevel.SUFFICIENT_BATTERY
            override fun addSatelliteShifter() = error("Preview stub")
            override suspend fun getSwitchImage(): SwitchImageInfo = error("Preview stub")
            override fun getFirmwareUpdate(): FirmwareUpdate = error("Preview stub")
        }
    )
    
    SwitchListContent(switches = sampleSwitches, onEvent = {})
}
```

**Data Class 直接构造**（无需 Anonymous Object）：
```kotlin
@Preview
@Composable
private fun BatteryInfoPreview() {
    val sampleBattery = BatteryInfo(
        level = 85,
        name = "BT-E8036",
        chargeState = ChargeState.ON_STANDBY
    )
    
    BatteryInfoCard(battery = sampleBattery)
}
```

### 7.4 多状态 Preview（可选）

```kotlin
@Preview(name = "加载中")
@Composable
private fun UserContentPreview_Loading() {
    AppTheme {
        UserContent(
            uiState = UserUiState(isLoading = true, users = emptyList()),
            onEvent = {}
        )
    }
}

@Preview(name = "错误状态")
@Composable
private fun UserContentPreview_Error() {
    AppTheme {
        UserContent(
            uiState = UserUiState(
                isLoading = false,
                error = "网络错误",
                users = emptyList()
            ),
            onEvent = {}
        )
    }
}

@Preview(name = "空列表")
@Composable
private fun UserContentPreview_Empty() {
    AppTheme {
        UserContent(
            uiState = UserUiState(isLoading = false, users = emptyList()),
            onEvent = {}
        )
    }
}
```

---

## 8. 重组性能优化

```kotlin
// ✅ 全 val 且字段均为稳定类型（String/Boolean/Int 等）：编译器自动推断，无需标注
data class User(val id: String, val name: String)

// ⚠️ 含 List<T> 字段时编译器无法推断稳定性：
//    方案A：改用 ImmutableList（推荐）
//    方案B：手动加 @Stable（开发者承诺 equals 稳定，但 List 内容变更需确保新对象）
@Stable
data class UserUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

// ✅ LazyColumn 必须提供 key，避免全量重组
LazyColumn {
    items(users, key = { it.id }) { user ->
        UserCard(name = user.name, onClick = { onUserClick(user.id) })
    }
}

// ✅ 派生状态用 derivedStateOf，避免过度重组
val isListEmpty by remember {
    derivedStateOf { uiState.users.isEmpty() }
}

// ✅ lambda 推迟读取频繁变化的 State，避免父组件重组
@Composable
fun ScrollHeader(scrollState: ScrollState) {
    // ❌ 错误：直接读取会导致 ScrollHeader 随滚动频繁重组
    // val alpha = if (scrollState.value > 100) 1f else 0f

    // ✅ 正确：用 lambda 推迟读取，只有 Box 内部重组
    Box(modifier = Modifier.graphicsLayer { alpha = if (scrollState.value > 100) 1f else 0f })
}
```

---

## 9. 可测试性标准写法

```kotlin
// ✅ Repository 定义为接口，方便注入 fake 实现
interface UserRepository {
    suspend fun getUsers(): List<User>
}

class UserRepositoryImpl(
    private val api: UserApi   // 依赖接口而非具体类
) : UserRepository {
    override suspend fun getUsers() = api.fetchUsers()
}

// ✅ FakeRepository 用于单元测试
class FakeUserRepository(
    private val result: Result<List<User>> = Result.success(emptyList())
) : UserRepository {
    override suspend fun getUsers() = result.getOrThrow()
}

// ✅ ViewModel 只依赖接口，无 Android 框架类，可在 JVM 测试
class UserViewModel(
    private val repository: UserRepository   // 接口，不是 Context/Application
) : ViewModel() { ... }

// ✅ ViewModel 单元测试示例
class UserViewModelTest {
    @Test
    fun `loadUsers success updates state`() = runTest {
        val fakeRepo = FakeUserRepository(
            result = Result.success(listOf(User("1", "张三")))
        )
        val viewModel = UserViewModel(fakeRepo)

        viewModel.onEvent(UserUiIntent.LoadUsers)
        advanceUntilIdle()

        assertEquals(false, viewModel.uiState.value.isLoading)
        assertEquals(1, viewModel.uiState.value.users.size)
    }
}

// ✅ Content 无状态，可直接用 ComposeTestRule 测试 UI
@Test
fun `UserContent shows loading indicator`() {
    composeTestRule.setContent {
        UserContent(uiState = UserUiState(isLoading = true), onEvent = {})
    }
    composeTestRule.onNodeWithTag("loading_indicator").assertIsDisplayed()
}
```

---

## 10. 可见性与作用域

```kotlin
// ✅ 局部变量优先：只在函数内用的变量不提升为成员变量
private fun loadUsers() {
    viewModelScope.launch {
        // ✅ pageSize 只此处使用，局部变量
        val pageSize = 20
        val users = repository.getUsers(pageSize)
        _uiState.update { it.copy(users = users) }
    }
}

// ❌ 错误：提升为成员变量但只在一处用
class BadViewModel : ViewModel() {
    private val pageSize = 20   // ❌ 只在 loadUsers 用，应为局部变量
    private fun loadUsers() { repository.getUsers(pageSize) }
}

// ✅ 可见性最小化
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    // public：对外暴露的 API
    fun onEvent(intent: UserUiIntent) { ... }

    // private：内部实现，外部不需要知道
    private fun loadUsers() { ... }
    private fun navigateToDetail(id: String) { ... }
}

// ✅ 逻辑相似的 Boolean 状态合并为 sealed class
// ❌ 错误：多个相互排斥的 Boolean 标志
data class BadUiState(
    val isLoadingUsers: Boolean = false,
    val isLoadingOrders: Boolean = false,
    val isLoadingProfile: Boolean = false
)

// ✅ 正确：合并为枚举或 sealed class
sealed interface LoadingState {
    data object Idle : LoadingState
    data object LoadingUsers : LoadingState
    data object LoadingOrders : LoadingState
    data object LoadingProfile : LoadingState
}

data class GoodUiState(
    val loadingState: LoadingState = LoadingState.Idle,
    val users: List<User> = emptyList()
)

// ✅ 冗余同类变量合并
// ❌ 错误：两个表达同一概念的变量
class BadViewModel : ViewModel() {
    private var currentPage = 0
    private var pageIndex = 0   // ❌ 和 currentPage 含义一样
}

// ✅ 正确：保留一个，命名清晰
class GoodViewModel : ViewModel() {
    private var currentPage = 0
}
```
