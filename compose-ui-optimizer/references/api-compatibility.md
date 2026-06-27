# API 版本兼容性参考

## Coil 图片加载库

### Coil 2.x
```kotlin
AsyncImage(
    model = imageUrl,
    contentDescription = "描述",
    onState = { state ->
        when (state) {
            is AsyncImagePainter.State.Success -> { /* ... */ }
            is AsyncImagePainter.State.Error -> { /* ... */ }
            else -> {}
        }
    }
)
```

### Coil 3.x
```kotlin
AsyncImage(
    model = imageUrl,
    contentDescription = "描述",
    placeholder = ColorPainter(Color(0xFFE0E0E0)),
    error = ColorPainter(Color(0xFFBDBDBD)),
    onSuccess = { state -> /* ... */ },
    onError = { state -> /* ... */ },
    onLoading = { state -> /* ... */ }
)
```

**变更**：`onState` → `onSuccess` + `onError` + `onLoading`

---

## Compose Lifecycle

### Compose 1.x (KMP commonMain)
```kotlin
// ❌ 不支持，commonMain 缺少 lifecycle-runtime-compose 多平台实现
val uiState by viewModel.uiState.collectAsStateWithLifecycle()

// ✅ 替代方案
val uiState by viewModel.uiState.collectAsState()
```

### Compose 2.x (KMP commonMain)
```kotlin
// ✅ 支持，添加 org.jetbrains.androidx.lifecycle:lifecycle-runtime-compose 依赖后
// 与 Android 单平台用法一致，用 by 委托读取 State<T> 的值
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

---

## 其他常见 API 变更

### Navigation Compose
```kotlin
// 1.x
NavHost(navController, startDestination) { }

// 2.x
NavHost(navController, startDestination, route) { }
```

### Material3
```kotlin
// 1.0.x
Scaffold(topBar = { }, content = { })

// 1.1.x+
Scaffold(topBar = { }) { paddingValues ->
    // 必须使用 paddingValues
}
```
