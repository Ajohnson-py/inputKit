import Quartz
from mouse.button import Button
import time


# TODO: add error handling

class MouseController:
    """
    A macOS mouse controller using Quartz.

    This class allows fine-grained control over mouse input, including cursor movement,
    clicking, dragging, and scrolling. It is designed for accessibility tools,
    automation systems, or custom user interfaces that require programmatic mouse input.

    Features
    --------
    - Get and set the mouse cursor position.
    - Move the cursor smoothly over time.
    - Perform left, right, and middle clicks (single or multiple).
    - Simulate press and release of mouse buttons.
    - Perform smooth dragging with any mouse button.
    - Simulate horizontal and vertical scrolling.

    Notes
    -----
    All coordinates are specified in screen space (origin at top-left).
    This implementation is specific to macOS and depends on the Quartz CoreGraphics framework.
    """
    @property
    def position(self) -> tuple[float, float]:
        """
        Get the current position of the mouse cursor on the screen.

        Returns
        -------
        tuple of float
            The (x, y) coordinates of the mouse cursor in screen space.
        """
        event = Quartz.CGEventCreate(None)
        position = Quartz.CGEventGetLocation(event)
        return position.x, position.y

    @position.setter
    def position(self, coordinate_pair: tuple[float, float]):
        """
        Set the mouse cursor position on the screen.

        Parameters
        ----------
        coordinate_pair : tuple of float
            The (x, y) screen coordinates to move the mouse cursor to.
        """
        event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventMouseMoved, coordinate_pair, 0)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def move(self, dx: float, dy: float, steps=1, delay=0.005) -> None:
        """
        Move the mouse cursor by a relative offset.

        Parameters
        ----------
        dx : float
            The horizontal distance to move the cursor (positive is right, negative is left).
        dy : float
            The vertical distance to move the cursor (positive is down, negative is up).
        steps : int, optional
            The number of intermediate steps to smooth the movement. Default is 1 (no smoothing).
        delay : float, optional
            Delay in seconds between each step. Ignored if steps is 1. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        current_position = self.position

        for i in range(1, steps + 1):
            intermediate_x = current_position[0] + (dx * i / steps)
            intermediate_y = current_position[1] + (dy * i / steps)

            event = Quartz.CGEventCreateMouseEvent(
                None,
                Quartz.kCGEventMouseMoved,
                (intermediate_x, intermediate_y),
                0
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

            time.sleep(0 if steps == 1 else delay)

    def click(self, button: Button, count=1, delay=0.005) -> None:
        """
        Simulate mouse clicks at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to click. Supported values are:
                - button.py.left: Left-click
                - button.py.right: Right-click
                - button.py.middle: Middle-click
        count : int, optional
            Number of times to click. Use 2 for double-click, 3 for triple-click, etc. Default is 1.
        delay : float, optional
            Delay in seconds between each click. Ignored if count is 1. Default is 0.005 seconds.

        Notes
        -----
        Middle-click may have no effect in apps that do not support it natively.
        """
        current_position = self.position

        if button == Button.left:
            down_type = Quartz.kCGEventLeftMouseDown
            up_type = Quartz.kCGEventLeftMouseUp
            button_type = Quartz.kCGMouseButtonLeft
        elif button == Button.right:
            down_type = Quartz.kCGEventRightMouseDown
            up_type = Quartz.kCGEventRightMouseUp
            button_type = Quartz.kCGMouseButtonRight
        elif button == Button.middle:
            down_type = Quartz.kCGEventOtherMouseDown
            up_type = Quartz.kCGEventOtherMouseUp
            button_type = 2
        else:
            return

        for i in range(1, count + 1):
            event_down = Quartz.CGEventCreateMouseEvent(None, down_type, current_position, button_type)
            Quartz.CGEventSetIntegerValueField(event_down, Quartz.kCGMouseEventClickState, i)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

            event_up = Quartz.CGEventCreateMouseEvent(None, up_type, current_position, button_type)
            Quartz.CGEventSetIntegerValueField(event_up, Quartz.kCGMouseEventClickState, i)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

            time.sleep(0 if count == 1 else delay)

    def press(self, button: Button) -> None:
        """
        Simulate mouse button press at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to press. Supported values are:
                - button.py.left: Left-click
                - button.py.right: Right-click
                - button.py.middle: Middle-click
        """
        current_position = self.position

        if button == Button.left:
            down_type = Quartz.kCGEventLeftMouseDown
            button_type = Quartz.kCGMouseButtonLeft
        elif button == Button.right:
            down_type = Quartz.kCGEventRightMouseDown
            button_type = Quartz.kCGMouseButtonRight
        elif button == Button.middle:
            down_type = Quartz.kCGEventOtherMouseDown
            button_type = 2
        else:
            return

        event_down = Quartz.CGEventCreateMouseEvent(None, down_type, current_position, button_type)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

    def release(self, button: Button) -> None:
        """
        Simulate mouse button release at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to release. Supported values are:
                - button.py.left: Left-click
                - button.py.right: Right-click
                - button.py.middle: Middle-click
        """
        current_position = self.position

        if button == Button.left:
            up_type = Quartz.kCGEventLeftMouseUp
            button_type = Quartz.kCGMouseButtonLeft
        elif button == Button.right:
            up_type = Quartz.kCGEventRightMouseUp
            button_type = Quartz.kCGMouseButtonRight
        elif button == Button.middle:
            up_type = Quartz.kCGEventOtherMouseUp
            button_type = 2
        else:
            return

        event_up = Quartz.CGEventCreateMouseEvent(None, up_type, current_position, button_type)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

    def drag(self, dx: float, dy: float, button: Button, steps=20, delay=0.005) -> None:
        """
        Simulate mouse drag relative to current cursor position.

        Parameters
        ----------
        dx : float
            The horizontal distance to drag the cursor (positive is right, negative is left).
        dy : float
            The vertical distance to drag the cursor (positive is down, negative is up).
        button : Button
            The mouse button to use when dragging. Supported values are:
                - button.py.left: Left-click
                - button.py.right: Right-click
                - button.py.middle: Middle-click
        steps : int, optional
            The number of intermediate steps to smooth the movement. Default is 20 (some smoothing).
        delay : float, optional
            Delay in seconds between each step. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        current_position = self.position

        if button == Button.left:
            self.press(Button.left)
            drag_type = Quartz.kCGEventLeftMouseDragged
            button_type = Quartz.kCGMouseButtonLeft
        elif button == Button.right:
            self.press(Button.right)
            drag_type = Quartz.kCGEventRightMouseDragged
            button_type = Quartz.kCGMouseButtonRight
        elif button == Button.middle:
            self.press(Button.middle)
            drag_type = Quartz.kCGEventOtherMouseDragged
            button_type = 2
        else:
            return

        for i in range(1, steps + 1):
            intermediate_x = current_position[0] + (dx * i / steps)
            intermediate_y = current_position[1] + (dy * i / steps)

            event_drag = Quartz.CGEventCreateMouseEvent(
                None,
                drag_type,
                (intermediate_x, intermediate_y),
                button_type
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_drag)

            time.sleep(delay)

        if button == Button.left:
            self.release(Button.left)
        elif button == Button.right:
            self.release(Button.right)
        else:
            self.release(Button.middle)

    def scroll(self, dx: float, dy: float, steps=1, delay=0.005) -> None:
        """
        Simulate mouse scroll.

        Parameters
        ----------
        dx : float
            The horizontal distance to scroll (positive is left, negative is right).
        dy : float
            The vertical distance to scroll (positive is up, negative is down).
        steps : int, optional
            The number of intermediate steps to smooth the scroll. Default is 1 (no smoothing).
        delay : float, optional
            Delay in seconds between each step. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        intermediate_dx = dx / steps
        intermediate_dy = dy / steps

        for i in range(1, steps + 1):
            event = Quartz.CGEventCreateScrollWheelEvent(
                None,
                Quartz.kCGScrollEventUnitPixel,
                2,
                intermediate_dy,
                intermediate_dx
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

            time.sleep(0 if steps == 1 else delay)
