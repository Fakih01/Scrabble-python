from scrabble import *


class Player:
    def __init__(self, bag):
        # Intializes a player instance. Creates the player's rack by creating an instance of that class.
        # Takes the bag as an argument, in order to create the rack.
        self._turn_score = 0
        self._player_score = 0
        self.total_score = 0
        self._player_rack = []
        self.bag = bag
        self._draw_tiles(7)
        self.blank_tile_indices = [i for i, letter in enumerate(self._player_rack) if letter == ' ']

    def _draw_tiles(self, amount):
        """
        Removes the specified number of tiles from the bag and puts them into
        the player rack.
        """
        for _ in range(amount):
            if len(self.bag._bag) > 0:
                self._player_rack.append(self.bag._bag.pop())
        #print("we're drawing tiles", self._player_rack)

    def num_remaining_tiles(self):
        """
        Returns how many tiles remain in the bag.
        """
        print("Tiles left =", len(self.bag._bag))
        return len(self.bag._bag)

    def exchange_tiles(self, old):
        """
        Returns the old tiles to the bag and draws an equal number to replace
        them.
        """
        # Only can return letters from the player's rack
        if self._all_letters_from_rack(old):
            # Make sure there is enough letters to exchange
            if len(old) > len(self.bag._bag):
                return

            # Add the new tiles to the rack
            self._draw_tiles(len(old))

            # Remove the old from the rack and add them to the bag
            for letter in old:
                self._player_rack.remove(letter)
                self.bag._bag.append(letter)

            self.bag.shuffle_bag()

    def _update_player_rack(self, tiles):
        """
        Removed the letters from the player rack and draw new ones.
        """
        for _, _, letter in tiles:
            self._player_rack.remove(letter)

        self._draw_tiles(len(tiles))
        print("updated rack should be", self._player_rack)

    def _all_letters_from_rack(self, letters):
        """
        Determines if all letters are present in the player's rack.
        """
        rack = self._player_rack[:]
        #print("Checking rack:", rack)  # Debugging line
        #print("Checking letters:", letters)  # Debugging line
        for letter in letters:
            if letter in rack:
                rack.remove(letter)
            else:
                print("Validation: Not all letters are from the rack")
                return False

        # All letters were in the rack
        return True

    def get_rack(self):
        #print("get_rack called", self._player_rack)
        return self._player_rack

    def _score_word(self, SBoard, start, end, letters):
        """
        Adds the score of the valid word between start and end.
        """
        score = 0
        multiplier = 1
        for row in range(start[0], end[0] + 1):
            for col in range(start[1], end[1] + 1):
                if (row, col) in letters:
                    # Check for score modifiers
                    multiplier *= WORD_MULTIPLIERS.get((row, col), 1)
                    score += POINTS[letters[(row, col)]]*LETTER_MULTIPLIERS.get((row, col), 1)
                else:
                    # Tile must be on board, add it's value
                    score += POINTS[SBoard[row][col]]
        self._turn_score = 0
        self._turn_score += score*multiplier
        print("Score for this word is:", self._turn_score)

    def get_turn_score(self):

        return self._turn_score

    def _score_turn(self, tiles):
        """
        Applies the score of the last validated move to the player score.
        """
        self._player_score += self._turn_score
        # Check for Bingo
        if len(tiles) == 7:
            self._player_score += 50

    def get_total_score(self):
        return self._player_score


class Bag:
    def __init__(self):
        self._bag = []
        self._populate_bag()
        self.shuffle_bag()

    def _populate_bag(self):
        """
        Fills the bag with the starting letter frequencies.
        """
        self._bag = []
        for letter in DISTRIBUTION:
            for _ in range(DISTRIBUTION[letter]):
                self._bag.append(letter)

    def shuffle_bag(self):
        """
        Randomizes contents of the bag.
        """
        shuffle(self._bag)


def test2():
    # Instantiate Bag
    bag = Bag()
    assert len(bag._bag) == 100  # As per standard Scrabble rules

    # Instantiate Player with Bag
    player = Player(bag)
    assert len(player._player_rack) == 7  # A player should start with 7 tiles

    # Test number of remaining tiles in the bag
    assert player.num_remaining_tiles() == 93  # 100 total - 7 drawn for player

    # Test exchanging tiles
    old_tiles = player._player_rack[:3]  # Let's exchange the first 3 tiles
    player.exchange_tiles(old_tiles)
    assert len(player._player_rack) == 7  # Player should still have 7 tiles
    assert player.num_remaining_tiles() == 93  # 100 total - 7 drawn for player
    assert old_tiles not in player._player_rack  # The old tiles should no longer be in the player's rack

    # Test rack update
    player._update_player_rack([('a', 'b', tile) for tile in player._player_rack[:0]])
    assert len(player._player_rack) == 7  # Player should still have 7 tiles
    assert player.num_remaining_tiles() == 93  # 100 total - 10 drawn for player

    # Test scoring
    SBoard = [[''] * 15 for _ in range(15)]  # Assume an empty Scrabble board
    start = (0, 0)
    end = (0, 2)
    letters = {(0, i): player._player_rack[i] for i in range(3)}  # Create a 3-letter word at the top left of the board
    player._score_word(SBoard, start, end, letters)
    # Add more assertions here as needed, depending on your POINTS and MULTIPLIERS
