#!/bin/bash
# ===============================================================
#   Game Focus Manager - Worker Script
# ===============================================================

# --- ПУТИ И ПАРАМЕТРЫ ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PID_FILE="/tmp/game_focus_manager.pid"
LOG_FILE="/tmp/game_focus_manager.log" # <-- Путь к лог-файлу
GAMES_CONFIG_FILE="$SCRIPT_DIR/games.json"
MANGOHUD_CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/MangoHud/MangoHud.conf"

echo $$ > "$PID_FILE"
exec >> "$LOG_FILE" 2>&1

echo "--- [$(date +%T)] Focus Worker process started (PID: $$) ---"
echo "[INFO] Using config file at: $GAMES_CONFIG_FILE"

read_config() {
    if [ ! -f "$GAMES_CONFIG_FILE" ]; then
        echo "[ERROR] Config file not found. Exiting."
        rm -f "$PID_FILE"; exit 1;
    fi
    GAMES_TO_WATCH_STR=$(jq -r '.games_to_watch | join("|")' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_ACTIVE=$(jq -r '.fps_limit_active' "$GAMES_CONFIG_FILE")
    FPS_LIMIT_INACTIVE=$(jq -r '.fps_limit_inactive' "$GAMES_CONFIG_FILE")
}

set_global_mangohud_config() {
    local limit=$1
    touch "$MANGOHUD_CONFIG_FILE"
    sed -i '/^fps_limit=/d' "$MANGOHUD_CONFIG_FILE"
    echo "fps_limit=$limit" >> "$MANGOHUD_CONFIG_FILE"
    echo "[ACTION] [$(date +%T)] Set global fps_limit=$limit"
}

cleanup() {
    echo "--- [$(date +%T)] Focus Worker stopping. Resetting FPS limit. ---"
    read_config
    set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- ОСНОВНОЙ ЦИКЛ ---
CURRENT_GAME_PID=""
IS_GAME_FOCUSED=false

read_config
set_global_mangohud_config "$FPS_LIMIT_ACTIVE"

while true; do
    read_config

    FOUND_PID=$(pgrep -f -i "$GAMES_TO_WATCH_STR" | head -n1)

    if [ -n "$FOUND_PID" ]; then
        if [ "$FOUND_PID" != "$CURRENT_GAME_PID" ]; then
            CURRENT_GAME_PID=$FOUND_PID
            IS_GAME_FOCUSED=true
            echo "[STATE] [$(date +%T)] New game detected. PID: $CURRENT_GAME_PID"
        fi

        ACTIVE_WINDOW_PID=$(kdotool getwindowpid $(kdotool getactivewindow) 2>/dev/null)

        if [ "$ACTIVE_WINDOW_PID" == "$CURRENT_GAME_PID" ]; then
            if ! $IS_GAME_FOCUSED; then
                echo "[EVENT] [$(date +%T)] Game PID $CURRENT_GAME_PID GAINED focus."
                set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
                IS_GAME_FOCUSED=true
            fi
        else
            if $IS_GAME_FOCUSED; then
                echo "[EVENT] [$(date +%T)] Game PID $CURRENT_GAME_PID LOST focus."
                set_global_mangohud_config "$FPS_LIMIT_INACTIVE"
                IS_GAME_FOCUSED=false
            fi
        fi
    elif [ -n "$CURRENT_GAME_PID" ]; then
        echo "[STATE] [$(date +%T)] Game process PID $CURRENT_GAME_PID ended. Resetting."
        set_global_mangohud_config "$FPS_LIMIT_ACTIVE"
        CURRENT_GAME_PID=""
        IS_GAME_FOCUSED=false
    fi

    sleep 1
done