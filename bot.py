import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

Playing = False
board_player = []
board_bot = []
ships_player = []
ships_bot = []

def create_board():
    return [["~" for _ in range(10)] for _ in range(10)]

def place_bot_ships(board, ships, count=3):
    while len(ships) < count:
        r = random.randint(0, 9)
        c = random.randint(0, 9)
        if board[r][c] == "~":
            board[r][c] = "S"
            ships.append((r, c))

async def render(ctx, board, hide_ships=False):
    numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    letters = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯"]

    display = "⬛ " + " ".join(numbers) + "\n"
    for i, row in enumerate(board):
        display += letters[i]
        for cell in row:
            if cell == "~":
                display += "🟦"
            elif cell == "S":
                display += "🟦" if hide_ships else "🚢"
            elif cell == "X":
                display += "💥"
            elif cell == "O":
                display += "⚪"
        display += "\n"
    await ctx.send(display)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def credits(ctx):
    await ctx.send(
        "🚢 **NetNaval**\n"
        "Developed by **EJ**\n"
        "Documentation: https://ej-edwards.github.io/NetNaval/\n"
        "Thanks for playing!"
    )

@bot.command()
async def start(ctx):
    global Playing, board_player, board_bot, ships_player, ships_bot

    if Playing:
        await ctx.send("❗ A game is already in progress.")
        return

    Playing = True
    board_player = create_board()
    board_bot = create_board()
    ships_player = []
    ships_bot = []

    place_bot_ships(board_bot, ships_bot)

    await ctx.send("🚢 **New Battleship game started!**")
    await ctx.send("Place 3 ships using: `!place A1 B2 C3`")

@bot.command()
async def place(ctx, *positions):
    global ships_player

    if not Playing:
        await ctx.send("Start a game with `!start`.")
        return

    if len(positions) != 3:
        await ctx.send("You must place **exactly 3 ships**.")
        return

    alphabet = "ABCDEFGHIJ"

    for pos in positions:
        try:
            row = alphabet.index(pos[0].upper())
            col = int(pos[1:]) - 1
            if board_player[row][col] != "~":
                raise ValueError
        except:
            await ctx.send(f"❌ Invalid position: `{pos}`")
            return

        board_player[row][col] = "S"
        ships_player.append((row, col))

    await ctx.send("✅ Ships placed! Your board:")
    await render(ctx, board_player)

@bot.command()
async def fire(ctx, position):
    global Playing, ships_bot, ships_player

    if not Playing:
        await ctx.send("Start a game with `!start`.")
        return

    alphabet = "ABCDEFGHIJ"
    try:
        row = alphabet.index(position[0].upper())
        col = int(position[1:]) - 1
    except:
        await ctx.send("❌ Invalid position. Example: `!fire B7`")
        return

    if (row, col) in ships_bot:
        board_bot[row][col] = "X"
        ships_bot.remove((row, col))
        await ctx.send("💥 **Hit!**")
    else:
        board_bot[row][col] = "O"
        await ctx.send("🌊 **Miss!**")

    if not ships_bot:
        await ctx.send("🏆 **You sank all enemy ships — YOU WIN!**")
        Playing = False
        return

    await bot_turn(ctx)

async def bot_turn(ctx):
    global Playing, ships_player

    while True:
        r = random.randint(0, 9)
        c = random.randint(0, 9)
        if board_player[r][c] in ["~", "S"]:
            break

    if (r, c) in ships_player:
        board_player[r][c] = "X"
        ships_player.remove((r, c))
        await ctx.send("🤖 **Bot hit your ship!**")
    else:
        board_player[r][c] = "O"
        await ctx.send("🤖 Bot missed.")

    if not ships_player:
        await ctx.send("💀 **All your ships were sunk — YOU LOSE.**")
        Playing = False
