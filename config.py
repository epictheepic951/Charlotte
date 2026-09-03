import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"See .env.example for the full list."
        )
    return value


DISCORD_TOKEN = _require("DISCORD_TOKEN")
GROQ_API_KEY = _require("GROQ_API_KEY")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _require("GOOGLE_APPLICATION_CREDENTIALS")


PROJECT_ID = _require("GCP_PROJECT_ID")
LOCATION = _require("GCP_LOCATION")
TUNED_MODEL_ENDPOINT = _require("TUNED_MODEL_ENDPOINT")


GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_LTM_MODEL = os.getenv("GROQ_LTM_MODEL", "llama-3.1-8b-instant")


MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))

AWAKE_DURATION = int(os.getenv("AWAKE_DURATION", "300"))

ACTIVE_WINDOW = int(os.getenv("ACTIVE_WINDOW", "300"))

MAX_CHARS = int(os.getenv("MAX_CHARS", "2000"))

GIF_COOLDOWN = int(os.getenv("GIF_COOLDOWN", "7"))

RESET_COMMAND = os.getenv("RESET_COMMAND", "!reset")


LTM_FILE = os.getenv("LTM_FILE", "ltm.json")
LTM_MAX_USER = int(os.getenv("LTM_MAX_USER", "50"))
LTM_MAX_CHANNEL = int(os.getenv("LTM_MAX_CHANNEL", "100"))
LTM_WRITE_EVERY = int(os.getenv("LTM_WRITE_EVERY", "5"))


TOKEN_LOG_FILE = os.getenv("TOKEN_LOG_FILE", "token_log.json")

IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
