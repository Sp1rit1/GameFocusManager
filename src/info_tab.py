# --- PATH: GameFocusManager/src/info_tab.py ---

import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTextBrowser,
                               QPlainTextEdit)
from PySide6.QtCore import QFileSystemWatcher, Slot


class InfoTab(QWidget):
    """
    A widget for the 'Info' tab. Displays help text and live logs.
    """

    def __init__(self):
        super().__init__()

        # --- Определяем путь к лог-файлу ---
        # Этот путь должен совпадать с тем, что используется в focus_worker.sh
        self.log_file = Path("/tmp/game_focus_manager.log")

        # --- Создание элементов интерфейса ---

        # Основной лейаут
        main_layout = QVBoxLayout(self)

        # Создаем вложенные вкладки
        tab_widget = QTabWidget()

        # --- Вкладка "Справка" ---
        help_widget = QWidget()
        help_layout = QVBoxLayout(help_widget)
        self.help_browser = QTextBrowser()
        self.help_browser.setOpenExternalLinks(True)  # Открывать ссылки в браузере
        self.populate_help_text()  # Заполняем текстом
        help_layout.addWidget(self.help_browser)

        # --- Вкладка "Логи" ---
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)  # Только для чтения
        self.log_viewer.setStyleSheet("font-family: monospace;")  # Моноширинный шрифт
        log_layout.addWidget(self.log_viewer)

        # Добавляем вложенные вкладки в основной виджет
        tab_widget.addTab(help_widget, "Справка")
        tab_widget.addTab(log_widget, "Логи")

        main_layout.addWidget(tab_widget)

        # --- Логика для обновления логов ---

        # Создаем "наблюдателя" за файловой системой
        self.file_watcher = QFileSystemWatcher()

        # Если лог-файл уже существует, добавляем его под наблюдение
        if self.log_file.exists():
            self.file_watcher.addPath(str(self.log_file))
            self.update_log_viewer()  # И сразу загружаем текущее содержимое

        # Подключаем сигнал изменения файла к нашему методу обновления
        self.file_watcher.fileChanged.connect(self.update_log_viewer)

    def populate_help_text(self):
        """ Заполняет вкладку "Справка" HTML-текстом. """
        help_html = """
        <h2>Game Focus Manager</h2>
        <p>Эта утилита автоматически управляет лимитом FPS в играх, чтобы снизить нагрузку на GPU, когда игра находится не в фокусе.</p>

        <h4>Как это работает:</h4>
        <ol>
            <li><b>Воркер:</b> Фоновый скрипт (<code>focus_worker.sh</code>) отслеживает, какая игра запущена и находится ли она в фокусе.</li>
            <li><b>Управление:</b> Когда игра теряет фокус, скрипт изменяет конфигурационный файл MangoHud, устанавливая низкий лимит FPS. Когда игра возвращает фокус, лимит снимается.</li>
            <li><b>Интерфейс:</b> Это приложение позволяет вам запускать/останавливать воркер и настраивать список отслеживаемых игр.</li>
        </ol>

        <h4>Требования:</h4>
        <ul>
            <li><b>MangoHud:</b> Должен быть установлен (<code>sudo dnf install mangohud</code>).</li>
            <li><b>kdotool:</b> Необходим для отслеживания окон в Wayland (<code>sudo dnf install kdotool</code>).</li>
            <li><b>jq:</b> Необходим для чтения JSON-конфига (<code>sudo dnf install jq</code>).</li>
        </ul>

        <p>Разработано с помощью Python и PySide6. Автор идеи и основной разработчик: <b>sp1rit</b>.</p>
        """
        self.help_browser.setHtml(help_html)

    @Slot(str)  # Декоратор, явно указывающий, что это слот PySide6
    def update_log_viewer(self):
        """ Читает лог-файл и обновляет текстовое поле. """
        try:
            # Проверяем, не был ли файл удален (например, при очистке /tmp)
            if not self.log_file.exists():
                self.log_viewer.setPlainText("Лог-файл не найден. Он будет создан при запуске воркера.")
                # Если файла нет, удаляем его из наблюдения
                paths = self.file_watcher.files()
                if paths:
                    self.file_watcher.removePaths(paths)
                return

            # Если файл есть, но его нет под наблюдением, добавляем
            if str(self.log_file) not in self.file_watcher.files():
                self.file_watcher.addPath(str(self.log_file))

            # Читаем содержимое и отображаем
            content = self.log_file.read_text()
            self.log_viewer.setPlainText(content)
            # Автоматически прокручиваем в самый конец
            self.log_viewer.verticalScrollBar().setValue(self.log_viewer.verticalScrollBar().maximum())
        except Exception as e:
            self.log_viewer.setPlainText(f"Ошибка чтения лог-файла:\n{e}")