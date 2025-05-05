from enum import Enum

class Key(Enum):
    # Modifier keys
    SHIFT_L = 56
    SHIFT_R = 60
    SHIFT = SHIFT_R
    CAPS_LOCK = 57
    CTRL_L = 59
    CTRL_R = 62
    CTRL = CTRL_R
    OPTION_L = 58
    OPTION_R = 61
    OPTION = OPTION_R
    CMD_L = 55
    CMD_R = 54
    CMD = CMD_R
    FN = 63

    # Control and navigation
    TAB = 48
    ESC = 53
    DELETE = 51
    NUMPAD_DELETE = 117
    RETURN = 36
    ENTER = 76
    SPACE = 49

    LEFT = 123
    RIGHT = 124
    UP = 126
    DOWN = 125
    HOME = 115
    END = 119
    PAGE_UP = 116
    PAGE_DOWN = 121

    # Function keys
    F1 = 122
    F2 = 120
    F3 = 99
    F4 = 118
    F5 = 96
    F6 = 97
    F7 = 98
    F8 = 100
    F9 = 101
    F10 = 109
    F11 = 103
    F12 = 111
