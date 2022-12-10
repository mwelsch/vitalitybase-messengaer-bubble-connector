import asyncio
import configparser

from flask import Flask, jsonify, request

import authenticator
import telegram_model
from connector import TelegramConnector

tgconnector = TelegramConnector()
app = Flask(__name__)

##ToDo handle JSON requests with invalid fields

@app.route("/get_all_chats")
def get_all_chats():
    chats = {
        "telegram": tgconnector.get_all_chats(request)
    }
    return jsonify(chats)


"""
Sample good json for this
{
  "phone": "+4312345"
}
the above returns a phone_code_hash which has to be used in further requests:
{
  "phone": "+4312345",
  "code": "asdlkfj",
  "phone_code_hash": "..."
}
{
  "phone": "+4312345",
  "code": "65867",
  "password": "secret",
  "phone_code_hash": "05a798621f640c815c%"
}
"""
@app.route("/telegram_login", methods=["POST"])
def telegram_login():
    return tgconnector.login(request)


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
    tgconnector.send_text_to_chats(request)
    return "200"

"""
sample json to put here
{
  "clients": {
    "telegram":[-742914797]
  },
  "images": ["https://mir-s3-cdn-cf.behance.net/project_modules/fs/f40d9575646601.5c52392e99153.jpg", "https://i.imgur.com/bJj8eg2.jpg"],
  "message": "Some sample text"
}
"""
@app.route("/send_image_to_chats", methods=["POST"])
def send_image_to_chats():
    telegram_response = tgconnector.send_image_to_chats(request)
    if telegram_response != "200":
        return telegram_response
    return "200"


if __name__ == "__main__":
    # //ToDO do we need the debug flag to be true?!
    app.run(debug=False, host='0.0.0.0', port=5000)
