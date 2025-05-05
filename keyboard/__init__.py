import sys

if sys.platform != "darwin":
    raise OSError("inputKit only supports macOS.")
