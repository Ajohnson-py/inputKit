import sys

if sys.platform != "darwin":
    raise OSError("inputKit only supports macOS.")

__version__ = "1.0.0"

from mouse.button import Button
from mouse.controller import MouseController
from mouse.listener import MouseListener

__all__ = ["Button", "MouseController", "MouseListener"]
