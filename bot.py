import discord
from discord.ext import commands
from rooms import Room  # Import the Room class
import random

# ----------------------------
# Bot setup and global variables
# ----------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Game state variables
Playing = False               
board_player = []             
board_bot = []                
board_radar = []              
ships_player = []             
ships_bot = []               

# ----------------------------
# Helper functions
# ----------------------------
def create_board():
    """Creates a 10x10 board filled with '~' representing water."""
    return [["~" for _ in range(10)] for _ in range(10)]

def place_bot_ships(board, ships, count=3):
    """Randomly places 'count' ships on the bot's board."""
    while len(ships) < count:
        r = random.randint(0, 9)
        c = random.randint(0, 9)
        if board[r][c] == "~":
            board[r][c] = "S"
            ships.append((r, c))

async def render(ctx, board, hide_ships=False):
    """Renders a board using emojis and sends it to Discord."""
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

# ----------------------------
# Bot events
# ----------------------------
@bot.event
async def on_ready():
    """Triggered when the bot is ready and connected to Discord."""
    print(f"✅ Logged in as {bot.user}")

# ----------------------------
# Bot commands
# ----------------------------
@bot.command()
async def credits(ctx):
    """Displays credits and documentation link."""
    await ctx.send(
        "🚢 **NetNaval**\n"
        "Developed by **EJ**\n"
        "Documentation: https://ej-edwards.github.io/NetNaval/\n"
        "Thanks for playing!"
    )

@bot.command()
async def start(ctx):
    """Starts a new single-player Battleship game."""
    global Playing, board_player, board_bot, board_radar, ships_player, ships_bot

    if Playing:
        await ctx.send("❗ A game is already in progress.")
        return

    # Initialize boards and ships
    Playing = True
    board_player = create_board()
    board_bot = create_board()
    board_radar = create_board()
    ships_player = []
    ships_bot = []

    place_bot_ships(board_bot, ships_bot)

    await ctx.send("🚢 **New Battleship game started!**")
    await ctx.send("Place 3 ships using: `!place A1 B2 C3`")

@bot.command()
async def place(ctx, *positions):
    """Places player's ships on their board."""
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

    await ctx.send("✅ Ships placed! **Your board:**")
    await render(ctx, board_player)

@bot.command()
async def fire(ctx, position):
    """Player fires at bot's board, updates radar, and triggers bot's turn."""
    global Playing, ships_bot

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

    if board_radar[row][col] in ["X", "O"]:
        await ctx.send("❗ You already fired there.")
        return

    if (row, col) in ships_bot:
        board_radar[row][col] = "X"
        board_bot[row][col] = "X"
        ships_bot.remove((row, col))
        await ctx.send("💥 **Hit!**")
    else:
        board_radar[row][col] = "O"
        await ctx.send("🌊 **Miss!**")

    await ctx.send("🎯 **Radar Board**")
    await render(ctx, board_radar, hide_ships=True)

    # Win condition
    if not ships_bot:
        await ctx.send("🏆 **You sank all enemy ships — YOU WIN!**")
        Playing = False
        return

    await bot_turn(ctx)

async def bot_turn(ctx):
    """Bot randomly fires at player's board."""
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

    await ctx.send("🛡️ **Your Board**")
    await render(ctx, board_player)

    if not ships_player:
        await ctx.send("💀 **All your ships were sunk — YOU LOSE.**")
        Playing = False

# ----------------------------
# Multiplayer room commands
# ----------------------------
@bot.command()
async def create(ctx):
    """Creates a multiplayer room and generates a unique PIN."""
    room = Room(ctx.author.id)
    await ctx.send(f"✅ Room created! PIN: {room.pin}")

@bot.command()
async def join(ctx, pin):
    """Join an existing multiplayer room using a PIN."""
    room = Room.get_room(pin)
    if room:
        room.add_player(ctx.author.id)
        await ctx.send("✅ Joined the room!")
    else:
        await ctx.send("❌ Room not found.")
