import threading
import uvicorn
import os
from bot import bot

def run_api():
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        log_level="info"
    )

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set")

    bot.run(token)
