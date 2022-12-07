import asyncio
from flask import Flask, jsonify, request
import telegram_model
app = Flask(__name__)
# This is ... working ... will change it in the future!
security_key = 'qwkjlasdifjpoasdfdlkasdf'

@app.route("/get_all_chats")
def get_all_chats():
    if request.headers["Secret-token"] == security_key:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        model = telegram_model.TelegramHandler(loop)
        return model.GetChats()
    return "Unauthorized"

@app.route("/send_text_to_chats", methods=["POST"])
def send_text_to_chats():
    ret = request.get_json()
    print(ret)
    return ret

@app.route("/send_image_to_chats", methods=["POST"])
def send_image_to_chats():
    model.SendImage([-742914797], "/home/moritz/Pictures/2022-04-16_9-14.png", "Test caption")
    return "Success... hopefully"