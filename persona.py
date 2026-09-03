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


GIF_LIBRARY: dict[str, list[str]] = {
    "disagree": [
        "https://tenor.com/view/son-im-crine-son-im-crine-gif-5176045023480767429",
        "https://tenor.com/view/brain-empty-brain-out-brain-meme-brain-no-brain-meme-gif-1120718379326435330",
        "https://klipy.com/gifs/corny-9",
        "https://klipy.com/gifs/ahem-shit-1--k01KR8DCAWXSE5HEQMN4426XB35",
        "https://klipy.com/gifs/he-made-a-statement-so-trash",
        "https://tenor.com/view/tesla-and-einstein-luma-ai-gif-14475294631445060178",
        "https://tenor.com/view/an-iq-too-high-raven-crow-tiktok-gif-3869671553367641450",
        "https://tenor.com/view/bait-bait-or-low-iq-bait-or-low-iq-call-it-call-it-bait-or-gif-11665902714889208022",
    ],
    "cringe": [
        "https://tenor.com/view/son-im-crine-son-im-crine-gif-5176045023480767429",
        "https://klipy.com/gifs/sukun-smile-jujutsu-kaisen",
        "https://tenor.com/view/an-iq-too-high-raven-crow-tiktok-gif-3869671553367641450",
    ],
    "confused": [
        "https://tenor.com/view/son-im-crine-son-im-crine-gif-5176045023480767429",
        "https://tenor.com/view/who-is-he-who-is-this-who-is-that-who-is-this-guy-who-is-he-peppa-pig-gif-11375013126139160285",
        "https://tenor.com/view/brain-empty-brain-out-brain-meme-brain-no-brain-meme-gif-1120718379326435330",
        "https://tenor.com/view/who-is-this-gif-4011795153273257473",
        "https://tenor.com/view/tesla-and-einstein-luma-ai-gif-14475294631445060178",
        "https://tenor.com/view/caldruki-einstein-nikola-tesla-gif-14422382707037544026",
        "https://tenor.com/view/an-iq-too-high-raven-crow-tiktok-gif-3869671553367641450",
    ],
    "shock": [
        "https://tenor.com/view/ishowspeed-degloving-colored-ishowspeed-hiding-speed-gif-1002767818191722465",
        "https://tenor.com/view/nahdog-gif-17900380376959797190",
        "https://tenor.com/view/ts-is-peak-man-im-crying-black-man-seeing-a-page-gif-15026551147765847806",
    ],
    "agree": [
        "https://tenor.com/view/homelander-glow-glowing-angel-hallucinating-gif-489344050525737667",
        "https://tenor.com/view/ts-is-peak-man-im-crying-black-man-seeing-a-page-gif-15026551147765847806",
        "https://klipy.com/gifs/he-made-a-statement-so-good",
    ],
    "angry": [
        "https://tenor.com/view/bait-bait-or-low-iq-bait-or-low-iq-call-it-call-it-bait-or-gif-11665902714889208022",
        "https://klipy.com/gifs/corny-9",
    ],
}
