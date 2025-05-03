import Quartz
import threading
from enum import Enum
import time


# TODO: add error handling


class Button(Enum):
    left = 0
    right = 1
    middle = 2


class Controller:
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
    All coordinates are specified in screen space (origin at bottom-left).
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
                - Button.left: Left-click
                - Button.right: Right-click
                - Button.middle: Middle-click
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
                - Button.left: Left-click
                - Button.right: Right-click
                - Button.middle: Middle-click
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
                - Button.left: Left-click
                - Button.right: Right-click
                - Button.middle: Middle-click
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
                - Button.left: Left-click
                - Button.right: Right-click
                - Button.middle: Middle-click
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


class MouseListener:
    """
    Listens for global mouse events on macOS using Quartz.

    Supports mouse movement, button clicks, and scroll events. Event handlers
    can be passed in for each type of event. Returning `False` from a handler
    blocks further propagation of the event.

    This class can be used as a context manager (with the `with` statement) or
    managed manually using `start()` and `stop()`.

    Parameters
    ----------
    on_move : Callable[[tuple[float, float]], Optional[bool]], optional
        Function called when the mouse moves. Receives (x, y) coordinates.
    on_click : Callable[[tuple[float, float], str, bool], Optional[bool]], optional
        Function called on mouse button press/release. Receives (x, y), button name, and pressed state.
    on_scroll : Callable[[tuple[float, float], int, int], Optional[bool]], optional
        Function called on scroll events. Receives (x, y), dx, and dy scroll deltas.
    """

    def __init__(self, on_move=None, on_click=None, on_scroll=None):
        self.on_move = on_move
        self.on_click = on_click
        self.on_scroll = on_scroll
        self.tap = None
        self.source = None
        self._thread = None
        self._running = False

    def _callback(self, proxy, event_type, event, refcon):
        """
        Internal callback invoked for each intercepted mouse event.
        Dispatches to the appropriate handler (move, click, scroll).
        """
        loc = Quartz.CGEventGetLocation(event)

        if event_type == Quartz.kCGEventMouseMoved and self.on_move:
            should_propagate = self.on_move((loc.x, loc.y))
            if should_propagate is False:
                return None  # Block the event

        elif event_type in (Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp,
                            Quartz.kCGEventRightMouseDown, Quartz.kCGEventRightMouseUp,
                            Quartz.kCGEventOtherMouseDown, Quartz.kCGEventOtherMouseUp
                            ):
            if self.on_click:
                button_number = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGMouseEventButtonNumber)
                button = {0: "left", 1: "right", 2: "middle"}.get(button_number, f"button{button_number}")
                pressed = event_type in (Quartz.kCGEventLeftMouseDown, Quartz.kCGEventRightMouseDown)
                should_propagate = self.on_click((loc.x, loc.y), button, pressed)
                if should_propagate is False:
                    return None

        elif event_type == Quartz.kCGEventScrollWheel and self.on_scroll:
            dy = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis1)
            dx = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis2)
            should_propagate = self.on_scroll((loc.x, loc.y), dx, dy)
            if should_propagate is False:
                return None

        return event  # Allow the event through

    def __enter__(self):
        """
        Initializes the event tap and starts listening.
        Used when entering a context block.
        """
        self._setup()
        return self

    def __exit__(self, *args):
        """
        Initializes the event tap and starts listening.
        Used when entering a context block.
        """
        self.stop()

    def _setup(self):
        """
        Sets up the Quartz event tap and registers it with the run loop.
        """
        event_mask = (
                Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved) |
                Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown) |
                Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseUp) |
                Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDown) |
                Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseUp) |
                Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseDown) |
                Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseUp) |
                Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel)
        )
        self.tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            self._callback,
            None
        )
        if not self.tap:
            raise RuntimeError("Failed to create event tap.")
        self.source = Quartz.CFMachPortCreateRunLoopSource(None, self.tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), self.source, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(self.tap, True)

    def start(self):
        """
        Starts the mouse listener in a background thread.
        """
        if self._running:
            return
        self._running = True

        def run():
            self.__enter__()
            Quartz.CFRunLoopRun()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stops the run loop and disables the event tap.
        """
        if self._running:
            Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())
            self._running = False
            self._thread.join()
            self._thread = None

    def join(self):
        """
        Blocks the current thread until the run loop is stopped.
        """
        Quartz.CFRunLoopRun()
