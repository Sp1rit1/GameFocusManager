# --- PATH: GameFocusManager/setup.py ---

from cx_Freeze import setup, Executable

# Список дополнительных файлов, которые нужно включить в сборку
# Формат: ('путь к файлу', 'путь назначения в сборке')
include_files = [
    "focus_worker.sh",
    "games.json"
]

# Опции для сборки
build_exe_options = {
    "packages": ["os", "sys"],
    "excludes": ["tkinter"], # Исключаем ненужные модули
    "include_files": include_files,
    "build_exe": "build/GameFocusManager" # Указываем папку для сборки
}

# Определяем нашу главную точку входа
base = "gui" # Используем "gui" для GUI-приложений на Linux

setup(
    name="GameFocusManager",
    version="1.0",
    description="Manages game performance on focus loss.",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="GameFocusManager")]
)