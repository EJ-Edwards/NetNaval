import threading
import uvicorn
from bot import bot
import os

def run_api():
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    bot.run(os.environ["DISCORD_TOKEN"])
