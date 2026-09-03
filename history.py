from vertexai.generative_models import Content, Part

import config

channel_histories: dict[int, list] = {}


def get_channel_history(channel_id: int) -> list:
    return channel_histories.setdefault(channel_id, [])


def add_to_channel_history(channel_id: int, role: str, text: str) -> None:
    history = get_channel_history(channel_id)
    history.append(Content(role=role, parts=[Part.from_text(text)]))

    if len(history) > config.MAX_HISTORY:
        channel_histories[channel_id] = history[-config.MAX_HISTORY :]


def get_contextual_history(channel_id: int) -> list:
    """Recent slice of history to prime the model with."""
    history = get_channel_history(channel_id)
    if len(history) < 10:
        return list(history)
    return list(history[-max(15, config.MAX_HISTORY // 2) :])


def clear_all() -> None:
    channel_histories.clear()
