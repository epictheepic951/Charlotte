import asyncio
import random

import config
import persona
from model import GIF_GEN_CONFIG, model
from token_log import log_tokens

GIF_MOODS = list(persona.GIF_LIBRARY.keys())

gif_cooldown_counters: dict[int, int] = {}


def bump_cooldown(channel_id: int) -> None:
    gif_cooldown_counters[channel_id] = (
        gif_cooldown_counters.get(channel_id, config.GIF_COOLDOWN) + 1
    )


def clear_all() -> None:
    gif_cooldown_counters.clear()


async def maybe_get_gif(channel_name: str, channel_id: int, user_message: str,
                        author_name: str) -> str | None:
    """Return a gif URL if one fits and the cooldown has elapsed, else None."""
    if not GIF_MOODS:
        return None

    since_last = gif_cooldown_counters.get(channel_id, config.GIF_COOLDOWN)
    if since_last < config.GIF_COOLDOWN:
        return None

    prompt = (
        f"You are in #{channel_name}. "
        f'{author_name} just said: "{user_message}"\n'
        f"Should you react with a gif? If yes, reply with one of: "
        f"{', '.join(GIF_MOODS)}. If no, reply with NONE."
    )

    try:
        response = await asyncio.to_thread(
            lambda: model.generate_content(prompt, generation_config=GIF_GEN_CONFIG)
        )

        if response.usage_metadata:
            log_tokens("gif_decision", response.usage_metadata.total_token_count)

        mood = response.candidates[0].content.parts[-1].text.strip().lower()

        if mood == "none" or mood not in GIF_MOODS:
            return None

        options = [url for url in persona.GIF_LIBRARY.get(mood, []) if url]
        if not options:
            return None

        gif_cooldown_counters[channel_id] = 0
        return random.choice(options)

    except Exception as e:
        print(f"GIF decision error: {e}")
        return None
