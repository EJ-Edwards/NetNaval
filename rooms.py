import random

class Room:
    """
    Represents a multiplayer game room.
    Handles room creation, unique PIN generation, player management, and room deletion.
    """
    rooms = {}  # Class-level dictionary storing all active rooms

    def __init__(self, host_id):
        self.host_id = host_id
        self.players = [host_id]      # List of player IDs in the room
        self.state = {}               # Can store board states, turns, etc.
        self.pin = self.generate_pin()
        Room.rooms[self.pin] = self   # Register room in global dictionary

    @classmethod
    def generate_pin(cls):
        """Generates a unique 4-digit PIN for the room."""
        while True:
            pin = str(random.randint(1000, 9999))
            if pin not in cls.rooms:
                return pin

    @classmethod
    def get_room(cls, pin):
        """Returns the Room object for a given PIN or None if not found."""
        return cls.rooms.get(pin)

    def add_player(self, player_id):
        """Adds a player to the room if they are not already in it."""
        if player_id not in self.players:
            self.players.append(player_id)

    def remove_player(self, player_id):
        """Removes a player and deletes the room if empty."""
        if player_id in self.players:
            self.players.remove(player_id)
        if not self.players:
            # Delete the room from the global dictionary if no players left
            del Room.rooms[self.pin]
