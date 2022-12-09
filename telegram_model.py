# the "sync" is marked as not used in pycharm - however it is needed; if not importet all telethon stuff will run async
from telethon import functions, types, events
from telethon.sync import TelegramClient
import wget
import hashlib
import configparser

class TelegramHandler:
    def __init__(self, personal_id, api_id, api_hash, loop):

        session_file = hashlib.sha512(personal_id.encode()).hexdigest()
        self.client = TelegramClient(session_file, api_id, api_hash, loop=loop)
        self.client.start()

    """
    We need the follwoing stuff:
    TODO: refactor jsonstring to native dict type which can be dumped with json.dump
    chat name
    chat id
    """
    def GetChats(self):
        print("Getting chats")
        jsonstring = "{"
        iter_dials = self.client.iter_dialogs()
        for dialog in iter_dials:
            if dialog.name != "":
                jsonstring += "\n    "
                jsonstring += str(dialog.id)
                jsonstring += ": '"
                jsonstring += dialog.name
                jsonstring += "',"
        # remove last comma

        jsonstring = jsonstring[:len(jsonstring)-1]
        jsonstring += "\n}"
        print(jsonstring)
        return jsonstring

    """
    expecting client_ids as array of strings
    expecting text as string
    """
    def SendTextMessage(self, client_ids, text):
        for id in client_ids:
            self.client.send_message(id, text)

    """
    expecting client_ids as array of strings
    expecting image_path as string array with local paths or URLs - preferably full paths
    expecting caption_text as string
    """
    def SendImages(self, client_ids, image_paths, caption_text):
        actual_paths = []
        print("HEYHO")
        for URL in image_paths:
            print(URL)
            file_path = hashlib.sha1(URL.encode()).hexdigest()#using hash as valid file name
            print("FILE PATH:" + file_path)
            try:
                response = wget.download(URL, file_path)
                print("RESPONSE" + response)
            except Exception as error:
                self.client.disconnect() # stop database from locking?!
        #self.client.send_file(client_ids, image_paths, caption=caption_text)
        return "200"