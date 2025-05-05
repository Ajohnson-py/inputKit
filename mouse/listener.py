import traceback

import Quartz
import threading
import logging

logger = logging.getLogger(__name__)


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
    on_error : Callable[[dict], None], optional
        Function called when an exception occurs inside a handler. Receives a dictionary
        containing error context including 'handler', 'args', 'exception', and 'traceback'.
    """

    def __init__(self, on_move=None, on_click=None, on_scroll=None, on_error=None):
        self.on_move = on_move
        self.on_click = on_click
        self.on_scroll = on_scroll
        self.on_error = on_error
        self.tap = None
        self.source = None
        self._thread = None
        self._running = False

    def _safe_call(self, func, *args) -> bool:
        try:
            return func(*args)
        except Exception as e:
            context_info = {
                "handler": func.__name__,
                "args": args,
                "exception": repr(e),
                "traceback": traceback.format_exc()
            }

            if self.on_error:
                self.on_error(context_info)
            else:
                logger.error(f"Error in handler {func.__name__} with args {args}:\n{context_info['traceback']}")

            return True  # Continue event propagation

    def _callback(self, proxy, event_type, event, refcon):
        """
        Internal callback invoked for each intercepted mouse event.
        Dispatches to the appropriate handler (move, click, scroll).
        """
        loc = Quartz.CGEventGetLocation(event)

        if event_type == Quartz.kCGEventMouseMoved and self.on_move:
            should_propagate = self._safe_call(self.on_move, (loc.x, loc.y))
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
                should_propagate = self._safe_call(self.on_click, (loc.x, loc.y), button, pressed)
                if should_propagate is False:
                    return None  # Block the event

        elif event_type == Quartz.kCGEventScrollWheel and self.on_scroll:
            dy = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis1)
            dx = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis2)
            should_propagate = self._safe_call(self.on_scroll, (loc.x, loc.y), dx, dy)
            if should_propagate is False:
                return None  # Block the event

        return event  # Allow the event through

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
            logger.critical("Failed to create event tap.")
            raise RuntimeError("Failed to create event tap.")
        self.source = Quartz.CFMachPortCreateRunLoopSource(None, self.tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), self.source, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(self.tap, True)

    def __enter__(self):
        """
        Initializes the event tap and starts listening.
        Used when entering a context block.
        """
        try:
            self._setup()
        except Exception as e:
            logging.exception("Failed to initialize MouseListener: %s", e)
            raise

        return self

    def __exit__(self, *args):
        """
        Initializes the event tap and starts listening.
        Used when entering a context block.
        """
        self.stop()

    def start(self):
        """
        Starts the mouse listener in a background thread.
        """
        if self._running:
            logger.warning("MouseListener is already running.")
            return

        self._running = True

        def run():
            try:
                self.__enter__()
                Quartz.CFRunLoopRun()
            except Exception as e:
                logger.exception("Error in MouseListener run loop: %s", e)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stops the run loop and disables the event tap.
        """
        if not self._running:
            logger.warning("MouseListener is not running.")
            return
        elif self._running:
            Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())
            self._running = False
            self._thread.join()
            self._thread = None

    def join(self):
        """
        Blocks the current thread until the run loop is stopped.
        """
        Quartz.CFRunLoopRun()
