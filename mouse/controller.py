import Quartz
from mouse.button import Button
import time


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

    def __init__(self):
        """
        Initialize the MouseController by ensuring system requirements are met.
        """
        self._screen_bounds = self._get_screen_bounds()
        self._validate_system_access()

    def _get_screen_bounds(self) -> tuple[float, float]:
        """Get the screen dimensions for validation."""
        try:
            main_display = Quartz.CGMainDisplayID()
            bounds = Quartz.CGDisplayBounds(main_display)
            return bounds.size.width, bounds.size.height
        except Exception as e:
            return float('inf'), float('inf')  # Allow any coordinates if bounds unknown

    def _validate_system_access(self) -> None:
        """
        Validate that the application has necessary permissions.

        Raises
        ------
        PermissionError
            If system access is denied or insufficient permissions.
        """
        try:
            # Test basic mouse access by getting current position
            test_event = Quartz.CGEventCreate(None)
            if test_event is None:
                raise PermissionError(
                    "Unable to create mouse events. This may indicate insufficient permissions. "
                    "On macOS 10.14+, grant accessibility permissions in System Settings > "
                    "Security & Privacy > Accessibility."
                )
        except Exception as e:
            raise PermissionError(f"System access validation failed: {e}")

    def _validate_button(self, button) -> None:
        """
        Validate that the button parameter is valid.

        Raises
        ------
        TypeError
            If button is not a Button enum.
        """
        if not isinstance(button, Button):
            raise TypeError(f"Invalid button type: {type(button)}. Must be Button enum.")

    def _validate_steps(self, steps):
        if not isinstance(steps, int) or steps < 1:
            raise TypeError(f"Invalid steps type: {type(steps)}. Must be an integer greater than 0.")

    def _validate_delay(self, delay):
        if not isinstance(delay, (int, float)) or delay < 0:
            raise TypeError(f"Invalid delay type: {type(delay)}. Must be an integer or float greater than 0.")

    def _validate_coordinates(self, x, y) -> None:
        """
        Validate that coordinates are within screen bounds.

        Raises
        ------
        TypeError
            If coordinates are not numeric.
        ValueError
            If coordinates are negative or outside screen bounds.
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Coordinates must be numeric values")

        if x < 0 or y < 0:
            raise ValueError(f"Coordinates cannot be negative: ({x}, {y})")

        screen_width, screen_height = self._screen_bounds
        if x > screen_width or y > screen_height:
            raise ValueError(
                f"Coordinates ({x}, {y}) exceed screen bounds ({screen_width}x{screen_height})"
            )

    @property
    def position(self) -> tuple[float, float]:
        """
        Get the current position of the mouse cursor on the screen.

        Returns
        -------
        tuple of float
            The (x, y) coordinates of the mouse cursor in screen space.
        """
        try:
            event = Quartz.CGEventCreate(None)
            if event is None:
                raise RuntimeError("Unable to create event to get mouse position")

            position = Quartz.CGEventGetLocation(event)
            return float(position.x), float(position.y)
        except Exception as e:
            raise RuntimeError(f"Failed to get mouse position: {e}")

    @position.setter
    def position(self, coordinate_pair: tuple[float | int, float | int]):
        """
        Set the mouse cursor position on the screen.

        Parameters
        ----------
        coordinate_pair : tuple of float
            The (x, y) screen coordinates to move the mouse cursor to.
        """
        if not isinstance(coordinate_pair, (tuple, list)) or len(coordinate_pair) != 2:
            raise TypeError("coordinate_pair must be a tuple/list of 2 numeric values")

        x, y = coordinate_pair
        self._validate_coordinates(x, y)

        try:
            event = Quartz.CGEventCreateMouseEvent(
                None,
                Quartz.kCGEventMouseMoved,
                (float(x), float(y)),
                0
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        except Exception as e:
            raise RuntimeError(f"Failed to set mouse position to ({x}, {y}): {e}")

    def move(self, dx: float | int, dy: float | int, steps=1, delay=0.005) -> None:
        """
        Move the mouse cursor by a relative offset.

        Parameters
        ----------
        dx : float or int
            The horizontal distance to move the cursor (positive is right, negative is left).
        dy : float or int
            The vertical distance to move the cursor (positive is down, negative is up).
        steps : int, optional
            The number of intermediate steps to smooth the movement. Default is 1 (no smoothing).
        delay : float or int, optional
            Delay in seconds between each step. Ignored if steps is 1. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            raise TypeError("dx and dy must be numeric values")
        self._validate_steps(steps)
        self._validate_delay(delay)

        try:
            current_x, current_y = self.position
            target_x, target_y = current_x + dx, current_y + dy

            # Clamp the target coordinates to screen bounds
            target_x = max(0, min(target_x, self._screen_bounds[0]))
            target_y = max(0, min(target_y, self._screen_bounds[1]))

            # Calculate deltas after clamping
            dx = target_x - current_x
            dy = target_y - current_y

            for i in range(1, steps + 1):
                intermediate_x = current_x + (dx * i / steps)
                intermediate_y = current_x + (dy * i / steps)

                event = Quartz.CGEventCreateMouseEvent(
                    None,
                    Quartz.kCGEventMouseMoved,
                    (intermediate_x, intermediate_y),
                    0
                )
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

                if steps > 1:
                    time.sleep(delay)
        except Exception as e:
            raise RuntimeError(f"Failed to move mouse by ({dx}, {dy}): {e}")

    def click(self, button: Button, count=1, delay=0.005) -> None:
        """
        Simulate mouse clicks at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to click. Supported values are:
                - Button.LEFT: Left-click
                - Button.RIGHT: Right-click
                - Button.MIDDLE: Middle-click
        count : int, optional
            Number of times to click. Use 2 for double-click, 3 for triple-click, etc. Default is 1.
        delay : float or int, optional
            Delay in seconds between each click. Ignored if count is 1. Default is 0.005 seconds.

        Notes
        -----
        Middle-click may have no effect in apps that do not support it natively.
        """
        current_position = self.position

        if count is int and count <= 0:
            raise TypeError(f"Invalid count type: {type(count)}. Count must be a positive integer.")
        self._validate_button(button)
        self._validate_delay(delay)

        try:
            if button == Button.LEFT:
                down_type = Quartz.kCGEventLeftMouseDown
                up_type = Quartz.kCGEventLeftMouseUp
                button_type = Quartz.kCGMouseButtonLeft
            elif button == Button.RIGHT:
                down_type = Quartz.kCGEventRightMouseDown
                up_type = Quartz.kCGEventRightMouseUp
                button_type = Quartz.kCGMouseButtonRight
            elif button == Button.MIDDLE:
                down_type = Quartz.kCGEventOtherMouseDown
                up_type = Quartz.kCGEventOtherMouseUp
                button_type = 2

            for i in range(1, count + 1):
                event_down = Quartz.CGEventCreateMouseEvent(None, down_type, current_position, button_type)
                Quartz.CGEventSetIntegerValueField(event_down, Quartz.kCGMouseEventClickState, i)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

                event_up = Quartz.CGEventCreateMouseEvent(None, up_type, current_position, button_type)
                Quartz.CGEventSetIntegerValueField(event_up, Quartz.kCGMouseEventClickState, i)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

                time.sleep(0 if count == 1 else delay)
        except Exception as e:
            raise RuntimeError(f"Failed to click at ({current_position[0]}, {current_position[1]}): {e}")

    def press(self, button: Button) -> None:
        """
        Simulate mouse button press at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to press. Supported values are:
                - Button.LEFT: Left-click
                - Button.RIGHT: Right-click
                - Button.MIDDLE: Middle-click
        """
        self._validate_button(button)

        current_position = self.position

        try:
            if button == Button.LEFT:
                down_type = Quartz.kCGEventLeftMouseDown
                button_type = Quartz.kCGMouseButtonLeft
            elif button == Button.RIGHT:
                down_type = Quartz.kCGEventRightMouseDown
                button_type = Quartz.kCGMouseButtonRight
            elif button == Button.MIDDLE:
                down_type = Quartz.kCGEventOtherMouseDown
                button_type = 2

            event_down = Quartz.CGEventCreateMouseEvent(None, down_type, current_position, button_type)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
        except Exception as e:
            raise RuntimeError(f"Failed to press button at ({current_position[0]}, {current_position[1]}): {e}")

    def release(self, button: Button) -> None:
        """
        Simulate mouse button release at the current cursor position.

        Parameters
        ----------
        button : Button
            The mouse button to release. Supported values are:
                - Button.LEFT: Left-click
                - Button.RIGHT: Right-click
                - Button.MIDDLE: Middle-click
        """
        self._validate_button(button)

        current_position = self.position

        try:
            if button == Button.LEFT:
                up_type = Quartz.kCGEventLeftMouseUp
                button_type = Quartz.kCGMouseButtonLeft
            elif button == Button.RIGHT:
                up_type = Quartz.kCGEventRightMouseUp
                button_type = Quartz.kCGMouseButtonRight
            elif button == Button.MIDDLE:
                up_type = Quartz.kCGEventOtherMouseUp
                button_type = 2

            event_up = Quartz.CGEventCreateMouseEvent(None, up_type, current_position, button_type)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
        except Exception as e:
            raise RuntimeError(f"Failed to release button at ({current_position[0]}, {current_position[1]}): {e}")

    def drag(self, dx: float | int, dy: float | int, button: Button, steps=20, delay=0.005) -> None:
        """
        Simulate mouse drag relative to current cursor position.

        Parameters
        ----------
        dx : float or int
            The horizontal distance to drag the cursor (positive is right, negative is left).
        dy : float or int
            The vertical distance to drag the cursor (positive is down, negative is up).
        button : Button
            The mouse button to use when dragging. Supported values are:
                - Button.LEFT: Left-click
                - Button.RIGHT: Right-click
                - Button.MIDDLE: Middle-click
        steps : int, optional
            The number of intermediate steps to smooth the movement. Default is 20 (some smoothing).
        delay : float or int, optional
            Delay in seconds between each step. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            raise TypeError("dx and dy must be numeric values")
        self._validate_steps(steps)
        self._validate_delay(delay)
        self._validate_button(button)

        current_position = self.position

        try:
            if button == Button.LEFT:
                self.press(Button.LEFT)
                drag_type = Quartz.kCGEventLeftMouseDragged
                button_type = Quartz.kCGMouseButtonLeft
            elif button == Button.RIGHT:
                self.press(Button.RIGHT)
                drag_type = Quartz.kCGEventRightMouseDragged
                button_type = Quartz.kCGMouseButtonRight
            elif button == Button.MIDDLE:
                self.press(Button.MIDDLE)
                drag_type = Quartz.kCGEventOtherMouseDragged
                button_type = 2

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

            if button == Button.LEFT:
                self.release(Button.LEFT)
            elif button == Button.RIGHT:
                self.release(Button.RIGHT)
            else:
                self.release(Button.MIDDLE)
        except Exception as e:
            raise RuntimeError(f"Failed to drag by {dx} and {dy} with {button.name}: {e}")

    def scroll(self, dx: float | int, dy: float | int, steps=1, delay=0.005) -> None:
        """
        Simulate mouse scroll.

        Parameters
        ----------
        dx : float or int
            The horizontal distance to scroll (positive is left, negative is right).
        dy : float or int
            The vertical distance to scroll (positive is up, negative is down).
        steps : int, optional
            The number of intermediate steps to smooth the scroll. Default is 1 (no smoothing).
        delay : float or int, optional
            Delay in seconds between each step. Default is 0.005 seconds.

        Notes
        -----
        A higher number of steps and a small delay create smoother, more natural movement.
        """
        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            raise TypeError("dx and dy must be numeric values")
        self._validate_steps(steps)
        self._validate_delay(delay)

        intermediate_dx = dx / steps
        intermediate_dy = dy / steps

        try:
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
        except Exception as e:
            raise RuntimeError(f"Failed to scroll by {dx} and {dy}: {e}")
