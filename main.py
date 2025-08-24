# --- PATH: GameFocusManager/main.py (Финальная версия) ---

import sys
from PySide6.QtWidgets import QApplication
# Импортируем наш класс главного окна
from src.main_window import MainWindow

if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем и показываем наше главное окно
    window = MainWindow()
    window.show()

    # Запускаем главный цикл обработки событий
    sys.exit(app.exec())