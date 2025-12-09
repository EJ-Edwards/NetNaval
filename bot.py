import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

Playing = False
board1 = []
board2 = []
ships1 = []
ships2 = []

def create_board():
    return [["~" for _ in range(10)] for _ in range(10)]

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

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def start(ctx):
    global Playing, board1, board2, ships1, ships2
    if Playing:
        await ctx.send("A game is already in progress!")
        return

    Playing = True
    board1 = create_board()
    board2 = create_board()
    ships1 = []
    ships2 = []

    await ctx.send("Starting a new game of Battleships!")
    await ctx.send("Place your ships using `!place A1 B2 C3`")

@bot.command()
async def place(ctx, *positions):
    global board1, ships1
    if not Playing:
        await ctx.send("Start a game first with `!start`")
        return

    if len(positions) != 3:
        await ctx.send("You need to place exactly 3 ships!")
        return

    alphabet = "ABCDEFGHIJ"
    for pos in positions:
        try:
            row = alphabet.index(pos[0].upper())
            col = int(pos[1:]) - 1
        except (ValueError, IndexError):
            await ctx.send(f"Invalid position: {pos}")
            return

        if board1[row][col] == "S":
            await ctx.send(f"Ship already placed at {pos}")
            return
        board1[row][col] = "S"
        ships1.append((row, col))

    await ctx.send("Ships placed!")
    await render(ctx, board1)
