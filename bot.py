package com.ivan.unavoce

import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TextReaderScreen(
    fileResId: Int,
    fontSize: Int,
    onInternalLinkClick: (String) -> Unit, // Наша новая команда для ссылок
    onBackClick: () -> Unit
) {
    val context = LocalContext.current

    // ВОТ ТОТ САМЫЙ БЛОК, КОТОРЫЙ СЛУЧАЙНО УДАЛИЛСЯ:
    val htmlContent = remember(fileResId, fontSize) {
        try {
            val rawText = context.resources.openRawResource(fileResId)
                .bufferedReader()
                .use { it.readText() }

            HtmlProcessor.process(rawText, fontSize)
        } catch (e: Exception) {
            "<html><body><h2>Ошибка: Не удалось загрузить текст</h2></body></html>"
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {}, // Заголовок убрали, как и договаривались
                navigationIcon = {
                    // Новая аккуратная стрелочка вместо громоздкой кнопки
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Назад",
                            tint = Color.DarkGray
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        }
    ) { innerPadding ->

        AndroidView(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 0.dp),
            factory = { ctx ->
                WebView(ctx).apply {
                    settings.loadWithOverviewMode = true
                    settings.useWideViewPort = true
                    settings.allowFileAccess = true
                    settings.allowContentAccess = true
                    setBackgroundColor(android.graphics.Color.TRANSPARENT)

                    // ВОТ ОН, НАШ ПЕРЕХВАТЧИК ССЫЛОК!
                    webViewClient = object : WebViewClient() {
                        override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                            val url = request?.url?.toString() ?: return false

                            // Ловим нашу хитрую "интернет"-ссылку
                            if (url.contains("unavoce.app/doc/")) {
                                // Вырезаем всё лишнее, достаем чистое имя файла (например "pix_i")
                                val docName = url.substringAfter("unavoce.app/doc/")
                                    .substringBefore("&") // отсекаем параметры Гугла
                                    .substringBefore("\"")
                                    .substringBefore("#")

                                onInternalLinkClick(docName) // Отправляем команду!
                                return true
                            }

                            // Если обычная ссылка в настоящий интернет — открываем как обычно
                            return false
                        }
                    }

                    loadDataWithBaseURL(
                        "file:///android_res/",
                        htmlContent,
                        "text/html",
                        "UTF-8",
                        null
                    )
                }
            },
            // И еще нужно обновлять WebView, если currentFileId изменился
            update = { webView ->
                webView.loadDataWithBaseURL(
                    "file:///android_res/",
                    htmlContent,
                    "text/html",
                    "UTF-8",
                    null
                )
            }
        )
    }
}
