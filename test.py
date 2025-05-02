from mouse import Controller, Button
import time

mouse = Controller()
#time.sleep(5)
#mouse.click(Button.left, 2)
mouse.position = (500, 50)
time.sleep(3)
mouse.drag(0, 500, Button.right)
print(mouse.position)