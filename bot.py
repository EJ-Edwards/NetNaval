import discord
from discord.ext import commands
from rooms import Room
import random
import aiohttp

# Bot setup

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Single-player game state
Playing = False
board_player = []
board_bot = []
board_radar = []
ships_player = []
ships_bot = []

# Helper functions
def create_board():
    return [["~"]*10 for _ in range(10)]

def place_bot_ships(board, ships, count=3):
    while len(ships) < count:
        r, c = random.randint(0,9), random.randint(0,9)
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

# Events
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Commands
@bot.command()
async def credits(ctx):
    await ctx.send(
        "🚢 **NetNaval**\n"
        "Developed by **EJ**\n"
        "Documentation: https://ej-edwards.github.io/NetNaval/\n"
        "Thanks for playing!"
    )

# Single-player commands
@bot.command()
async def start(ctx):
    global Playing, board_player, board_bot, board_radar, ships_player, ships_bot
    if Playing:
        await ctx.send("❗ A game is already in progress.")
        return
    Playing = True
    board_player = create_board()
    board_bot = create_board()
    board_radar = create_board()
    ships_player = []
    ships_bot = []
    place_bot_ships(board_bot, ships_bot)
    await ctx.send("🚢 **Single-player game started!**")
    await ctx.send("Place 3 ships using: `!place A1 B2 C3`")

@bot.command()
async def stop(ctx):
    global Playing
    # Multiplayer check
    room = next((r for r in Room.rooms.values() if ctx.author.id in r.players), None)
    if room:
        room.remove_player(ctx.author.id)
        await ctx.send(f"❌ {ctx.author.name} left the room.")
        if room.players:
            await ctx.send(f"ℹ️ {room.get_current_player().mention}, the other player left.")
        return
    # Single-player stop
    if Playing:
        Playing = False
        await ctx.send("🛑 Single-player game stopped.")
        return
    await ctx.send("❌ No game or room to stop.")

# Place ships
@bot.command()
async def place(ctx, *positions):
    room = next((r for r in Room.rooms.values() if ctx.author.id in r.players), None)
    alphabet = "ABCDEFGHIJ"

    # Multiplayer
    if room:
        if len(positions) != 3:
            await ctx.send("You must place exactly 3 ships.")
            return
        board = room.boards[ctx.author.id]
        ships = room.ships[ctx.author.id]
        for pos in positions:
            try:
                row = alphabet.index(pos[0].upper())
                col = int(pos[1:])-1
                if board[row][col] != "~":
                    raise ValueError
            except:
                await ctx.send(f"❌ Invalid position: `{pos}`")
                return
            board[row][col] = "S"
            ships.append((row, col))
        await ctx.send("✅ Ships placed! **Your board:**")
        await render(ctx, board)
        return

    # Single-player
    global ships_player, board_player
    if not Playing:
        await ctx.send("Start a game with `!start`.")
        return
    if len(positions) != 3:
        await ctx.send("You must place exactly 3 ships.")
        return
    for pos in positions:
        try:
            row = alphabet.index(pos[0].upper())
            col = int(pos[1:])-1
            if board_player[row][col] != "~":
                raise ValueError
        except:
            await ctx.send(f"❌ Invalid position: `{pos}`")
            return
        board_player[row][col] = "S"
        ships_player.append((row, col))
    await ctx.send("✅ Ships placed! **Your board:**")
    await render(ctx, board_player)

# Fire
@bot.command()
async def fire(ctx, position):
    alphabet = "ABCDEFGHIJ"
    room = next((r for r in Room.rooms.values() if ctx.author.id in r.players), None)

    # Multiplayer
    if room:
        if ctx.author.id != room.get_current_player():
            await ctx.send("❗ It's not your turn!")
            return
        opponent_id = [p for p in room.players if p != ctx.author.id][0]
        board_opponent = room.boards[opponent_id]
        radar = room.radars[ctx.author.id]
        ships_opponent = room.ships[opponent_id]
        try:
            row = alphabet.index(position[0].upper())
            col = int(position[1:])-1
        except:
            await ctx.send("❌ Invalid position.")
            return
        if radar[row][col] in ["X","O"]:
            await ctx.send("❗ Already fired there.")
            return
        if (row,col) in ships_opponent:
            radar[row][col] = "X"
            board_opponent[row][col] = "X"
            ships_opponent.remove((row,col))
            await ctx.send("💥 **Hit!**")
        else:
            radar[row][col] = "O"
            await ctx.send("🌊 **Miss!**")
        await ctx.send("🎯 **Radar Board**")
        await render(ctx, radar, hide_ships=True)
        if not ships_opponent:
            await ctx.send(f"🏆 **{ctx.author.name} wins!**")
            del Room.rooms[room.pin]
            return
        room.switch_turn()
        await ctx.send(f"🔄 It's now {room.get_current_player().mention}'s turn.")
        return

    # Single-player
    global board_radar, board_bot, ships_bot, board_player, ships_player
    if not Playing:
        await ctx.send("Start a game with `!start`.")
        return
    try:
        row = alphabet.index(position[0].upper())
        col = int(position[1:])-1
    except:
        await ctx.send("❌ Invalid position. Example: `!fire B7`")
        return
    if board_radar[row][col] in ["X","O"]:
        await ctx.send("❗ Already fired there.")
        return
    if (row,col) in ships_bot:
        board_radar[row][col] = "X"
        board_bot[row][col] = "X"
        ships_bot.remove((row,col))
        await ctx.send("💥 **Hit!**")
    else:
        board_radar[row][col] = "O"
        await ctx.send("🌊 **Miss!**")
    await ctx.send("🎯 **Radar Board**")
    await render(ctx, board_radar, hide_ships=True)
    if not ships_bot:
        await ctx.send("🏆 **You sank all enemy ships — YOU WIN!**")
        Playing = False
        return
    await bot_turn(ctx)


async def bot_turn(ctx):
    global board_player, ships_player, Playing
    while True:
        r,c = random.randint(0,9), random.randint(0,9)
        if board_player[r][c] in ["~","S"]:
            break
    if (r,c) in ships_player:
        board_player[r][c] = "X"
        ships_player.remove((r,c))
        await ctx.send("🤖 **Bot hit your ship!**")
    else:
        board_player[r][c] = "O"
        await ctx.send("🤖 Bot missed.")
    await ctx.send("🛡️ **Your Board**")
    await render(ctx, board_player)
    if not ships_player:
        await ctx.send("💀 **All your ships were sunk — YOU LOSE.**")
        Playing = False


@bot.command()
async def create(ctx):
    for room in Room.rooms.values():
        if room.host_id == ctx.author.id:
            await ctx.send(f"❌ You already have a room! PIN: {room.pin}")
            return
    room = Room(ctx.author.id)
    await ctx.send(f"✅ Room created! PIN: {room.pin}")

@bot.command()
async def join(ctx, pin):
    room = Room.get_room(str(pin))
    if not room:
        await ctx.send("❌ Room not found.")
        return
    success = room.add_player(ctx.author.id)
    if not success:
        await ctx.send("❌ Room is full.")
        return
    await ctx.send(f"✅ Joined room {pin}! Waiting for host to start the game.")

@bot.command()
async def ping(ctx):
    """Wake up the API server (useful for Render or similar)."""
    api_url = "https://netnaval.onrender.com"  
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as resp:
                if resp.status == 200:
                    await ctx.send("✅ API is awake and ready!")
                else:
                    await ctx.send(f"⚠️ API responded with status {resp.status}.")
    except Exception as e:
        await ctx.send(f"❌ Could not reach the API: {e}")
