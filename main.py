import asyncio
import os
import threading
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
import vk_api

# 🔑 ТОКЕНЫ (лучше вынести в ENV!)
TG_TOKEN = "8684595244:AAEPmj5cWQRxidC8XnO2TrplHnDWhFDHeKU"
VK_TOKEN = "vk1.a.H7EvteHaCkF_RBHlEV59_Pktk17P9sq4-SerX1EqXmNTIOxRI7atijG_nlDcbj7ZFwGlqbS5k8o_7I3MbhObWEXiz0Ssp3LtR1XE6mnAQUpggxJmVBKsIvc4sMoJjzFm7zGvKuEjK0kPRhV48K_xtZG93IM00TX1d_T6WL71vUKmGwjaQlycCVlKMkW_m1MYHeirLb4md5b4DW99yoNozA"
VK_CHAT_ID = 2000000002
TG_CHAT_ID = -3380376400
CONFIRMATION_TOKEN = "22aa14be"

# --- Telegram ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# --- VK ---
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

# --- Flask ---
app = Flask(__name__)
print("VK EVENT:", data)

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
    print("VK EVENT:", data)


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
