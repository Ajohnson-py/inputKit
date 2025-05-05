KEYCODE_CHAR_MAP = {
    0: 'a',
    1: 's',
    2: 'd',
    3: 'f',
    4: 'h',
    5: 'g',
    6: 'z',
    7: 'x',
    8: 'c',
    9: 'v',
    11: 'b',
    12: 'q',
    13: 'w',
    14: 'e',
    15: 'r',
    16: 'y',
    17: 't',
    18: '1',
    19: '2',
    20: '3',
    21: '4',
    22: '6',
    23: '5',
    24: '=',
    25: '9',
    26: '7',
    27: '-',
    28: '8',
    29: '0',
    30: ']',
    31: 'o',
    32: 'u',
    33: '[',
    34: 'i',
    35: 'p',
    37: 'l',
    38: 'j',
    39: '\'',
    40: 'k',
    41: ';',
    42: '\\',
    43: ',',
    44: '/',
    45: 'n',
    46: 'm',
    47: '.',
    49: ' ',
    50: '`',
    82: '0',
    83: '1',
    84: '2',
    85: '3',
    86: '4',
    87: '5',
    88: '6',
    89: '7',
    91: '8',
    92: '9',
}

# Characters that can only be accessed with shift
SHIFTED_CHAR_MAP = {
    '~': '`',
    '!': '1',
    '@': '2',
    '#': '3',
    '$': '4',
    '%': '5',
    '^': '6',
    '&': '7',
    '*': '8',
    '(': '9',
    ')': '0',
    '_': '-',
    '+': '=',
    '{': '[',
    '}': ']',
    '|': '\\',
    ':': ';',
    '"': '\'',
    '<': ',',
    '>': '.',
    '?': '/'
}


def char_to_keycode(char: str) -> tuple[int, bool] | None:
    if char in SHIFTED_CHAR_MAP.keys():
        base_char = SHIFTED_CHAR_MAP[char]
        result = char_to_keycode(base_char)
        if result:
            return result[0], True

    if char.isalpha() and char.isupper():
        result = char_to_keycode(char.lower())
        if result:
            return result[0], True

    for key, value in KEYCODE_CHAR_MAP.items():
        if value == char:
            return key, False

    return None
