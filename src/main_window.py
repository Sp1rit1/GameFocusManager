# --- PATH: GameFocusManager/src/main_window.py ---

from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget
from PySide6.QtGui import QIcon

# Импортируем все наши компоненты
from src.worker_manager import WorkerManager
from src.status_tab import StatusTab
from src.settings_tab import SettingsTab
from src.info_tab import InfoTab


class MainWindow(QMainWindow):
    """
    The main window of the application. It initializes the UI,
    creates the tabs, and holds the central WorkerManager instance.
    """

    def __init__(self):
        super().__init__()

        # --- Создаем ЕДИНЫЙ экземпляр WorkerManager ---
        # Все вкладки будут использовать его, чтобы обмениваться информацией
        # и управлять одним и тем же фоновым процессом.
        self.worker_manager = WorkerManager()

        # --- Настройка главного окна ---
        self.setWindowTitle("Game Focus Manager")
        self.resize(700, 500)

        # Устанавливаем иконку окна (путь к icon.png в корне проекта)
        # Убедитесь, что файл icon.png лежит в корне вашего проекта
        if (self.worker_manager.project_root / "icon.png").exists():
            self.setWindowIcon(QIcon(str(self.worker_manager.project_root / "icon.png")))

        # --- Создание и наполнение вкладок ---

        # Создаем виджет для управления вкладками
        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)

        # Создаем экземпляры каждой нашей вкладки
        # Передаем WorkerManager в StatusTab, так как он ему нужен
        status_widget = StatusTab(self.worker_manager)
        settings_widget = SettingsTab()  # Эта вкладка теперь независима
        info_widget = InfoTab()  # Эта вкладка тоже независима

        # Добавляем созданные виджеты-вкладки в QTabWidget
        tab_widget.addTab(status_widget, "Состояние")
        tab_widget.addTab(settings_widget, "Настройки")
        tab_widget.addTab(info_widget, "Информация")