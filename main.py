import os
import threading
import uvicorn
from fastapi import FastAPI
from discord.ext import commands

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

def run_api():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

intents = commands.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

def run_bot():
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    run_bot()
