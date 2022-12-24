# the "sync" is marked as not used in pycharm - however it is needed; if not importet all telethon stuff will run async
import os.path
from telethon import functions, types, events
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
import wget
import hashlib
import logger


# Thanks to ChagtGPT for suggesting comments :)


class TelegramHandler:
    """
   Initializes a TelegramHandler object.

   Parameters:
   personal_id (str): The personal identifier for this handler.
   api_id (int): The API ID for the telegram API.
   api_hash (str): The API hash for the telegram API.
   loop (asyncio.AbstractEventLoop): The event loop for this handler.
   """

    def __init__(self, personal_id, api_id, api_hash, loop):
        # Create a new session file using the personal_id as a unique identifier
        session_file = hashlib.sha512(personal_id.encode()).hexdigest()
        # Initialize the TelegramClient object using the session file, api_id, and api_hash
        self.client = TelegramClient(session_file, api_id, api_hash, loop=loop)

    # Get a dictionary of chat names and IDs for all the chats in the user's account
    def get_chats(self):
        """
        Gets a list of chats available to this handler.

        Returns:
        dict: A dictionary with chat IDs as keys and chat names as values.
        """
        # Connect to the Telegram API if not already connected
        self._connect_if_not_connected()
        # //ToDo change to get_dialogs at some point
        # Get an iterator for all the chats in the user's account
        iter_dials = self.client.iter_dialogs()
        # Create an empty dictionary to store the chat IDs and names
        chats = {}
        # Iterate over the chats and add their names and IDs to the dictionary
        for dialog in iter_dials:
            if dialog.name != "":
                chats[str(dialog.id)] = dialog.name
        # Disconnect from the Telegram API
        self.client.disconnect()
        # Return the dictionary of chat IDs and names
        return chats

    # Send a text message to the specified clients
    def send_text_message(self, client_ids, text):
        logger.log("send_text_message")
        client_ids = self.check_client_ids_validity(client_ids)
        self._connect_if_not_connected()
        for id in client_ids:
            logger.log("sending" + str(id) + "Text: " + str(text))
            logger.log("Type of id: " + str(type(id)))
            self.client.send_message(id, text)
        self.client.disconnect()
        return "200"

    def send_images(self, client_ids, image_paths, caption_text):
        """
        Sends images to a list of clients.

        Parameters:
        client_ids (list): A list of client IDs to send the images to.
        image_paths (list): A list of local paths or URLs of the images to send.
        caption_text (str): The caption text to send with the images.

        Returns:
        str: "200" if the images were sent successfully.
        """
        logger.log("send_images")
        self._connect_if_not_connected()
        paths = self.convert_image_urls_to_local_paths(image_paths)
        client_ids = self.make_client_ids_valid(client_ids)
        for id in client_ids:
            # providing IDs as string does not seem to be an option. Fuck this
            self.client.send_file(int(id), paths, caption=caption_text)
        self.client.disconnect()
        # we delete all images afterwords. idk if this is a good idea, but I dont think we work with static files of similarely
        self.delete_all_images(paths)
        return "200"

    def login(self, phone_number, code=None, phone_code_hash=None, password=None):
        """
        Logs in the user.

        Parameters:
        phone_number (str): The phone number of the user.
        code (str, optional): The code sent to the user's phone.
        phone_code_hash (str, optional): The hash of the code sent to the user's phone.
        password (str, optional): The password of the user's account.

        Returns:
        str: "200" if login is successful, "phone_code_hash" if a code needs to be sent to the user's phone,
             "Probably wrong password" if the provided password is incorrect.
        """
        if code is None:
            self._connect_if_not_connected()
            phone_code_hash = {"phone_code_hash": self.client.send_code_request(phone_number).phone_code_hash}
            self.client.disconnect()
            return phone_code_hash
        try:
            self.client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            self.client.disconnect()
            return "200"
        except SessionPasswordNeededError:
            try:
                self.client.sign_in(password=password)
                self.client.disconnect()
                return "200"
            except Exception as error:
                self.client.disconnect()
                self.handle_unknown_error(error, self.login.__qualname__)
                return "Probably wrong password."

    def _connect_if_not_connected(self):
        """
        Connects to the client if it is not already connected
        """
        if not self.client.is_connected():
            self.client.connect()

    @staticmethod
    def convert_image_urls_to_local_paths(image_paths):
        """
       Converts a list of image URLs to local paths.

       Parameters:
       image_paths (list): A list of image URLs.

       Returns:
       list: A list of local paths corresponding to the image URLs.
       """
        paths = []
        for URL in image_paths:
            # using hashsum as valid file name
            file_path = hashlib.sha1(URL.encode()).hexdigest()
            # //ToDo probperly determine file extension via the header
            file_path += URL[URL.rindex("."):]
            try:
                response = wget.download(URL, file_path, bar=None)
                paths.append(file_path)
            except Exception as error:
                # Assuming its a local path. idk if this is a good idea
                print(error)
                print("Error... Assuming local path: " + str(URL))
                paths.append(URL)
        return paths

    def delete_all_images(self, paths):
        """
        Deletes all files at the provided local path

       Parameters:
       paths (list): A list of local paths.
        """
        for path in paths:
            if os.path.exists(path):
                os.remove(path)

    def is_user_authorized(self):
        """
        Checks if the user is authorized to Telegram

        Returns:
        boolean: Wheter the user is authorized
        """
        self._connect_if_not_connected()
        is_authorized = self.client.is_user_authorized()
        self.client.disconnect()
        return is_authorized

    @staticmethod
    def make_client_ids_valid(client_ids):
        client_ids = client_ids.split(",")
        logger.log("Trying to convert each id to an int. If failing it will stay as string")
        ids = []
        for id in client_ids:
            try:
                ids.append(int(id))
            except:
                ids.append(id)
        return ids

    def disconnect(self):
        self.client.disconnect()
