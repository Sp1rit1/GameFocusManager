# --- PATH: GameFocusManager/src/settings_tab.py ---

import json
import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QLineEdit, QPushButton, QLabel, QMessageBox,
                               QFormLayout, QSpinBox)  # <-- Добавляем новые виджеты
from PySide6.QtCore import Qt


class SettingsTab(QWidget):
    """
    A widget for the 'Settings' tab. Allows managing the list of monitored games
    and FPS limits.
    """

    def __init__(self):
        super().__init__()

        # --- ИСПРАВЛЕНО: Определяем путь к конфигу в корне проекта ---
        # Мы предполагаем, что приложение запускается из корня проекта.
        self.project_root = Path(os.getcwd())
        self.config_file = self.project_root / "games.json"
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        # --- Создание элементов интерфейса ---

        main_layout = QVBoxLayout(self)

        # --- Секция списка игр ---
        games_group_layout = QVBoxLayout()
        list_label = QLabel("Отслеживаемые игры (имена процессов или .exe):")
        self.games_list_widget = QListWidget()

        add_remove_layout = QHBoxLayout()
        self.new_game_input = QLineEdit()
        self.new_game_input.setPlaceholderText("Например, dota2 или witcher3.exe")
        self.add_button = QPushButton("Добавить")
        self.remove_button = QPushButton("Удалить выбранное")

        add_remove_layout.addWidget(self.new_game_input)
        add_remove_layout.addWidget(self.add_button)
        add_remove_layout.addWidget(self.remove_button)

        games_group_layout.addWidget(list_label)
        games_group_layout.addWidget(self.games_list_widget)
        games_group_layout.addLayout(add_remove_layout)

        # --- ДОБАВЛЕНО: Секция настроек FPS ---
        fps_group_layout = QFormLayout()
        fps_label = QLabel("Настройки лимитов FPS:")
        fps_label.setStyleSheet("font-weight: bold; margin-top: 10px;")  # Делаем заголовок жирным

        self.active_fps_spinbox = QSpinBox()
        self.active_fps_spinbox.setRange(0, 1000)
        self.active_fps_spinbox.setSuffix(" FPS")
        self.active_fps_spinbox.setSpecialValueText("Без лимита")  # Показывает текст для значения 0

        self.inactive_fps_spinbox = QSpinBox()
        self.inactive_fps_spinbox.setRange(1, 1000)
        self.inactive_fps_spinbox.setSuffix(" FPS")

        fps_group_layout.addRow(fps_label)
        fps_group_layout.addRow("Активный режим (0 = без лимита):", self.active_fps_spinbox)
        fps_group_layout.addRow("Фоновый режим:", self.inactive_fps_spinbox)

        self.save_fps_button = QPushButton("Сохранить лимиты FPS")
        # --- КОНЕЦ ДОБАВЛЕНИЯ ---

        # Добавляем все виджеты в основной лейаут
        main_layout.addLayout(games_group_layout)
        main_layout.addLayout(fps_group_layout)
        main_layout.addWidget(self.save_fps_button, 0, Qt.AlignmentFlag.AlignRight)
        main_layout.addStretch()  # Добавляем "распорку", чтобы прижать всё к верху

        # --- Подключение сигналов к слотам ---
        self.add_button.clicked.connect(self.add_game)
        self.remove_button.clicked.connect(self.remove_game)
        self.save_fps_button.clicked.connect(self.save_config)  # <-- Привязываем сохранение FPS

        # --- Начальная загрузка данных ---
        self.load_config()

    def load_config(self):
        """ Загружает всю конфигурацию из games.json и обновляет UI. """
        self.games_list_widget.clear()

        if not self.config_file.exists():
            self.save_config()  # Создаст дефолтный конфиг, если его нет

        try:
            with self.config_file.open("r") as f:
                data = json.load(f)

                # Загружаем список игр
                games = data.get("games_to_watch", [])
                self.games_list_widget.addItems(games)

                # Загружаем лимиты FPS
                self.active_fps_spinbox.setValue(data.get("fps_limit_active", 0))
                self.inactive_fps_spinbox.setValue(data.get("fps_limit_inactive", 20))

        except (json.JSONDecodeError, Exception) as e:
            QMessageBox.warning(self, "Ошибка Конфигурации",
                                f"Не удалось прочитать файл {self.config_file}:\n{e}")

    def save_config(self):
        """ Сохраняет всю конфигурацию (игры и FPS) в games.json. """
        games = []
        for i in range(self.games_list_widget.count()):
            games.append(self.games_list_widget.item(i).text())

        data = {
            "games_to_watch": games,
            "fps_limit_active": self.active_fps_spinbox.value(),
            "fps_limit_inactive": self.inactive_fps_spinbox.value()
        }

        try:
            with self.config_file.open("w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Конфигурация успешно сохранена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл настроек: {e}")

    def add_game(self):
        """ Добавляет новую игру в список и сохраняет конфиг. """
        game_name = self.new_game_input.text().strip()
        if game_name:
            items = [self.games_list_widget.item(i).text() for i in range(self.games_list_widget.count())]
            if game_name not in items:
                self.games_list_widget.addItem(game_name)
                self.save_config()
                self.new_game_input.clear()
            else:
                QMessageBox.information(self, "Информация", "Эта игра уже в списке.")
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, введите имя процесса игры.")

    def remove_game(self):
        """ Удаляет выбранную игру из списка и сохраняет конфиг. """
        selected_items = self.games_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите игру для удаления.")
            return

        for item in selected_items:
            self.games_list_widget.takeItem(self.games_list_widget.row(item))

        self.save_config()