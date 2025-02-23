import os
import json
import requests
from datetime import datetime

CONFIG_FILE = "tg_config.json"

def load_or_create_config():
    """Завантажує або створює конфігураційний файл"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        print("Перший запуск. Введіть дані:")
        config = {
            "bot_token": input("Bot Token з @BotFather: ").strip(),
            "reports_left": 20,
            "last_report_date": None
        }
        save_config(config)
        return config

def save_config(config):
    """Зберігає конфігурацію у файл"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def get_target_info():
    """Отримує дані для скарги"""
    print("\n" + "="*40)
    target_type = input("Тип об'єкта (1 - канал, 2 - користувач): ").strip()
    target_id = input("ID або username цілі: ").strip()
    reason = input("Причина (spam/violence/pornography/illegal_drugs): ").strip()
    return target_type, target_id, reason

def send_report(config, target_type, target_id, reason):
    """Відправляє скаргу з правильними параметрами API"""
    url = f"https://api.telegram.org/bot{config['bot_token']}/reportChat"
    
    params = {"reason": reason}
    
    if target_type == "1":
        params["chat_id"] = target_id  # Для каналів/чатів
    else:
        params["user_id"] = target_id  # Для користувачів
    
    try:
        response = requests.post(url, json=params)
        result = response.json()
        
        if result.get("ok"):
            config["reports_left"] -= 1
            config["last_report_date"] = str(datetime.now())
            save_config(config)
        
        return result
    except Exception as e:
        return {"error": str(e)}

def main():
    config = load_or_create_config()
    
    if config["reports_left"] <= 0:
        print("Ліміт скарг вичерпано (20/добу)")
        return

    print(f"\nЗалишилось скарг: {config['reports_left']}")
    target_type, target_id, reason = get_target_info()
    
    result = send_report(config, target_type, target_id, reason)
    
    print("\nРезультат:")
    print(json.dumps(result, indent=2))
    
    if "error_code" in result.get("parameters", {}):
        print("\nПОМИЛКА API:", result["description"])

if __name__ == "__main__":
    print("УВАГА: Цей скрипт має обмеження 20 скарг/добу")
    print("Використовуйте тільки для законних цілей!\n")
    main()
