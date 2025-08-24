# --- PATH: GameFocusManager/main.py ---

import time
from src.worker_manager import WorkerManager

def print_status(manager):
    """Функция для вывода текущего статуса"""
    is_running, pid = manager.is_running()
    if is_running:
        print(f"СТАТУС: Воркер активен (PID: {pid})")
    else:
        print("СТАТУС: Воркер неактивен")

def main():
    """Основная функция для интерактивного тестирования"""
    manager = WorkerManager()

    print("--- Тестирование WorkerManager ---")
    print_status(manager)
    print("----------------------------------")

    while True:
        print("\nДоступные команды:")
        print("  1 - Запустить воркер")
        print("  2 - Остановить воркер")
        print("  3 - Проверить статус")
        print("  4 - Показать лог (последние 10 строк)")
        print("  q - Выйти")

        choice = input("Введите команду: ")

        if choice == '1':
            print("\nПопытка запуска воркера...")
            manager.start()
            time.sleep(1) # Даем время на запуск и проверку
            print_status(manager)
        elif choice == '2':
            print("\nПопытка остановки воркера...")
            manager.stop()
            time.sleep(1) # Даем время на остановку
            print_status(manager)
        elif choice == '3':
            print("\nПроверка статуса...")
            print_status(manager)
        elif choice == '4':
            print("\n--- Лог-файл ---")
            if manager.log_file.exists():
                # Выводим последние 10 строк лога
                lines = manager.log_file.read_text().splitlines()
                for line in lines[-10:]:
                    print(line)
            else:
                print("Лог-файл еще не создан.")
            print("----------------")
        elif choice.lower() == 'q':
            print("Выход.")
            # Убедимся, что воркер остановлен при выходе из теста
            if manager.is_running()[0]:
                print("Останавливаем воркер перед выходом...")
                manager.stop()
            break
        else:
            print("Неверная команда.")

if __name__ == "__main__":
    main()