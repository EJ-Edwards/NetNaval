import os
import threading
import uvicorn
import discord
from discord.ext import commands
from bot import bot  
from fastapi import FastAPI

# ---------------------
# FastAPI setup
# ---------------------
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running!"}

def run_api():
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT env
    uvicorn.run(app, host="0.0.0.0", port=port)

# ---------------------
# Discord bot setup
# ---------------------
intents = discord.Intents.default()
intents.message_content = True  # needed to read messages
intents.members = True  # needed if you access guild members
bot = bot  # use your existing bot object from bot.py
bot.intents = intents

# ---------------------
# Run both API and bot
# ---------------------
if __name__ == "__main__":
    # Start FastAPI in a separate thread
    threading.Thread(target=run_api, daemon=True).start()

    # Run Discord bot
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set!")
    bot.run(token)
