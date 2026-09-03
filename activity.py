import time

import config

channel_active_users: dict[int, dict[int, float]] = {}

typing_users: dict[int, dict[int, float]] = {}


def mark_active(channel_id: int, user_id: int) -> None:
    channel_active_users.setdefault(channel_id, {})[user_id] = time.time()


def mark_typing(channel_id: int, user_id: int) -> None:
    typing_users.setdefault(channel_id, {})[user_id] = time.time()


def count_active_users(channel_id: int) -> int:
    """Users seen in this channel within ACTIVE_WINDOW seconds."""
    now = time.time()
    bucket = channel_active_users.get(channel_id, {})
    return sum(1 for ts in bucket.values() if now - ts < config.ACTIVE_WINDOW)


def is_typing(channel_id: int, user_id: int, within: float = 4.0) -> bool:
    bucket = typing_users.get(channel_id)
    if not bucket or user_id not in bucket:
        return False
    return time.time() - bucket[user_id] < within


def active_typers(channel_id: int, exclude_id: int, within: float = 4.0) -> dict:
    now = time.time()
    bucket = typing_users.get(channel_id, {})
    return {
        uid: ts
        for uid, ts in bucket.items()
        if now - ts < within and uid != exclude_id
    }


def clear_all() -> None:
    channel_active_users.clear()
