# Charlotte

A Discord bot powered by a fine-tuned LLM trained on my own chat history! This is the controller I used in group chats to make it type the way I actually do, rather than sounding like a generic assistant.


## What happens to a message

```
message
   ↓
gate           allowed channel? is the bot awake, or was it addressed?
   ↓
vision         image attached? caption it and stick the caption in the text
   ↓
buffer         wait for the user to stop typing, then merge what they sent
   ↓
gif            ask the model if a reaction gif fits, send it first if so
   ↓
memory         pull up any stored facts relevant to this message
   ↓
generate       tuned model + channel history + memories → reply
   ↓
pace           split into bursts, wait for a lull, send with delays
   ↓
memory write   every N responses, ask the model what to remember
```

## Some choices I made

**History is per channel** It's a group chat, so the bot needs to see everything, not just messages aimed at it. Each turn gets prefixed with the speaker's name so the model knows who said what.

**Replies wait on the typing indicator** People send one thought as three messages. With a fixed delay you either cut them off or feel slow. Watching for the typing indicator to stop means the bot waits however long the person actually takes. Every new message from that user restarts the wait.

**A cheap model handles memory lookup.** Stuffing every saved fact into the prompt gets expensive and buries the actual conversation, so a small fast model reads the incoming message and returns just the IDs of facts that matter. Writing works the other way around: the tuned model decides what from the last few exchanges is worth saving, since it's the one that knows what the persona would care about.

**Memory has a ceiling.** Per-user and per-channel facts are capped separately and old ones get dropped. Otherwise it grows into the context limit and fills up with stale junk.

**Replies come out in bursts.** The model hands back one block of text. People don't type like that. So it gets split on sentence boundaries into random-sized groups, with the delay between them scaled to how long the message is.

**Inline replies only when the channel is busy.** If two or more people have said something recently the bot uses Discord's reply feature so it's clear who it's talking to. In a quiet channel that looks weird, so it just sends normally.

**It won't talk over you.** If someone starts typing while the model is still generating, the bot holds off for a second.

**Images get captioned before the model sees them.** The tuned model is text-only, so attachments get pulled from Discord's CDN, described by a vision model, and dropped into the prompt in brackets. The persona reacts to images it can't actually see.

**Gifs are the model's call.** No keyword matching. It gets asked whether a gif fits and which mood, then a URL gets picked at random from that mood's list. The cooldown counts responses rather than seconds so it can't spam gifs when the chat is moving fast.

## Files

```
charlotte/
├── bot.py                Discord events, buffering, the main pipeline
├── config.py             settings from .env, errors out if any are missing
├── persona.py            system prompt, gif library, username map  (gitignored)
├── persona.example.py    template for the above
├── model.py              Vertex AI and Groq client setup
├── memory.py             long-term memory: lookup, writing, pruning
├── history.py            per-channel conversation history
├── activity.py           who's around and who's typing
├── gifs.py               mood picking and cooldown
├── vision.py             image captioning
├── messaging.py          burst splitting, pacing, debug logs
└── token_log.py          token counter, broken down by call type
```

Config is split in two. `config.py` pulls secrets and tunables out of `.env`. Anything personal (system prompt, which Discord handles map to which names, my gif library) lives in `persona.py`, which is gitignored. Means I can push this without stripping stuff out by hand every time.

## Running it

```bash
git clone <repo-url>
cd charlotte
pip install -r requirements.txt

cp .env.example .env
cp persona.example.py persona.py
```

Fill in `.env` with your Discord token, GCP credentials, model endpoint and Groq key. Then edit `persona.py`: system prompt, the channel IDs it's allowed to post in, and optionally a gif library and username map.

```bash
python bot.py
```

You'll need your own fine-tuned model for this to do anything interesting. See below.

## Config reference

| Setting | Where | What it does |
|---|---|---|
| `DISCORD_TOKEN`, `GROQ_API_KEY`, GCP vars | `.env` | credentials |
| `GROQ_MODEL`, `GROQ_LTM_MODEL` | `.env` | vision model and memory-filter model |
| `MAX_HISTORY` | `.env` | how many turns of history to keep |
| `AWAKE_DURATION` | `.env` | how long it keeps replying without being addressed |
| `ACTIVE_WINDOW` | `.env` | how long someone counts as "in the channel" |
| `GIF_COOLDOWN` | `.env` | minimum responses between gifs |
| `LTM_*` | `.env` | memory file, caps, write frequency |
| `SYSTEM_INSTRUCTION` | `persona.py` | who the persona is, how it talks |
| `ALLOWED_CHANNEL_IDS` | `persona.py` | where it's allowed to post |
| `TRIGGER_WORD` | `persona.py` | prefix that wakes it up when idle |
| `LTM_MODE` | `persona.py` | turn long-term memory on |
| `USER_LIST` | `persona.py` | Discord handle → trained name |
| `GIF_LIBRARY` | `persona.py` | mood → gif URLs |

## Stack

Python, discord.py, Vertex AI (fine-tuned Gemini), Groq (Llama), asyncio, httpx

## Caveats

**Groq models will deprecate** The ones in `.env.example` may be dead or renamed by now, check [Groq's model list](https://console.groq.com/docs/models).
