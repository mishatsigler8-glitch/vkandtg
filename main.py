from aiogram import Bot, Dispatcher, types
from flask import Flask, request
import vk_api
import asyncio

TG_TOKEN = "TG_TOKEN"
VK_TOKEN = "VK_TOKEN"
VK_CHAT_ID = 2000000001  # беседа VK
TG_CHAT_ID = -1001234567890  # чат/канал Telegram

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

app = Flask(__name__)

# ---------- Telegram → VK ----------
@dp.message_handler()
async def tg_to_vk(message: types.Message):
    name = message.from_user.first_name
    text = message.text

    vk.messages.send(
        peer_id=VK_CHAT_ID,
        message=f"Бот: {name}: {text}",
        random_id=0
    )

# ---------- VK → Telegram ----------
@app.route("/", methods=["POST"])
def vk_callback():
    data = request.json

    if data["type"] == "message_new":
        msg = data["object"]["message"]
        text = msg["text"]
        user_id = msg["from_id"]

        user = vk.users.get(user_ids=user_id)[0]
        name = user["first_name"]

        asyncio.run(
            bot.send_message(
                TG_CHAT_ID,
                f"Бот: {name}: {text}"
            )
        )

    return "ok"

# ---------- запуск ----------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    app.run(port=5000)