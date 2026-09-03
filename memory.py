import asyncio
import datetime
import json
import os
import re

import config
from model import groq_client, model
from token_log import log_tokens


def load_ltm() -> dict:
    if os.path.exists(config.LTM_FILE):
        with open(config.LTM_FILE, "r") as f:
            return json.load(f)
    return {"per_user": {}, "per_channel": {}}


def save_ltm(ltm: dict) -> None:
    with open(config.LTM_FILE, "w") as f:
        json.dump(ltm, f, indent=2)


def _trim_ltm(entries: list, cap: int) -> list:
    """Drop oldest entries when over cap."""
    return entries[-cap:] if len(entries) > cap else entries


def add_ltm_entry(ltm: dict, scope: str, key: str, content: str, cap: int) -> None:
    bucket = ltm.setdefault(scope, {}).setdefault(key, [])
    bucket.append(
        {
            "content": content,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )
    ltm[scope][key] = _trim_ltm(bucket, cap)


def get_ltm_entries(ltm: dict, scope: str, key: str) -> list:
    return ltm.get(scope, {}).get(str(key), [])


async def retrieve_relevant_ltm(
    channel_id: int, current_message: str, author_name: str
) -> str:
    """Return a formatted block of memories relevant to this message, or ''."""
    ltm = load_ltm()
    user_mems = get_ltm_entries(ltm, "per_user", author_name)
    chan_mems = get_ltm_entries(ltm, "per_channel", str(channel_id))

    if not user_mems and not chan_mems:
        return ""

    all_mems = [
        f"[U{i}] (about {author_name}) {m['content']}" for i, m in enumerate(user_mems)
    ] + [f"[C{i}] (channel fact) {m['content']}" for i, m in enumerate(chan_mems)]

    filter_prompt = (
        "You are a memory filter. Given a list of stored facts and a new message, "
        "return only the IDs of facts relevant to the message.\n\n"
        f"Facts:\n" + "\n".join(all_mems) + "\n\n"
        f"Message from {author_name}: {current_message}\n\n"
        "Reply ONLY with the relevant IDs (e.g. 'U0, C2'). "
        "If none are relevant, reply with 'NONE'. No explanation."
    )

    try:
        response = await asyncio.to_thread(
            lambda: groq_client.chat.completions.create(
                model=config.GROQ_LTM_MODEL,
                messages=[{"role": "user", "content": filter_prompt}],
                max_tokens=100,
            )
        )
        raw = response.choices[0].message.content.strip()

        if not raw or raw.upper() == "NONE":
            return ""

        selected = []
        for token in re.findall(r"[UC]\d+", raw):
            kind, idx = token[0], int(token[1:])
            if kind == "U" and idx < len(user_mems):
                selected.append(f"(about {author_name}) {user_mems[idx]['content']}")
            elif kind == "C" and idx < len(chan_mems):
                selected.append(f"(channel) {chan_mems[idx]['content']}")

        if not selected:
            return ""

        return "[Relevant memories]\n" + "\n".join(f"- {s}" for s in selected)

    except Exception as e:
        print(f"LTM retrieval error: {e}")
        return ""


async def maybe_write_ltm(
    channel_id: int, channel_name: str, recent_history: list, member_names: list
) -> None:
    """Ask the persona what's worth remembering from the recent conversation."""
    if not recent_history:
        return

    history_text = "\n".join(f"{c.role}: {c.parts[0].text}" for c in recent_history)
    members_str = ", ".join(member_names) if member_names else "unknown"

    write_prompt = (
        f"You just had the following conversation in #{channel_name} "
        f"with: {members_str}.\n\n{history_text}\n\n"
        "Decide what, if anything, is worth storing in long-term memory.\n"
        "Reply ONLY in this JSON format (no markdown, no extra text):\n"
        '{"per_user": {"name": ["fact1", "fact2"]}, "per_channel": ["fact1", "fact2"]}\n'
        "Use empty lists/dicts if nothing is worth remembering."
    )

    try:
        response = await asyncio.to_thread(lambda: model.generate_content(write_prompt))
        raw = response.candidates[0].content.parts[-1].text.strip()

        if response.usage_metadata:
            log_tokens("ltm_write", response.usage_metadata.total_token_count)

        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)

        ltm = load_ltm()

        for username, facts in data.get("per_user", {}).items():
            for fact in facts:
                if fact:
                    add_ltm_entry(ltm, "per_user", username, fact, config.LTM_MAX_USER)

        for fact in data.get("per_channel", []):
            if fact:
                add_ltm_entry(
                    ltm, "per_channel", str(channel_id), fact, config.LTM_MAX_CHANNEL
                )

        save_ltm(ltm)
        print(f"LTM updated for #{channel_name}: {data}")

    except Exception as e:
        print(f"LTM write error: {e}")
