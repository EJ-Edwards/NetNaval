import os
import asyncio
import discord
from discord.ext import commands
from fastapi import FastAPI
import uvicorn

# ---------- Discord Setup ----------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 pong")

# ---------- FastAPI Setup ----------
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

# ---------- Combined Runner ----------
async def main():
    port = int(os.environ.get("PORT", 10000))

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    await asyncio.gather(
        server.serve(),
        bot.start(os.environ["DISCORD_TOKEN"])
    )

if __name__ == "__main__":
    asyncio.run(main())
