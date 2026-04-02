import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
import oc
import threading
import vk_api

# 🔑 ВСТАВЬ СЮДА
TG_TOKEN = "8684595244:AAEPmj5cWQRxidC8XnO2TrplHnDWhFDHeKU"
VK_TOKEN = "vk1.a.H7EvteHaCkF_RBHlEV59_Pktk17P9sq4-SerX1EqXmNTIOxRI7atijG_nlDcbj7ZFwGlqbS5k8o_7I3MbhObWEXiz0Ssp3LtR1XE6mnAQUpggxJmVBKsIvc4sMoJjzFm7zGvKuEjK0kPRhV48K_xtZG93IM00TX1d_T6WL71vUKmGwjaQlycCVlKMkW_m1MYHeirLb4md5b4DW99yoNozA"
VK_CHAT_ID = 2000000002  # ID беседы VK
TG_CHAT_ID = -3380376400  # ID чата Telegram
CONFIRMATION_TOKEN = "2d609c96"  # из VK

# --- Telegram ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()  # для aiogram v3+

# --- VK ---
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

# --- Flask ---
app = Flask(__name__)

# Telegram → VK
@dp.message()
async def tg_to_vk(message: types.Message):
    if not message.text:
        return
    name = message.from_user.first_name
    text = message.text

    vk.messages.send(
        peer_id=VK_CHAT_ID,
        message=f"Бот: {name}: {text}",
        random_id=0
    )

# VK → Telegram
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
            user = vk.users.get(user_ids=user_id)[0]
            name = user["first_name"]

            asyncio.run(bot.send_message(TG_CHAT_ID, f"Бот: {name}: {text}"))

        return "ok"
    return "ok"

# --- Запуск ---
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
