from mouse import Controller, Button, MouseListener
import Quartz
import time

'''
mouse = Controller()
# time.sleep(5)
# mouse.scroll(0, 100, steps=20)
# time.sleep(2)
# mouse.scroll(100, 0, steps=20)
time.sleep(5)
# mouse.click(Button.middle, 2)
mouse.position = (500, 50)
time.sleep(3)
mouse.drag(0, 500, Button.left)
# print(mouse.position)
'''


def moved(position):
    print(position)
    return True


def scrolled(position, dx, dy):
    print(position)
    return False


def clicked(position, x, y):
    print(y)


listener = MouseListener(on_click=clicked)
listener.start()
time.sleep(10)
listener.stop()
