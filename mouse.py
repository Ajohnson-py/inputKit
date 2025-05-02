from Quartz.CoreGraphics import (
    CGEventCreate, CGEventGetLocation, CGEventCreateMouseEvent,
    kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp,
    kCGEventLeftMouseDragged, kCGEventRightMouseDown, kCGEventRightMouseUp,
    kCGEventRightMouseDragged, kCGMouseButtonLeft, kCGMouseButtonRight,
    CGEventPost, kCGHIDEventTap, CGEventSetIntegerValueField,
    kCGMouseEventClickState
)
from enum import Enum
import time


# TODO: add documentation and error handling


class Button(Enum):
    left = 1
    right = 2
    middle = 3


class Controller:
    @property
    def position(self) -> tuple[float, float]:
        event = CGEventCreate(None)
        position = CGEventGetLocation(event)
        return position.x, position.y

    @position.setter
    def position(self, coordinate_pair: tuple[float, float]):
        event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, coordinate_pair, 0)
        CGEventPost(kCGHIDEventTap, event)

    def move(self, dx: float, dy: float, steps=1, delay=0.0005) -> None:
        current_position = self.position

        for i in range(1, steps + 1):
            intermediate_x = current_position[0] + (dx * i / steps)
            intermediate_y = current_position[1] + (dy * i / steps)

            event = CGEventCreateMouseEvent(
                None,
                kCGEventMouseMoved,
                (intermediate_x, intermediate_y),
                0
            )
            CGEventPost(kCGHIDEventTap, event)

            time.sleep(0 if steps == 1 else delay)

    def click(self, button: Button, count=1) -> None:
        current_position = self.position

        if button == Button.left:
            down_type = kCGEventLeftMouseDown
            up_type = kCGEventLeftMouseUp
            button_type = kCGMouseButtonLeft
        elif button == Button.right:
            down_type = kCGEventRightMouseDown
            up_type = kCGEventRightMouseUp
            button_type = kCGMouseButtonRight
        else:
            return

        for i in range(1, count + 1):
            event_down = CGEventCreateMouseEvent(None, down_type, current_position, button_type)
            CGEventSetIntegerValueField(event_down, kCGMouseEventClickState, i)
            CGEventPost(kCGHIDEventTap, event_down)

            event_up = CGEventCreateMouseEvent(None, up_type, current_position, button_type)
            CGEventSetIntegerValueField(event_up, kCGMouseEventClickState, i)
            CGEventPost(kCGHIDEventTap, event_up)

            time.sleep(0 if count == 1 else 0.005)

    def press(self, button: Button) -> None:
        current_position = self.position

        if button == Button.left:
            event_down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, current_position, kCGMouseButtonLeft)
            CGEventPost(kCGHIDEventTap, event_down)

        elif button == Button.right:
            event_down = CGEventCreateMouseEvent(None, kCGEventRightMouseDown, current_position, kCGMouseButtonRight)
            CGEventPost(kCGHIDEventTap, event_down)

    def release(self, button: Button) -> None:
        current_position = self.position

        if button == Button.left:
            event_up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, current_position, kCGMouseButtonLeft)
            CGEventPost(kCGHIDEventTap, event_up)

        elif button == Button.right:
            event_up = CGEventCreateMouseEvent(None, kCGEventRightMouseUp, current_position, kCGMouseButtonRight)
            CGEventPost(kCGHIDEventTap, event_up)

    def drag(self, dx: float, dy: float, button: Button, steps=20, delay=0.005) -> None:
        # NOTE: for large dx and dy, use more steps to increase accuracy
        current_position = self.position

        if button == Button.left:
            self.press(Button.left)
            drag_type = kCGEventLeftMouseDragged
            button_type = kCGMouseButtonLeft
        elif button == Button.right:
            self.press(Button.right)
            drag_type = kCGEventRightMouseDragged
            button_type = kCGMouseButtonRight
        else:
            return

        for i in range(1, steps + 1):
            intermediate_x = current_position[0] + (dx * i / steps)
            intermediate_y = current_position[1] + (dy * i / steps)

            event_drag = CGEventCreateMouseEvent(
                None,
                drag_type,
                (intermediate_x, intermediate_y),
                button_type
            )
            CGEventPost(kCGHIDEventTap, event_drag)

            time.sleep(delay)

        self.release(Button.left)
