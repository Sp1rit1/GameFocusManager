#!/bin/bash
# ===============================================================
#   Game Focus Manager - Worker Script v6.0 (Reverse Logic Final)
#   - Reads config from local games.json.
#   - Determines the game by checking the active window first to
#     reliably handle multi-process games like CS2.
# ===============================================================

# --- ОПРЕДЕЛЯЕМ ПУТЬ К САМОМУ СКРИПТУ ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# --- ПУТИ И ПАРАМЕТРЫ ---
PID_FILE="/tmp/game_focus_manager.pid"
LOG_FILE="/tmp/game_focus_manager.log"
# Конфиг теперь ищется рядом со скриптом
GAMES_CONFIG_FILE="$SCRIPT_DIR/games.json"
MANGOHUD_CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/MangoHud/MangoHud.conf"

# --- ИНИЦИАЛИЗАЦИЯ ---
echo $$ > "$PID_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "--- [$(date +%T)] Focus Worker process started (PID: $$) ---"
echo "[INFO] Using config file at: $GAMES_CONFIG_FILE"

# Функция для чтения параметров из JSON
read_config() {
    if [ ! -f "$GAMES_CONFIG_FILE" ]; then
        echo "[ERROR] Config file not found at $GAMES_CONFIG_FILE. Exiting."
        rm -f "$PID_FILE"; exit 1;
    fi
    # Читаем массив игр в формате, понятном для grep (например, "dota2|witcher3.exe|cs2")
    GAMES_TO_WATCH_STR=$(jq -r '.games_to_watch | join("|")' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_ACTIVE=$(jq -r '.fps_limit_active' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_INACTIVE=$(jq -r '.fps_limit_inactive' "$GAMES_CONFIG_FILE")
}

# Функция для изменения ЕДИНОГО конфиг-файла MangoHud
set_global_mangohud_config() {
    local limit=$1
    touch "$MANGOHUD_CONFIG_FILE"
    sed -i '/^fps_limit=/d' "$MANGOHUD_CONFIG_FILE"
    echo "fps_limit=$limit" >> "$MANGOHUD_CONFIG_FILE"
    echo "[ACTION] [$(date +%T)] Set global fps_limit=$limit"
}

# Функция для очистки при выходе
cleanup() {
    echo "--- [$(date +%T)] Focus Worker stopping. Resetting FPS limit. ---"
    read_config
    set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- НОВАЯ, ОБРАТНАЯ ЛОГИКА ЦИКЛА ---

IS_GAME_FOCUSED=false

# Сбрасываем лимит при старте
read_config
set_global_mangohud_config "$FPS_LIMIT_ACTIVE"

while true; do
    # Перечитываем конфиг на каждой итерации
    read_config

    # Шаг 1: Получаем PID активного в данный момент окна
    ACTIVE_WINDOW_PID=$(kdotool getwindowpid $(kdotool getactivewindow) 2>/dev/null)

    # Шаг 2: Проверяем, является ли команда, запустившая этот PID, одной из наших игр
    # Мы используем 'ps ...' для получения имени процесса по PID.
    if [ -n "$ACTIVE_WINDOW_PID" ] && ps -p "$ACTIVE_WINDOW_PID" -o cmd= | grep -qE "$GAMES_TO_WATCH_STR"; then
        # ОКНО В ФОКУСЕ - ЭТО ИГРА
        if ! $IS_GAME_FOCUSED; then
            echo "[EVENT] [$(date +%T)] Game process (PID: $ACTIVE_WINDOW_PID) GAINED focus."
            set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
            IS_GAME_FOCUSED=true
        fi
    else
        # ОКНО В ФОКУСЕ - ЭТО НЕ ИГРА (или kdotool вернул пустой PID)
        if $IS_GAME_FOCUSED; then
            echo "[EVENT] [$(date +%T)] Game window LOST focus."
            set_global_mangohud_config "$FPS_LIMIT_INACTIVE"
            IS_GAME_FOCUSED=false
        fi
    fi

    sleep 1
done