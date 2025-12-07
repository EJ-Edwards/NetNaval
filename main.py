import os
import threading
from fastapi import FastAPI
import uvicorn
from discord.ext import commands

# ---------------------------
# Discord Bot Setup
# ---------------------------
intents = commands.Intents.default()
intents.message_content = True  # Required for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.environ.get("DISCORD_TOKEN")  # Make sure this is set in Render

# Example bot command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# ---------------------------
# FastAPI Setup
# ---------------------------
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running!"}

def run_api():
    port = int(os.environ.get("PORT", 10000))  # Render sets this automatically
    uvicorn.run(app, host="0.0.0.0", port=port)

# ---------------------------
# Run both
# ---------------------------
if __name__ == "__main__":
    # Start FastAPI in a separate thread
    threading.Thread(target=run_api, daemon=True).start()
    # Start Discord bot (blocking call)
    bot.run(TOKEN)
