package com.ivan.unavoce

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ivan.unavoce.ui.theme.CCappTheme
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.Outline
import androidx.compose.ui.graphics.asComposePath
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import androidx.graphics.shapes.RoundedPolygon
import androidx.graphics.shapes.star
import androidx.graphics.shapes.toPath
import androidx.graphics.shapes.CornerRounding

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val sharedPreferences = getSharedPreferences("UnavoceSettings", MODE_PRIVATE)

        setContent {
            // Читаем из памяти настройку темной темы
            val isSystemDark = androidx.compose.foundation.isSystemInDarkTheme()
            val isDarkTheme = remember {
                mutableStateOf(sharedPreferences.getBoolean("dark_theme", isSystemDark))
            }

            // Читаем из памяти настройку динамических цветов
            val useDynamicColor = remember {
                mutableStateOf(sharedPreferences.getBoolean("dynamic_color", false))
            }

            CCappTheme(useDynamicColor = useDynamicColor.value) {
                val context = LocalContext.current
                val currentScreen = remember { mutableStateOf("Menu") }
                val previousScreen = remember { mutableStateOf("Menu") }
                val currentFileId = remember { mutableIntStateOf(R.raw.orientales_omnes_ecclesias) }

                val isAccessibilityMode = remember {
                    mutableStateOf(sharedPreferences.getBoolean("accessibility_mode", false))
                }

                val fontSize = remember {
                    mutableIntStateOf(sharedPreferences.getInt("font_size", 20))
                }

                val mainViewModel: MainViewModel = viewModel()
                val upcomingFeastText by mainViewModel.upcomingFeastText.collectAsState()
                val selectedLibraryAuthor = remember { mutableStateOf<String?>(null) }

                when (currentScreen.value) {
                    "Menu" -> {
                        MainScreen(
                            isAccessibilityMode = isAccessibilityMode.value,
                            upcomingFeastText = upcomingFeastText,
                            onLibraryClick = {
                                selectedLibraryAuthor.value = null
                                previousScreen.value = "Menu"
                                currentScreen.value = "Library"
                            },
                            onPrayerBookClick = {
                                previousScreen.value = "Menu"
                                currentScreen.value = "PrayerBook"
                            },
                            onSettingsClick = {
                                previousScreen.value = "Menu"
                                currentScreen.value = "Settings"
                            }
                        )
                    }

                    "Library" -> {
                        LibraryScreen(
                            selectedAuthor = selectedLibraryAuthor.value,
                            onAuthorChange = { author -> selectedLibraryAuthor.value = author },
                            onBackClick = {
                                selectedLibraryAuthor.value = null
                                currentScreen.value = "Menu"
                            },
                            onDocumentClick = { fileId ->
                                currentFileId.intValue = fileId
                                previousScreen.value = "Library"
                                currentScreen.value = "TextReader"
                            }
                        )
                    }

                    "PrayerBook" -> {
                        PrayerBookScreen(
                            onBackClick = { currentScreen.value = "Menu" },
                            onPrayerClick = { fileId ->
                                currentFileId.intValue = fileId
                                previousScreen.value = "PrayerBook"
                                currentScreen.value = "TextReader"
                            }
                        )
                    }

                    "TextReader" -> {
                        TextReaderScreen(
                            fileResId = currentFileId.intValue,
                            fontSize = fontSize.intValue,
                            onInternalLinkClick = { docName ->
                                val resId = context.resources.getIdentifier(
                                    docName,
                                    "raw",
                                    context.packageName
                                )
                                if (resId != 0) {
                                    currentFileId.intValue = resId
                                }
                            },
                            onBackClick = { currentScreen.value = previousScreen.value }
                        )
                    }

                    "Settings" -> {
                        SettingsScreen(
                            isAccessibilityMode = isAccessibilityMode.value,
                            onModeChange = { newValue ->
                                isAccessibilityMode.value = newValue
                                sharedPreferences.edit().putBoolean("accessibility_mode", newValue).apply()
                            },
                            fontSize = fontSize.intValue,
                            onFontSizeChange = { newSize ->
                                fontSize.intValue = newSize
                                sharedPreferences.edit().putInt("font_size", newSize).apply()
                            },
                            useDynamicColor = useDynamicColor.value,
                            onDynamicColorChange = { newValue ->
                                useDynamicColor.value = newValue
                                sharedPreferences.edit().putBoolean("dynamic_color", newValue).apply()
                            },
                            onBackClick = { currentScreen.value = previousScreen.value }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MainScreen(
    isAccessibilityMode: Boolean,
    upcomingFeastText: String,
    onLibraryClick: () -> Unit,
    onPrayerBookClick: () -> Unit,
    onSettingsClick: () -> Unit
) {
    var showCalendar by remember { mutableStateOf(false) }

    if (showCalendar) {
        LiturgicalCalendarScreen(onBackClick = { showCalendar = false })
    } else {
        Scaffold(
            containerColor = MaterialTheme.colorScheme.background,
            bottomBar = {
                BottomAppBar(
                    containerColor = MaterialTheme.colorScheme.secondaryContainer,
                    modifier = Modifier.clip(RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)),
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(80.dp)
                            .padding(horizontal = 16.dp)
                    ) {
                        Text(
                            text = "Una Voce Russia",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                            modifier = Modifier.align(Alignment.Center)
                        )

                        FloatingActionButton(
                            onClick = onSettingsClick,
                            shape = RealCloverShape,
                            containerColor = MaterialTheme.colorScheme.primaryContainer,
                            contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                            elevation = FloatingActionButtonDefaults.elevation(0.dp),
                            modifier = Modifier
                                .align(Alignment.CenterEnd)
                                .size(80.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Настройки",
                                modifier = Modifier.size(30.dp)
                            )
                        }
                    }
                }
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                        .clip(RoundedCornerShape(28.dp))
                        .background(MaterialTheme.colorScheme.primaryContainer)
                        .clickable { showCalendar = true },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = upcomingFeastText,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                        lineHeight = 32.sp,
                        modifier = Modifier.padding(16.dp)
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    MenuTile(
                        title = "Бревиарий",
                        imageResId = R.drawable.breviarium,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { /* TODO */ }
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    MenuTile(
                        title = "Библиотека",
                        imageResId = R.drawable.biblioteka,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { onLibraryClick() }
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    MenuTile(
                        title = "Тексты Собора",
                        imageResId = R.drawable.trieden,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { /* TODO */ }
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    MenuTile(
                        title = "Молитвенник",
                        imageResId = R.drawable.molitva,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { onPrayerBookClick() }
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    MenuTile(
                        title = "Чин Мессы",
                        imageResId = R.drawable.missa,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { /* TODO */ }
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    MenuTile(
                        title = "Вульгата",
                        imageResId = R.drawable.vulgata,
                        isAccessibilityMode = isAccessibilityMode,
                        modifier = Modifier.weight(1f),
                        onClick = { /* TODO */ }
                    )
                }
            }
        }
    }
}

@Composable
fun MenuTile(
    title: String,
    imageResId: Int,
    isAccessibilityMode: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    ElevatedCard(
        modifier = modifier
            .height(100.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.elevatedCardElevation(defaultElevation = 6.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            Image(
                painter = painterResource(id = imageResId),
                contentDescription = title,
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize()
            )

            if (isAccessibilityMode) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.6f))
                )
                Text(
                    text = title,
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .align(Alignment.Center)
                        .padding(8.dp)
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    isAccessibilityMode: Boolean,
    onModeChange: (Boolean) -> Unit,
    fontSize: Int,
    onFontSizeChange: (Int) -> Unit,
    isDarkTheme: Boolean,
    onDarkThemeChange: (Boolean) -> Unit,
    // ВЕРНУЛИ ПАРАМЕТРЫ ДЛЯ ДИНАМИЧЕСКИХ ЦВЕТОВ:
    useDynamicColor: Boolean,
    onDynamicColorChange: (Boolean) -> Unit,
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Настройки",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Назад",
                            tint = MaterialTheme.colorScheme.onBackground
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp)
        ) {

            // 1. Блок: Темная тема
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Темная тема",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "Строгий ночной режим",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = isDarkTheme,
                    onCheckedChange = onDarkThemeChange,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = MaterialTheme.colorScheme.primary,
                        checkedTrackColor = MaterialTheme.colorScheme.primaryContainer
                    )
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 2. Блок: Динамические цвета (Умные обои)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Динамические цвета",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "Цвета на основе обоев (Android 12+)",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = useDynamicColor,
                    onCheckedChange = onDynamicColorChange,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = MaterialTheme.colorScheme.primary,
                        checkedTrackColor = MaterialTheme.colorScheme.primaryContainer
                    )
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 3. Блок: Режим для слабовидящих
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Режим для слабовидящих",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "Высокий контраст на карточках",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = isAccessibilityMode,
                    onCheckedChange = onModeChange,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = MaterialTheme.colorScheme.primary,
                        checkedTrackColor = MaterialTheme.colorScheme.primaryContainer
                    )
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 4. Блок: Ползунок размера текста
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp)
            ) {
                Text(
                    text = "Размер текста в разделах",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "Текущий размер: $fontSize",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )

                Slider(
                    value = fontSize.toFloat(),
                    onValueChange = { onFontSizeChange(it.toInt()) },
                    valueRange = 14f..30f,
                    steps = 15,
                    colors = SliderDefaults.colors(
                        thumbColor = MaterialTheme.colorScheme.primary,
                        activeTrackColor = MaterialTheme.colorScheme.primary
                    )
                )
            }
        }
    }
}
