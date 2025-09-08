# inputKit


> A library that handles mouse and keyboard macOS inputs. 

---

### Table of Contents

- [Description](#description)
- [Improvements to Come](#improvements-to-come)
- [Installation and Running](#installation-and-running)
- [How To Use inputKit](#how-to-use-inputKit)
- [License](#license)
- [Author Info](#author-info)

---

## Description

For programmers on macOS, receiving and handling global device inputs can be a challenging task, particularly when you need to create input hooks. That is why I created **inputKit**. This library utilizes **PyObjC** to call native macOS functions that handle device inputs, thereby abstracting this process.

#### Technologies

- Python
- PyObjC
- Quartz

---

## Improvements to Come

Currently, inputKit has **limited error handling** and is not installable with ```pip```. As such, this functionality will be added in the near future. I also plan to create extensive documentation.

---

## Installation and Running

### Coming soon!

---

## How To Use inputKit

With inputKit, the usage is extremely simple. First, you import the functionality you desire, and then you create an object that performs the actions.

See the code below:

```python
from keyboard.listener import KeyboardListener


def on_key_press(key_info):
    print(
        f"Key pressed: {key_info['name']} (code: {key_info['keycode']})\n"
    )

    key_name = key_info['name']

    # Example: Block the 'a' key
    if key_name == 'a':
        print("Blocking 'a' key!")
        return False


def on_key_release(key_info):
    print(f"Key released: {key_info['name']} (code: {key_info['keycode']})\n")


def on_flags_changed(flags):
    print(f"Modifier flags changed: {flags}\n")


with KeyboardListener(on_press=on_key_press, on_release=on_key_release, on_flags_changed=on_flags_changed) as listener:
    listener.join()
```

This code listens for key presses and blocks the 'a' key from being read by macOS. It also prints important info for the keys that are press, like the name and keycode associated with it, as well as if it's pressed or released.

---

## License

MIT License

Copyright (c) 2025 August Johnson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Author Info

- LinkedIn - [August Johnson](https://www.linkedin.com/in/aug-johnson)


[Back To The Top](#inputkit)