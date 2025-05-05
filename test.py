from mouse.listener import MouseListener
import time

'''
keyboard = KeyboardController()
time.sleep(3)
keyboard.press(Key.SHIFT)
time.sleep(3)
keyboard.release(Key.SHIFT)
'''


def on_move(position):
    print(f"Mouse moved to {position}")


def on_click(position, button, pressed):
    print(f"Mouse clicked at {position} with the {button} button, and pressed = {pressed}")


def on_scroll(position, dx, dy):
    print(f"Mouse scrolled at {position} by dx = {dx} and dy = {dy}")


time.sleep(3)
with MouseListener(on_move=on_move, on_scroll=on_scroll, on_click=on_click) as listener:
    listener.join()
