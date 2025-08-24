# --- PATH: GameFocusManager/src/status_tab.py ---

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

# Мы импортируем наш WorkerManager, чтобы использовать его
from src.worker_manager import WorkerManager


class StatusTab(QWidget):
    """
    A widget for the 'Status' tab. Provides controls to start/stop the worker
    and displays its current state.
    """

    def __init__(self, worker_manager: WorkerManager):
        super().__init__()

        self.worker_manager = worker_manager

        # --- Создание элементов интерфейса ---

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем всё

        # Добавляем "распорку" сверху, чтобы прижать всё к центру
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Метка статуса
        self.status_label = QLabel("Статус: Неизвестен")
        font = self.status_label.font()
        font.setPointSize(14)
        self.status_label.setFont(font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка-переключатель
        self.toggle_button = QPushButton("АКТИВИРОВАТЬ")
        self.toggle_button.setFixedSize(200, 60)  # Делаем кнопку большой и заметной
        font = self.toggle_button.font()
        font.setPointSize(16)
        font.setBold(True)
        self.toggle_button.setFont(font)

        # Добавляем виджеты в лейаут
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Добавляем "распорку" снизу
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Подключение сигналов к слотам ---
        self.toggle_button.clicked.connect(self.toggle_worker)

        # --- Логика обновления статуса ---

        # Создаем таймер, который будет проверять статус воркера каждую секунду
        self.status_timer = QTimer()
        self.status_timer.setInterval(1000)  # 1000 мс = 1 секунда
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start()

        # Сразу же обновляем статус при запуске
        self.update_status()

    def update_status(self):
        """ Проверяет, запущен ли воркер, и обновляет интерфейс. """
        is_running, pid = self.worker_manager.is_running()

        if is_running:
            self.status_label.setText(f"Статус: Активен (PID: {pid})")
            self.toggle_button.setText("ДЕАКТИВИРОВАТЬ")
            # Устанавливаем "опасный" красный цвет для кнопки
            self.toggle_button.setStyleSheet("background-color: #d32f2f; color: white;")
        else:
            self.status_label.setText("Статус: Неактивен")
            self.toggle_button.setText("АКТИВИРОВАТЬ")
            # Устанавливаем "безопасный" зелёный цвет для кнопки
            self.toggle_button.setStyleSheet("background-color: #388e3c; color: white;")

    def toggle_worker(self):
        """ Запускает или останавливает воркер в зависимости от его состояния. """
        is_running, _ = self.worker_manager.is_running()

        if is_running:
            self.worker_manager.stop()
        else:
            self.worker_manager.start()

        # Немедленно обновляем статус после нажатия, не дожидаясь таймера
        # Добавляем небольшую задержку, чтобы система успела обработать start/stop
        QTimer.singleShot(500, self.update_status)