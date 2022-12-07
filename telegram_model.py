
from telethon import functions, types, events
from telethon.sync import TelegramClient


class TelegramHandler:
    def __init__(self, loop):
        

        self.client = TelegramClient('session_file', api_id, api_hash, loop=loop)
        self.client.start()

    """
    We need the follwoing stuff:
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
    expecting image_path as local path - preferably full paths
    expecting caption_text as string
    """
    def SendImage(self, client_ids, image_path, caption_text):
        for id in client_ids:
            self.client.send_file(id, image_path, caption=caption_text)