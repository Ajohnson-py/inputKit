import sys

if sys.platform != "darwin":
    raise OSError("inputKit only supports macOS.")

__version__ = "1.0.0"

from keyboard.key import Key
from keyboard.controller import KeyboardController
from keyboard.listener import KeyboardListener

__all__ = ["Key", "KeyboardController", "KeyboardListener"]
