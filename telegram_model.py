# the "sync" is marked as not used in pycharm - however it is needed; if not importet all telethon stuff will run async
import os.path
from telethon import functions, types, events
from telethon.sync import TelegramClient
import wget
import hashlib


class TelegramHandler:
    def __init__(self, personal_id, api_id, api_hash, loop):
        session_file = hashlib.sha512(personal_id.encode()).hexdigest()
        self.client = TelegramClient(session_file, api_id, api_hash, loop=loop)

    """
    We need the follwoing stuff:
    TODO: refactor jsonstring to native dict type which can be dumped with json.dump
    chat name
    chat id
    """

    def get_chats(self):
        if not self.client.is_connected():
            self.client.connect()
        iter_dials = self.client.iter_dialogs()
        # //ToDo work with dictionary rather than string
        jsonstring = "{"
        for dialog in iter_dials:
            if dialog.name != "":
                jsonstring += "\n    "
                jsonstring += str(dialog.id)
                jsonstring += ": '"
                jsonstring += dialog.name
                jsonstring += "',"
        # remove last comma
        jsonstring = jsonstring[:len(jsonstring) - 1]
        jsonstring += "\n}"
        print(jsonstring)
        self.client.disconnect()
        return jsonstring

    """
    expecting client_ids as array of strings
    expecting text as string
    """

    def send_text_message(self, client_ids, text):
        if not self.client.is_connected():
            self.client.connect()
        for id in client_ids:
            self.client.send_message(id, text)
        self.client.disconnect()

    """
    expecting client_ids as array of strings
    expecting image_path as string array with local paths or URLs - preferably full paths
    expecting caption_text as string
    """

    def send_images(self, client_ids, image_paths, caption_text):
        if not self.client.is_connected():
            self.client.connect()
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

        for id in client_ids:
            self.client.send_file(id, paths, caption=caption_text)
        self.client.disconnect()

        # we delete all images afterwords. idk if this is a good idea, but I dont think we work with static files of similarely
        for path in paths:
            if os.path.exists(path):
                os.remove(path)

        return "200"
