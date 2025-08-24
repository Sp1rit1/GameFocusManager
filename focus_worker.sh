#!/bin/bash

# ===============================================================
#   Game Focus Manager - Worker Script
#   - Reads configuration from an external JSON file.
#   - Monitors for game processes.
#   - Tracks window focus using kdotool.
#   - Modifies the global MangoHud config to set FPS limits.
# ===============================================================

# --- ПУТИ И ПАРАМЕТРЫ ---
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/GameFocusManager"
GAMES_CONFIG_FILE="$CONFIG_DIR/games.json"
MANGOHUD_CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/MangoHud/MangoHud.conf"
LOG_FILE="/tmp/game_focus_manager.log"
# --- КОНЕЦ ПАРАМЕТРОВ ---

# Перенаправляем весь вывод (stdout и stderr) в лог-файл
# 'tee' позволяет одновременно выводить и в лог, и в консоль, если скрипт запущен вручную
exec > >(tee -a "$LOG_FILE") 2>&1

echo "--- [$(date +%T)] Focus Worker process started ---"

# Проверяем наличие необходимых утилит
if ! command -v jq &> /dev/null; then
    echo "[ERROR] 'jq' is not installed. Please install it with 'sudo dnf install jq'. Exiting."
    exit 1
fi
if ! command -v kdotool &> /dev/null; then
    echo "[ERROR] 'kdotool' is not installed. Please install it with 'sudo dnf install kdotool'. Exiting."
    exit 1
fi

# Функция для чтения параметров из JSON
read_config() {
    if [ ! -f "$GAMES_CONFIG_FILE" ]; then
        # Если конфига нет, создаем дефолтный
        mkdir -p "$CONFIG_DIR"
        echo '{"games_to_watch": [], "fps_limit_active": 0, "fps_limit_inactive": 20}' > "$GAMES_CONFIG_FILE"
        echo "[INFO] Config file not found. Created a default one at $GAMES_CONFIG_FILE."
    fi
    # Читаем массив игр в формате, понятном для pgrep (например, "dota2|witcher3.exe")
    GAMES_TO_WATCH_STR=$(jq -r '.games_to_watch | join("|")' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_ACTIVE=$(jq -r '.fps_limit_active' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_INACTIVE=$(jq -r '.fps_limit_inactive' "$GAMES_CONFIG_FILE")
}

# Функция для изменения ЕДИНОГО конфиг-файла MangoHud
set_global_mangohud_config() {
    local limit=$1
    # Создаем основной конфиг, если его нет
    touch "$MANGOHUD_CONFIG_FILE"
    # Удаляем старую строку fps_limit и добавляем новую
    sed -i '/^fps_limit=/d' "$MANGOHUD_CONFIG_FILE"
    echo "fps_limit=$limit" >> "$MANGOHUD_CONFIG_FILE"
    echo "[ACTION] Set global fps_limit=$limit in $MANGOHUD_CONFIG_FILE"
}

# Функция для очистки при выходе
cleanup() {
    echo
    echo "--- [$(date +%T)] Focus Worker stopping. Resetting FPS limit. ---"
    read_config # Читаем конфиг, чтобы получить последний активный лимит
    set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- ОСНОВНОЙ ЦИКЛ ---
CURRENT_GAME_PID=""
IS_GAME_FOCUSED=false

while true; do
    # Перечитываем конфиг на каждой итерации, чтобы подхватывать изменения из GUI
    read_config

    # Ищем запущенную игру из нашего списка (если список не пустой)
    FOUND_PID=""
    if [ -n "$GAMES_TO_WATCH_STR" ]; then
        FOUND_PID=$(pgrep -f -i "$GAMES_TO_WATCH_STR" | head -n1)
    fi

    if [ -n "$FOUND_PID" ]; then
        if [ "$FOUND_PID" != "$CURRENT_GAME_PID" ]; then
            CURRENT_GAME_PID=$FOUND_PID
            IS_GAME_FOCUSED=true # Считаем, что новая игра сразу в фокусе
            echo "[STATE] New game detected. PID: $CURRENT_GAME_PID. Assuming focus."
        fi

        ACTIVE_WINDOW_PID=$(kdotool getwindowpid $(kdotool getactivewindow) 2>/dev/null)

        if [ "$ACTIVE_WINDOW_PID" == "$CURRENT_GAME_PID" ]; then
            if ! $IS_GAME_FOCUSED; then
                echo "[EVENT] Game PID $CURRENT_GAME_PID GAINED focus."
                set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
                IS_GAME_FOCUSED=true
            fi
        else
            if $IS_GAME_FOCUSED; then
                echo "[EVENT] Game PID $CURRENT_GAME_PID LOST focus."
                set_global_mangohud_config "$FPS_LIMIT_INACTIVE"
                IS_GAME_FOCUSED=false
            fi
        fi
    elif [ -n "$CURRENT_GAME_PID" ]; then
        echo "[STATE] Game process PID $CURRENT_GAME_PID ended. Resetting global config."
        set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
        CURRENT_GAME_PID=""
        IS_GAME_FOCUSED=false
    fi

    sleep 1
done