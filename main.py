import os
import threading
import discord
from discord.ext import commands
import uvicorn

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True  # Needed to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Example bot event (you can remove if you already have handlers in bot.py)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# --- FastAPI Setup ---
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

def run_api():
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# --- Run both Discord bot and FastAPI ---
if __name__ == "__main__":
    # Start FastAPI in a separate thread
    threading.Thread(target=run_api, daemon=True).start()
    
    # Run the Discord bot
    bot.run(os.environ["DISCORD_TOKEN"])
