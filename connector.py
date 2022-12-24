import asyncio
import configparser
import json

from telethon.errors import SessionPasswordNeededError

import logger
import telegram_model


class TelegramConnector:
    def __init__(self):
        self.parse_config()

    def parse_config(self):
        """
        Parses the config file and stores the required values in the object
        """
        self.config = configparser.ConfigParser()
        self.config.read("config")
        self.telegram_api_id = self.config["Telegram"]["api_id"]
        self.telegram_api_hash = self.config["Telegram"]["api_hash"]
        self.whitelist_enbaled = self.config["DEFAULT"].getboolean("personal-id-whitelist")
        if self.whitelist_enbaled:
            self.whitelist_members = get_whitelist_members()

    def personal_id_authorized(self, personal_id):
        """
        Checks if the provided personal_id is authorized to use the service

        Parameters:
        personal_id (str): The personal_id to be checked

        Returns:
        bool: True if the personal_id is authorized, False otherwise
        """
        if self.whitelist_enbaled:
            if personal_id not in self.whitelist_members:
                return False
        return True

    def login(self, request):
        """
        Handles a login request

        Parameters:
        request (flask.Request): The request object containing the login data

        Returns:
        str: The status of the request. This can be a success message or an error message.
        dict: with the phone_code_hash which is required for further logins
        """
        try:
            # Get the personal_id from the request header
            personal_id = request.headers["Personal-ID"]
            # Check if the personal_id is authorized
            if not self.personal_id_authorized(personal_id):
                return "Unauthorized. Guess this is an API-ID/Hash issue"
            # Initialize the telegram model
            model = self._initialize_model_w_loop(personal_id)
            # If the user is already authorized, return a message indicating so
            if model.is_user_authorized():
                return "Already logged in"
            # Parse the login data from the request body
            ret = request.get_json()
            phone_number = ret['phone']
            # Handle login request without code provided. Asking to send code to phone
            if 'code' not in ret:
                return model.login(phone_number)
            # Login with code provided
            code = ret['code']
            phone_code_hash = ret['phone_code_hash']
            if 'password' in ret:
                password = ret['password']
                return model.login(phone_number, code, phone_code_hash, password)
            return model.login(phone_number, code, phone_code_hash)
        except Exception as error:
            # If the error is a KeyError, the request header is probably missing the personal_id
            if isinstance(error, KeyError):
                return "KeyError. Probably no 'Personal-ID' header was provided."
            return self.handle_unknown_error(error, self.login.__qualname__)

    def get_all_chats(self, request):
        try:
            model = self._initialize_model(request)
            if isinstance(model, str):
                return model
            chats = model.get_chats()
            return chats
        except Exception as error:
            return self.handle_unknown_error(error, self.get_all_chats.__qualname__)

    def send_text_to_chats(self, request):
        try:
            # initialize the telegram model
            logger.log("initializing")
            model = self._initialize_model(request)
            # if an error occured a string is returned.
            if isinstance(model, str):
                logger.log("model is instance of str")
                return model
            # parse json
            logger.log("Calling sendtxtmsgs")
            ret = request.get_json()
            # tell model to send messages
            logger.log("Calling sendtxtmsgs")
            logger.log("Json i got:")
            logger.log(json.dumps(ret))
            model.send_text_message(ret["clients"]["telegram"], ret["message"])
            return "200"
        except Exception as error:
            return self.handle_unknown_error(error, self.send_text_to_chats.__qualname__)

    def _initialize_model(self, request):
        try:
            #Get identifier. This raises a KeyError if no id is provided
            personal_id = request.headers["Personal-ID"]
            #Check if id is authorized
            if not self.personal_id_authorized(personal_id):
                return "Unauthorized"
            #Create a new model
            model = self._initialize_model_w_loop(personal_id)
            if model.is_user_authorized():
                return model
            return "The telegram user is not authorized. Probably you need to login with /telegram_login. "
        except Exception as error:
            if isinstance(error, KeyError):
                return "KeyError. Proably no 'Personal-ID' header was provided. The error was logged to the output of the server"
            return self.handle_unknown_error(error, self._initialize_model.__qualname__)

    def _initialize_model_w_loop(self, personal_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        model = telegram_model.TelegramHandler(personal_id, self.telegram_api_id, self.telegram_api_hash, loop)
        return model

    def send_image_to_chats(self, request):
        try:
            # initialize the telegram model
            model = self._initialize_model(request)
            # if an error occured a string is returned.
            if isinstance(model, str):
                return model
            # parse json
            ret = request.get_json()
            # tell model to send images
            client_ids = ret["clients"]["telegram"]
            image_array = ret["images"]
            image_caption = ret["message"]
            model.send_images(client_ids, image_array , image_caption)
            return "200"
        except Exception as error:
            return self.handle_unknown_error(error, self.send_image_to_chats.__qualname__)

    @staticmethod
    def handle_unknown_error(error, location):
        print("Error Details:")
        print(error)
        print(type(error))
        print("Location Details:")
        print(location)
        # //ToDo log unhandled errors somewhere
        return "Some unhandled error. Please contact admin"

"""
Reads the "whitelist" file and returns an array containing strings with each line, the new line character is stripeed
"""
def get_whitelist_members():
    f = open("whitelist", "r")
    lines = f.readlines()
    whitelist_members = []
    for line in lines:
        line = line.replace("\n", "")
        whitelist_members.append(line)
    return whitelist_members
