# --- PATH: GameFocusManager/src/worker_manager.py ---

import os
import signal
import subprocess
from pathlib import Path


class WorkerManager:
    """
    Manages the lifecycle of the focus_worker.sh background script.
    It uses a PID file to track the worker's process ID.
    """

    def __init__(self):
        # Определяем пути, используя pathlib для кроссплатформенности
        self.home_dir = Path.home()
        self.project_root = self._find_project_root()
        self.pid_file = Path("/tmp/game_focus_manager.pid")
        self.log_file = Path("/tmp/game_focus_manager.log")
        self.worker_script = self.project_root / "focus_worker.sh"

    def _find_project_root(self) -> Path:
        # Простой способ найти корень проекта, предполагая, что скрипт запускается оттуда
        # В будущем можно сделать более сложную логику
        return Path(os.getcwd())

    def is_running(self) -> (bool, int):
        """
        Checks if the worker process is currently running.
        Returns a tuple: (True/False, PID or -1)
        """
        if not self.pid_file.exists():
            return False, -1

        try:
            pid = int(self.pid_file.read_text().strip())
            # Проверяем, существует ли процесс с таким PID
            # os.kill(pid, 0) не убивает процесс, а проверяет, можно ли послать ему сигнал
            os.kill(pid, 0)
            return True, pid
        except (ValueError, ProcessLookupError, PermissionError):
            # Если PID некорректный или процесс не существует
            # Очищаем "мёртвый" PID-файл
            self.pid_file.unlink(missing_ok=True)
            return False, -1

    def start(self) -> bool:
        """
        Starts the focus_worker.sh script as a detached background process.
        Returns True on success, False on failure.
        """
        is_running, _ = self.is_running()
        if is_running:
            print("Worker is already running.")
            return False

        if not self.worker_script.is_file():
            print(f"Error: Worker script not found at {self.worker_script}")
            return False

        # Убеждаемся, что скрипт исполняемый
        self.worker_script.chmod(0o755)

        try:
            # Запускаем скрипт как полностью новый, отсоединенный процесс
            # Он не будет дочерним для нашего Python-приложения
            process = subprocess.Popen(
                [str(self.worker_script)],
                start_new_session=True,  # <-- Ключевой параметр для отсоединения
                stdout=subprocess.DEVNULL,  # Мы не следим за выводом здесь,
                stderr=subprocess.DEVNULL  # так как скрипт сам пишет в лог-файл
            )

            # Записываем PID нового процесса в PID-файл
            self.pid_file.write_text(str(process.pid))
            print(f"Worker started successfully with PID: {process.pid}")
            return True
        except Exception as e:
            print(f"Failed to start worker: {e}")
            return False

    def stop(self) -> bool:
        """
        Stops the worker process using the PID from the PID file.
        Returns True on success, False on failure.
        """
        is_running, pid = self.is_running()
        if not is_running:
            print("Worker is not running.")
            return False

        try:
            # Отправляем сигнал SIGTERM (корректное завершение) процессу
            os.kill(pid, signal.SIGTERM)
            # Удаляем PID-файл
            self.pid_file.unlink(missing_ok=True)
            print(f"Stop signal sent to worker with PID: {pid}")
            return True
        except Exception as e:
            print(f"Failed to stop worker: {e}")
            return False