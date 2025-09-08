import Quartz
import threading
import traceback
import logging

from keyboard.key import flags_to_key_enum
from keyboard.keymap import get_key_info

logger = logging.getLogger(__name__)


class KeyboardListener:
    """
    Listens for global keyboard events on macOS using Quartz.

    Supports key press, key release, and flag change events. Event handlers
    can be passed in for each type of event. Returning `False` from a handler
    blocks further propagation of the event.

    This class can be used as a context manager (with the `with` statement) or
    managed manually using `start()` and `stop()`.

    Parameters
    ----------
    on_press : Callable[[dict], Optional[bool]], optional
        Function called when a key is pressed. Receives key info dict with 'key_enum', 'name', 'keycode'.
        Return False to block the event, True or None to allow it.
    on_release : Callable[[dict], Optional[bool]], optional
        Function called when a key is released. Receives key info dict with 'key_enum', 'name', 'keycode'.
        Return False to block the event, True or None to allow it.
    on_flags_changed : Callable[[dict], Optional[bool]], optional
        Function called when modifier flags change. Receives modifier flags as Key.
        Return False to block the event, True or None to allow it.
    on_error : Callable[[dict], None], optional
        Function called when an exception occurs inside a handler. Receives a dictionary
        containing error context including 'handler', 'args', 'exception', and 'traceback'.
    """

    def __init__(self, on_press=None, on_release=None, on_flags_changed=None, on_error=None):
        self.on_press = on_press
        self.on_release = on_release
        self.on_flags_changed = on_flags_changed
        self.on_error = on_error
        self.tap = None
        self.source = None
        self._thread = None
        self._running = False

    def _setup(self) -> None:
        """
        Sets up the Quartz event tap and registers it with the run loop.
        """
        event_mask = (
                Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
                Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
                Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged)
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

    def _safe_call(self, func, *args) -> bool:
        """
        Invokes a handler safely, catching and reporting any exceptions.

        If `on_error` is defined, the exception is passed to it as a structured dict.
        Otherwise, the error is logged.

        Returns
        -------
        bool
            True to continue event propagation, or the handler's actual return value.
            If an exception occurs, defaults to True (do not block the event).
        """
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
        Internal callback invoked for each intercepted keyboard event.
        Dispatches to the appropriate handler (press, release, flags_changed).
        """
        # Key down event
        if event_type == Quartz.kCGEventKeyDown and self.on_press:
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            key_info = get_key_info(keycode)
            should_propagate = self._safe_call(self.on_press, key_info)
            if should_propagate is False:
                return None  # Block the event
        # Key up event
        elif event_type == Quartz.kCGEventKeyUp and self.on_release:
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            key_info = get_key_info(keycode)
            should_propagate = self._safe_call(self.on_release, key_info)
            if should_propagate is False:
                return None  # Block the event
        # Modifier key event change
        elif event_type == Quartz.kCGEventFlagsChanged and self.on_flags_changed:
            flags = Quartz.CGEventGetFlags(event)
            active_modifiers = flags_to_key_enum(flags)
            should_propagate = self._safe_call(self.on_flags_changed, active_modifiers)
            if should_propagate is False:
                return None  # Block the event

        return event  # Allow the event through

    def __enter__(self):
        """
        Initializes the event tap and starts listening.
        Used when entering a context block.
        """
        try:
            self._setup()
        except Exception as e:
            logging.exception("Failed to initialize KeyboardListener: %s", e)
            raise

        return self

    def __exit__(self, *args):
        """
        Stops the event tap when exiting a context block.
        """
        self.stop()

    def start(self):
        """
        Starts the keyboard listener in a background thread.
        """
        if self._running:
            logger.warning("KeyboardListener is already running.")
            return

        self._running = True

        def run():
            try:
                self.__enter__()
                Quartz.CFRunLoopRun()
            except Exception as e:
                logger.exception("Error in KeyboardListener run loop: %s", e)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stops the run loop and disables the event tap.
        """
        if not self._running:
            logger.warning("KeyboardListener is not running.")
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