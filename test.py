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


# Using as context manager
with KeyboardListener(on_press=on_key_press, on_release=on_key_release, on_flags_changed=on_flags_changed) as listener:
    listener.join()
