import asyncio
import configparser

from flask import Flask, jsonify, request

import authenticator
import telegram_model

def parse_config():
    global telegram_api_id, telegram_api_hash, whitelist_enbaled, whitelist_members
    config = configparser.ConfigParser()
    config.read("config")
    telegram_api_id = int(config["Telegram"]["api_id"])
    telegram_api_hash = config["Telegram"]["api_hash"]
    whitelist_enbaled = config["DEFAULT"].getboolean("personal-id-whitelist")
    if whitelist_enbaled:
        whitelist_members = authenticator.get_whitelist_members()



parse_config()
app = Flask(__name__)



@app.route("/get_all_chats")
def get_all_chats():
    try:
        personal_id = request.headers["Personal-ID"]
        if whitelist_enbaled:
            if personal_id not in whitelist_members:
                raise Exception("Not a member of whitelist")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        model = telegram_model.TelegramHandler(personal_id, telegram_api_id, telegram_api_hash, loop)
        return model.GetChats()
    except Exception as error:
        return error


"""
Sample good json for this
{
  "clients": {
    "telegram":[-742914797]
  },
  "message": "Some sample text"
}
"""
@app.route("/send_text_to_chats", methods=["POST"])
def send_text_to_chats():
    if request.headers["Secret-token"] == security_key:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            model = telegram_model.TelegramHandler(loop)
            ret = request.get_json()
            model.SendTextMessage(ret["clients"]["telegram"],ret["message"])
            return "200"
        except Exception as error:
            return str(error)
    return "Unauthorized"


@app.route("/send_image_to_chats", methods=["POST"])
def send_image_to_chats():
    print("1")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        model = telegram_model.TelegramHandler(loop)
        ret = request.get_json()
        print("2")
        model.SendImages(ret["clients"]["telegram"],ret["images"],ret["message"])
    except Exception as error:
        print("3")
        print(error)
        return str(error)
    return "Success... hopefully"


