import Quartz
import time
from keyboard.key import Key
from keyboard.keymap import char_to_keycode


class KeyboardController:
    def press(self, key) -> None:
        if isinstance(key, str):
            keycode, needs_shift = char_to_keycode(key)

            event_down = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)

            if needs_shift:
                Quartz.CGEventSetFlags(event_down, Quartz.kCGEventFlagMaskShift)

            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
        elif isinstance(key, Key):
            event_down = Quartz.CGEventCreateKeyboardEvent(None, key.value, True)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

    def release(self, key) -> None:
        if isinstance(key, str):
            keycode, _ = char_to_keycode(key)

            event_up = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
        elif isinstance(key, Key):
            event_up = Quartz.CGEventCreateKeyboardEvent(None, key.value, False)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

    def tap(self, key) -> None:
        self.press(key)
        self.release(key)

    def type(self, text: str, delay=0.05) -> None:
        if isinstance(text, str):
            for char in text:
                self.tap(char)
                time.sleep(delay)
