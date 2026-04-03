import asyncio
import os
import threading
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
import vk_api

# 🔑 ТОКЕНЫ (лучше вынести в ENV!)
TG_TOKEN = os.environ.get("TG_TOKEN")
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_CHAT_ID = int(os.environ.get("VK_CHAT_ID", 2000000002))
TG_CHAT_ID = int(os.environ.get("TG_CHAT_ID", -1000000000))
CONFIRMATION_TOKEN = os.environ.get("CONFIRMATION_TOKEN")

# --- Telegram ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# --- VK ---
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

# --- Flask ---
app = Flask(__name__)

# 📩 Telegram → VK
@dp.message()
async def tg_to_vk(message: types.Message):
    if not message.text:
        return

    name = message.from_user.first_name
    text = message.text

    try:
        vk.messages.send(
            peer_id=VK_CHAT_ID,
            message=f"{name}: {text}",
            random_id=0
        )
    except Exception as e:
        print("VK SEND ERROR:", e)


# 📩 VK → Telegram
@app.route("/", methods=["POST"])
def vk_callback():
    data = request.json

    if data["type"] == "confirmation":
        return CONFIRMATION_TOKEN

    if data["type"] == "message_new":
        msg = data["object"]["message"]
        text = msg.get("text", "")
        user_id = msg.get("from_id")

        if text:
            try:
                user = vk.users.get(user_ids=user_id)[0]
                name = user["first_name"]

                loop = asyncio.get_event_loop()
                loop.create_task(
                    bot.send_message(TG_CHAT_ID, f"{name}: {text}")
                )

            except Exception as e:
                print("TG SEND ERROR:", e)

        return "ok"

    return "ok"


# --- Запуск Flask ---
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)


# --- Запуск бота ---
def run_bot():
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        print("BOT ERROR:", e)


# --- MAIN ---
if __name__ == "__main__":
    # сначала бот в фоне
    threading.Thread(target=run_bot).start()

    # потом Flask (Render требует порт!)
    run_flask()
