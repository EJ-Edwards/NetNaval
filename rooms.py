import random

class Room:
    rooms = {}  
    def __init__(self, host_id):
        self.host_id = host_id
        self.players = [host_id]
        self.boards = {}      
        self.ships = {}       
        self.radars = {}      
        self.turn_index = 0   
        self.pin = self.generate_pin()
        Room.rooms[self.pin] = self

        self.boards[host_id] = [["~" for _ in range(10)] for _ in range(10)]
        self.ships[host_id] = []
        self.radars[host_id] = [["~" for _ in range(10)] for _ in range(10)]

    @staticmethod
    def generate_pin():
        """Generates a unique 4-digit PIN for the room."""
        while True:
            pin = str(random.randint(1000, 9999))
            if pin not in Room.rooms:
                return pin

    @classmethod
    def get_room(cls, pin):
        """Returns the room object for a given PIN."""
        return cls.rooms.get(str(pin))

    def add_player(self, player_id):
        """Adds a player to the room. Returns False if full, True if added."""
        if len(self.players) >= 2:
            return False
        if player_id not in self.players:
            self.players.append(player_id)
            self.boards[player_id] = [["~" for _ in range(10)] for _ in range(10)]
            self.ships[player_id] = []
            self.radars[player_id] = [["~" for _ in range(10)] for _ in range(10)]
        return True

    def remove_player(self, player_id):
        """Removes a player. Deletes the room if empty."""
        if player_id in self.players:
            self.players.remove(player_id)
            self.boards.pop(player_id, None)
            self.ships.pop(player_id, None)
            self.radars.pop(player_id, None)

        if not self.players:
            del Room.rooms[self.pin]

    def get_current_player(self):
        """Returns the user ID of the current player whose turn it is."""
        if not self.players:
            return None
        return self.players[self.turn_index]

    def switch_turn(self):
        """Switches turn to the next player."""
        if len(self.players) > 1:
            self.turn_index = (self.turn_index + 1) % len(self.players)
