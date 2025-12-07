import os
import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

Playing = False
board1 = ""
board2 = ""
boardtoshow1 = ""
boardtoshow2 = ""

async def render(ctx, board):
    numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    alphabet = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯"]

    display = "⬛ " + " ".join(numbers) + "\n"

    for i, row in enumerate(board):
        display += alphabet[i]
        for cell in row:
            if cell == "~":
                display += "🟦"
            elif cell == "S":
                display += "🚢"
            elif cell == "X":
                display += "💥"
            elif cell == "O":
                display += "⚪"
            else:
                display += "⬛"
        display += "\n"

    await ctx.send(display)

@bot.command()
async def start(ctx):
    global Playing
    if Playing:
        await ctx.send("A game is already in progress!")
    else:
        Playing = True
        await ctx.send("Starting a new game of Battleships!")

bot.run(TOKEN)
