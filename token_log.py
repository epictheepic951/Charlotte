import json
import os

import config


def load_token_log() -> dict:
    if os.path.exists(config.TOKEN_LOG_FILE):
        with open(config.TOKEN_LOG_FILE, "r") as f:
            return json.load(f)
    return {"ltm_write": 0, "gif_decision": 0, "response": 0, "total": 0}


def log_tokens(category: str, count: int) -> None:
    log = load_token_log()
    log[category] = log.get(category, 0) + count
    log["total"] = log.get("total", 0) + count

    with open(config.TOKEN_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

    print(f"Tokens [{category}]: +{count} | Total: {log['total']}")
