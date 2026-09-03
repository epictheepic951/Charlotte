import asyncio
import datetime
import os
import time

import discord

import activity
import config
import gifs
import history
import memory
import messaging
import persona
from model import model
from token_log import log_tokens
from vision import describe_image

client = discord.Client()
messaging.set_client(client)


last_interaction: dict[int, datetime.datetime] = {}
message_buffers: dict[tuple, list] = {}
pending_tasks: dict[tuple, asyncio.Task] = {}
response_counters: dict[int, int] = {}


def username_map(author_name: str) -> str:
    """Translate a Discord handle to the name the model was trained on."""
    return persona.USER_LIST.get(author_name, author_name)


def reset_state() -> None:
    history.clear_all()
    activity.clear_all()
    gifs.clear_all()
    response_counters.clear()
    message_buffers.clear()
    last_interaction.clear()

    for task in pending_tasks.values():
        task.cancel()
    pending_tasks.clear()

    print("System reset")


async def process_and_reply(message, combined_text: str, author_name: str) -> None:
    channel_id = message.channel.id
    channel_name = getattr(message.channel, "name", str(channel_id))
    author_name = username_map(author_name)

    try:
        gif_url = await gifs.maybe_get_gif(
            channel_name, channel_id, combined_text, author_name
        )
        if gif_url:
            await message.channel.send(gif_url)
        gifs.bump_cooldown(channel_id)

        ltm_context = ""
        if persona.LTM_MODE:
            ltm_context = await memory.retrieve_relevant_ltm(
                channel_id, combined_text, author_name
            )

        formatted_input = f"[Channel: #{channel_name}]\n"
        if ltm_context:
            formatted_input += f"{ltm_context}\n\n"
        formatted_input += f"{author_name}: {combined_text}"

        history.add_to_channel_history(channel_id, "user", formatted_input)
        contextual_history = history.get_contextual_history(channel_id)

        print(f"Generating response for {author_name} in #{channel_name}...")

        chat = model.start_chat(history=contextual_history)
        async with message.channel.typing():
            response = await asyncio.to_thread(
                lambda: chat.send_message(formatted_input)
            )
            parts = response.candidates[0].content.parts
            reply = parts[-1].text if len(parts) > 1 else parts[0].text

        if response.usage_metadata:
            total = response.usage_metadata.total_token_count
            log_tokens("response", total)
            if total > 2000:
                await messaging.log(str(total), "[TOKEN ALERT]")

        if reply.upper().endswith("END") or reply.upper().endswith("END."):
            reply = reply[:-3].strip().rstrip(".! ")

        history.add_to_channel_history(channel_id, "model", reply)

        if persona.LTM_MODE:
            response_counters[channel_id] = response_counters.get(channel_id, 0) + 1
            if response_counters[channel_id] >= config.LTM_WRITE_EVERY:
                response_counters[channel_id] = 0
                recent = history.get_contextual_history(channel_id)
                member_names = list(
                    {
                        m.parts[0].text.split(":")[0]
                        for m in recent
                        if m.role == "user" and ":" in m.parts[0].text
                    }
                )
                asyncio.create_task(
                    memory.maybe_write_ltm(
                        channel_id, channel_name, recent, member_names
                    )
                )

        await messaging.wait_for_quiet(channel_id)
        await messaging.send_human_like(message, reply)

    except Exception as e:
        print(f"Bot error: {e}")


async def buffer_waiter(user_id: int, channel_id: int, message_obj) -> None:
    """
    Wait for the user to stop typing, then handle everything they sent as one
    message. Stops the bot from replying three times to one thought.
    """
    key = (user_id, channel_id)

    while activity.is_typing(channel_id, user_id):
        await asyncio.sleep(2)

    if key in message_buffers and message_buffers[key]:
        buffered = message_buffers[key]
        print(f"Processing buffer for {user_id}: {len(buffered)} messages")

        combined_text = " ".join(item["text"] for item in buffered)
        author_name = buffered[-1]["author_name"]
        message_buffers[key] = []

        await process_and_reply(message_obj, combined_text, author_name)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_typing(channel, user, when):
    if user.id == client.user.id:
        return
    activity.mark_typing(channel.id, user.id)


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    if message.channel.id not in persona.ALLOWED_CHANNEL_IDS:
        return
    if message.content.startswith("/"):
        return

    channel_id = message.channel.id
    content = message.content.strip()
    user_id = message.author.id
    author_name = message.author.name

    if content == config.RESET_COMMAND:
        reset_state()
        await message.channel.send("ok")
        return

    activity.mark_active(channel_id, user_id)

    has_trigger = bool(persona.TRIGGER_WORD) and content.lower().startswith(
        persona.TRIGGER_WORD.lower()
    )

    now = datetime.datetime.now()
    is_awake = False
    if channel_id in last_interaction:
        is_awake = (
            now - last_interaction[channel_id]
        ).total_seconds() < config.AWAKE_DURATION

    if not (has_trigger or is_awake or not persona.TRIGGER_WORD):
        return

    image_prefix = ""
    for attachment in message.attachments:
        ext = os.path.splitext(attachment.filename.lower())[1]
        if ext in config.IMAGE_TYPES:
            description = await describe_image(attachment.url)
            if description:
                image_prefix = f"[Image shared by {author_name}: {description}] "
            break

    text = content[len(persona.TRIGGER_WORD) :].strip() if has_trigger else content

    if not text and image_prefix:
        text, image_prefix = image_prefix.strip(), ""
    elif not text:
        return

    combined = f"{image_prefix}{text}" if image_prefix else text

    last_interaction[channel_id] = now

    key = (user_id, channel_id)
    message_buffers.setdefault(key, []).append(
        {"text": combined, "author_name": author_name}
    )

    if key in pending_tasks:
        pending_tasks[key].cancel()

    pending_tasks[key] = asyncio.create_task(
        buffer_waiter(user_id, channel_id, message)
    )


if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
