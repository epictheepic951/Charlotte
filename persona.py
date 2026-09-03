"""
Persona configuration — LOCAL ONLY. This file is gitignored.

Carried over from the original single-file version. Two bugs fixed while
porting: a missing comma in the "disagree" list that silently concatenated
two URLs into one broken string, and a duplicate "confused" key that
shadowed the first definition.
"""


SYSTEM_INSTRUCTION = """
"""


ALLOWED_CHANNEL_IDS: list[int] = []

LOG_CHANNEL_ID = 0

TRIGGER_WORD = ""


LTM_MODE = False


USER_LIST: dict[str, str] = {}

#add more!
GIF_LIBRARY: dict[str, list[str]] = {
    "disagree": [
        "https://tenor.com/view/an-iq-too-high-raven-crow-tiktok-gif-3869671553367641450",
    ],
    "cringe": [
        "https://tenor.com/view/son-im-crine-son-im-crine-gif-5176045023480767429",
    ],
    "confused": [
        "https://tenor.com/view/who-is-he-who-is-this-who-is-that-who-is-this-guy-who-is-he-peppa-pig-gif-11375013126139160285",
    ],
    "shock": [
        "https://tenor.com/view/nahdog-gif-17900380376959797190",
    ],
    "agree": [
        "https://klipy.com/gifs/he-made-a-statement-so-good",
    ],
    "angry": [
        "https://tenor.com/view/bait-bait-or-low-iq-bait-or-low-iq-call-it-call-it-bait-or-gif-11665902714889208022",
    ],
}
