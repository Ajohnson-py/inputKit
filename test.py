from mouse import Controller, Button
import time

mouse = Controller()
time.sleep(5)
mouse.scroll(0, 100, steps=20)
time.sleep(2)
mouse.scroll(100, 0, steps=20)
#time.sleep(5)
#mouse.click(Button.middle, 2)
#mouse.position = (500, 50)
#time.sleep(3)
#mouse.drag(0, 500, Button.left)
#print(mouse.position)