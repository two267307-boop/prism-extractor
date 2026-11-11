"""Small optional terminal logo animation."""
import os
import time

a = "\033[38;5;17m"
b = "\033[38;5;25m"
c = "\033[38;5;69m"
d = "\033[38;5;105m"
e = "\033[38;5;141m"

_logos = {
    "frame_1": f"""
        {a}        ██       ██████  ██████  ██  ██████ ███    ███       ██
        {b}         ██      ██   ██ ██   ██ ██ ██      ████  ████      ██
        {c}          ██     ██████  ██████  ██  █████  ██ ████ ██     ██
        {d}         ██      ██      ██   ██ ██      ██ ██  ██  ██      ██
        {e}        ██       ██      ██   ██ ██ ██████  ██      ██       ██""",
    "frame_2": f"""
        {a}          ██     ██████  ██████  ██  ██████ ███    ███     ██
        {b}           ██    ██   ██ ██   ██ ██ ██      ████  ████    ██
        {c}            ██   ██████  ██████  ██  █████  ██ ████ ██   ██
        {d}           ██    ██      ██   ██ ██      ██ ██  ██  ██    ██
        {e}          ██     ██      ██   ██ ██ ██████  ██      ██     ██""",
    "frame_3": f"""
        {a}            ██   ██████  ██████  ██  ██████ ███    ███   ██
        {b}             ██  ██   ██ ██   ██ ██ ██      ████  ████  ██
        {c}              ██ ██████  ██████  ██  █████  ██ ████ ██ ██
        {d}             ██  ██      ██   ██ ██      ██ ██  ██  ██  ██
        {e}            ██   ██      ██   ██ ██ ██████  ██      ██   ██""",
}


def _clear_terminal() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[2J\033[H", end="")


def _play_logo_intro(logos=None, delay: float = 0.15) -> None:
    for frame in (logos or _logos).values():
        print(frame)
        time.sleep(max(0.0, delay))
        _clear_terminal()


if __name__ == "__main__":
    _play_logo_intro()
