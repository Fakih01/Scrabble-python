import itertools
from random import shuffle

from scoringSystem import *
import twl
from gamestate import *


class Scrabble:
    moveCount = 0

    def __init__(self, debug, num_players):
        self.debug = debug
        self.SBoard = [
            [None]*15 for _ in range(15)
        ]
        self.player = player
        self.players = [Player() for _ in range(num_players)]

    def _print_board(self):  #  prints board when p is pressed
        """
        Prints an ASCII representation of the board
        """
        for i in range(15):
            for j in range(15):
                if self.SBoard[j][i] == None:
                    print('_', end='')
                elif self.SBoard[j][i] == ' ':
                    print('-', end='')
                else:
                    print(self.SBoard[j][i], end='')
            print('')
        print("Rack: ", self.player._player_rack)
        return self.player._player_rack

    def submit_turn(self, tiles):
        """
        Given a list of tiles (i, j, letter), check if valid, place on to board
        and add to player score.
        """
        print("Tiles submitted:", tiles)
        if self._is_valid_move(tiles):
            self.player._score_turn(tiles)
            self._place_move(tiles)
            self.player._update_player_rack(tiles)
            return True
        else:
            return False

    def _is_valid_move(self, tiles):
        """
        Returns True if the list of tiles forms valid words and are placed
        in a correct manner.
        """
        rows = []
        cols = []
        letters = []

        for row, col, letter in tiles:
            rows.append(row)
            cols.append(col)
            letters.append(letter)

        # Reset score accumulation
        self._turn_score = 0

        return (
            self.player._all_letters_from_rack(letters) and
            self._is_colinear(rows, cols) and
            self._all_unique_places(rows, cols) and
            self._is_contiguous(rows, cols) and
            self._touches_others(rows, cols) and
            self._all_valid_words(tiles)
        )

    def _is_colinear(self, rows, cols):
        """
        True if all rows are equal or all cols are equal.
        """
        ret = len(set(rows)) == 1 or len(set(cols)) == 1
        if self.debug and ret == False:
            print("Validation: Tiles are not colinear")

        return ret

    def _all_unique_places(self, rows, cols):
        """
        Cannot have duplicate places
        """
        places = list(zip(rows, cols))
        ret = len(set(places)) == len(places)
        if self.debug and ret == False:
            print("Validation: Tiles are not uniquely placed")
            print(places)
        return ret

    def _is_contiguous(self, rows, cols):
        """
        Tiles must be in a contiguous line with existing tiles, if needed.
        """
        # Case: Only one tile
        if len(cols) == len(rows) == 1:
            return True

        is_vertical = len(set(cols)) == 1

        if is_vertical:
            start = min(rows)
            end = max(rows)
            col = cols[0]

            for row in range(start, end):
                if row not in rows and self.SBoard[row][col] == None:
                    if self.debug:
                        print("Validation: Tiles are not contiguous")
                    return False

        else:
            start = min(cols)
            end = max(cols)
            row = rows[0]

            for col in range(start, end):
                if col not in cols and self.SBoard[row][col] == None:
                    if self.debug:
                        print("Validation: Tiles are not contiguous")
                    return False

        return True

    def _touches_others(self, rows, cols):
        """
        Word being played must touch existing tiles, or first move must start
        in the middle of the board.
        """
        places = list(zip(rows, cols))

        if Scrabble.moveCount == 0:
            ret = (7, 7) in places
            if self.debug and ret == False and Scrabble.moveCount < 1:
                print("Validation: First move wasn't on star")
            return ret
        else:
            for row, col in places:
                # Above
                if row > 0 and self.SBoard[row - 1][col] is not None:
                    return True
                # Below
                if row < 14 and self.SBoard[row + 1][col] is not None:
                    return True
                # Left
                if col > 0 and self.SBoard[row][col - 1] is not None:
                    return True
                # Right
                if col < 14 and self.SBoard[row][col + 1] is not None:
                    return True

            # Made it through each tile without touching, invalid
            if self.debug:
                print("Validation: Tiles do not touch existing tiles")
            return False

    def _all_valid_words(self, tiles):
        """
        Determines if all the words formed are valid.
        Accumulates the score for valid words
        Assumes tiles are colinear and contiguous.
        """
        rows = []
        cols = []
        letters = {}
        for row, col, letter in tiles:
            rows.append(row)
            cols.append(col)
            letters[(row, col)] = letter

        is_vertical = len(set(cols)) == 1

        if is_vertical:  # Also true if only one tile was placed
            start = min(rows)
            end = max(rows)
            col = cols[0]

            # Start may be extended by existing tiles
            for row in range(start - 1, -1, -1):
                if self.SBoard[row][col] is not None:
                    start = row
                else:
                    # Found first open place, quit
                    break
            # Same for the end
            for row in range(end + 1, 15):
                if self.SBoard[row][col] is not None:
                    end = row
                else:
                    # Found first open place, quit
                    break

            # If only one tile was played, there may not be a vertical word
            if start != end:
                # Check the word that was made vertically
                word = ''
                for row in range(start, end + 1):
                    word += letters.get((row, col), self.SBoard[row][col])
                if not self._is_valid_word(word):
                    if self.debug:
                        print("Validation: Invalid word:", word)
                    return False

                self.player._score_word(self.SBoard, (start, col), (end, col), letters)

            # Check all horizontal words made from each of the new tiles
            for row, col, _ in tiles:
                start_h = col
                end_h = col

                # Start may be extended by existing tiles
                for col_h in range(start_h - 1, -1, -1):
                    if self.SBoard[row][col_h] is not None:
                        start_h = col_h
                    else:
                        # Found first open place, quit
                        break
                # Same for the end
                for col_h in range(end_h + 1, 15):
                    if self.SBoard[row][col_h] is not None:
                        end_h = col_h
                    else:
                        # Found first open place, quit
                        break

                # No word made horizontally
                if start_h == end_h:
                    # Issue if only one tile was placed on start
                    if len(tiles) == 1:
                        if self.debug:
                            print("Validation: Only placed one tile on start")
                        return False
                    continue

                # Make and check word
                word = ''
                for col_h in range(start_h, end_h + 1):
                    word += letters.get((row, col_h), self.SBoard[row][col_h])
                if not self._is_valid_word(word):
                    if self.debug:
                        print("Validation: Invalid word:", word)
                    return False

                self.player._score_word(self.SBoard, (row, start_h), (row, end_h), letters)

        else:  # is horizontal
            start = min(cols)
            end = max(cols)
            row = rows[0]

            # Start may be extended by existing tiles
            for col in range(start - 1, -1, -1):
                if self.SBoard[row][col] is not None:
                    start = col
                else:
                    # Found first open place, quit
                    break
            # Same for the end
            for col in range(end + 1, 15):
                if self.SBoard[row][col] is not None:
                    end = col
                else:
                    # Found first open place, quit
                    break


            # Check the word that was made horizontally
            word = ''
            for col in range(start, end + 1):
                word += letters.get((row, col), self.SBoard[row][col])
            if not self._is_valid_word(word):
                if self.debug:
                    print("Validation: Invalid word:", word)
                return False

            self.player._score_word(self.SBoard, (row, start), (row, end), letters)

            # Check all vertical words made from each of the new tiles
            for row, col, _ in tiles:
                start_v = row
                end_v = row

                # Start may be extended by existing tiles
                for row_v in range(start_v - 1, -1, -1):
                    if self.SBoard[row_v][col] is not None:
                        start_v = row_v
                    else:
                        # Found first open place, quit
                        break
                # Same for the end
                for row_v in range(end_v + 1, 15):
                    if self.SBoard[row_v][col] is not None:
                        end_v = row_v
                    else:
                        # Found first open place, quit
                        break

                # No word made vertically
                if start_v == end_v:
                    continue

                # Make and check word
                word = ''
                for row_v in range(start_v, end_v + 1):
                    word += letters.get((row_v, col), self.SBoard[row_v][col])
                if not self._is_valid_word(word):
                    if self.debug:
                        print("Validation: Invalid word:", word)
                    return False

                self.player._score_word(self.SBoard, (start_v, col), (end_v, col), letters)

        # Validated all words
        if self.debug:
            print("All words validated")
        return True

    def _is_valid_word(self, word):
        """
        Uses twl to determine if word is a valid word.
        """
        word = word.lower()
        ret = twl.check(word)  # checks if word is valid
        if self.debug:
            print(f"Word '{word}' is valid? {ret}")
        #list(twl.anagram(word))
        return twl.check(word)

    def _place_move(self, tiles):
        """
        Given a valid set of tiles, adds them to the board.
        """
        Scrabble.moveCount += 1
        print("Move count=", Scrabble.moveCount)
        for row, col, letter in tiles:
            self.SBoard[row][col] = letter


class Player:
    def __init__(self):
        # Intializes a player instance. Creates the player's rack by creating an instance of that class.
        # Takes the bag as an argument, in order to create the rack.
        self._turn_score = 0
        self.name = ""
        self._player_rack = []
        self._bag = []
        self._populate_bag()
        self.shuffle_bag()
        self._draw_tiles(7)
        self._player_score = 0
        self.total_score = 0

    def set_name(self, name):
        # Sets the player's name.
        self.name = name

    def get_name(self):
        # Gets the player's name.
        return self.name

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
        Randomizes the contents of the bag.
        """
        shuffle(self._bag)

    def _draw_tiles(self, amount):
        """
        Removes the specified number of tiles from the bag and puts them into
        the player rack.
        """
        for _ in range(amount):
            if len(self._bag) > 0:
                self._player_rack.append(self._bag.pop())

    def num_remaining_tiles(self):
        """
        Returns how many tiles remain in the bag.
        """
        return len(self._bag)

    def get_rack(self):
        """
        Returns a copy of the player's rack
        """
        print("get_rack called", self._player_rack)  # wrong rack called  # works now
        return self._player_rack

    def exchange_tiles(self, old):
        """
        Returns the old tiles to the bag and draws an equal number to replace
        them.
        """
        # Only can return letters from the player's rack
        if self._all_letters_from_rack(old):
            # Make sure there is enough letters to exchange
            if len(old) > len(self._bag):
                return

            # Add the new tiles to the rack
            self._draw_tiles(len(old))

            # Remove the old from the rack and add them to the bag
            for letter in old:
                self._player_rack.remove(letter)
                self._bag.append(letter)

            self.shuffle_bag()

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
        print("Checking rack:", rack)  # Debugging line
        print("Checking letters:", letters)  # Debugging line
        for letter in letters:
            if letter in rack:
                rack.remove(letter)
            else:
                print("Validation: Not all letters are from the rack")
                return False

        # All letters were in the rack
        return True

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
        #self.increase_score(self._turn_score)
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
        # Reset turn score counter
        #self._turn_score = 0

        #print("Total score for this player:", self._player_score)

    def increase_score(self, increase):
        #Increases the player's score by a certain amount. Takes the increase (int) as an argument and adds it to the score.
        self._turn_score += increase
        print("increased player score: ", self._player_score)
        return self._turn_score

    def get_total_score(self):
        #print("Total score for this player is: ", self._player_score)
        return self._player_score


player = Player()


def test():
    scrabble = Scrabble(True)

    scrabble._print_board()


if __name__ == '__main__':
    test()

