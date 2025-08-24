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
        print("  q - Выйти из тестового скрипта")

        choice = input("Введите команду: ")

        if choice == '1':
            print("\nПопытка запуска воркера...")
            manager.start()
        elif choice == '2':
            print("\nПопытка остановки воркера...")
            manager.stop()
        elif choice == '3':
            print("\nПроверка статуса...")
            print_status(manager)
        elif choice == '4':
            print("\n--- Лог-файл ---")
            # --- ИСПРАВЛЕНО: Теперь мы просим менеджер показать логи ---
            log_lines = manager.get_log_tail()
            for line in log_lines:
                print(line)
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
            print("----------------")
        elif choice.lower() == 'q':
            print("Выход.")
            break
        else:
            print("Неверная команда.")

if __name__ == "__main__":
    main()