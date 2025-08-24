import os
import subprocess
from pathlib import Path

class WorkerManager:

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.worker_script = self.project_root / "focus_worker.sh"
        self.pid_file = Path("/tmp/game_focus_manager.pid")

    def is_running(self) -> (bool, int):
        if not self.pid_file.exists():
            return False, -1
        try:
            pid = int(self.pid_file.read_text().strip())
            os.kill(pid, 0)
            return True, pid
        except (ValueError, ProcessLookupError):
            self.pid_file.unlink(missing_ok=True)
            return False, -1

    def start(self) -> bool:
        if self.is_running()[0]:
            print("Worker is already running.")
            return False

        if not self.worker_script.is_file():
            print(f"Error: Worker script not found at {self.worker_script}")
            return False

        self.worker_script.chmod(0o755)

        try:
            # Запускаем воркер, передавая ему полное окружение для доступа к системным утилитам.
            subprocess.Popen(
                [str(self.worker_script)],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy()
            )
            # Воркер сам создаст PID-файл почти мгновенно.
            print("Start command sent to worker.")
            return True
        except Exception as e:
            print(f"Failed to start worker: {e}")
            return False

    def stop(self) -> bool:
        is_running, pid = self.is_running()
        if not is_running:
            print("Worker is not running.")
            return False

        try:
            # Используем pkill для гарантированной остановки.
            # `trap` в Bash-скрипте поймает сигнал и выполнит очистку.
            subprocess.run(["pkill", "-f", str(self.worker_script)])
            print(f"Stop signal sent to worker process (was PID: {pid})")
            return True
        except Exception as e:
            print(f"Failed to stop worker: {e}")
            return False