import asyncio
import random
import re
import time

import activity
import config
import persona

_client = None


def set_client(client) -> None:
    global _client
    _client = client


async def log(msg: str, where: str) -> None:
    """Post a debug line to the log channel, if one is configured."""
    if not persona.LOG_CHANNEL_ID or _client is None:
        return
    try:
        channel = _client.get_channel(persona.LOG_CHANNEL_ID)
        if channel:
            await channel.send(f"{where} {msg}")
    except Exception as e:
        print(f"log send failed: {e}")


async def wait_for_quiet(channel_id: int, timeout: float = 2.0) -> None:
    """Hold until nobody else is typing, or until timeout."""
    start = time.time()
    bot_id = _client.user.id if _client else -1

    while time.time() - start < timeout:
        if not activity.active_typers(channel_id, exclude_id=bot_id):
            return
        await asyncio.sleep(0.5)


def split_at_sentences(text: str, limit: int = None) -> list[str]:
    """Break text into chunks under Discord's character limit, on sentence ends."""
    limit = limit or config.MAX_CHARS

    if len(text) <= limit:
        return [text]

    chunks = []
    while len(text) > limit:
        boundary = max(
            text.rfind(". ", 0, limit),
            text.rfind("! ", 0, limit),
            text.rfind("? ", 0, limit),
        )
        boundary = limit if boundary == -1 else boundary + 1

        chunks.append(text[:boundary].strip())
        text = text[boundary:].strip()

    if text:
        chunks.append(text)

    return chunks


async def send_human_like(message, full_text: str) -> None:
    """Send a reply as a series of paced bursts rather than one wall of text."""
    if not full_text:
        return

    use_reply = activity.count_active_users(message.channel.id) >= 2

    first_message = True
    for chunk in split_at_sentences(full_text, config.MAX_CHARS):
        sentences = re.split(r"(?<=[.!?])\s+|(?<=\s)(?=[A-Z][a-z]{2,})", chunk)

        bursts = []
        i = 0
        while i < len(sentences):
            group_size = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
            bursts.append(" ".join(sentences[i : i + group_size]))
            i += group_size

        async with message.channel.typing():
            for i, burst in enumerate(bursts):
                if first_message and use_reply:
                    await message.reply(burst)
                else:
                    await message.channel.send(burst)
                first_message = False

                if i < len(bursts) - 1:
                    await asyncio.sleep(random.uniform(0.5, 1.0) + len(burst) / 150)
