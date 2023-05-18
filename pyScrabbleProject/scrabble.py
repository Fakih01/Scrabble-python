import itertools
from random import shuffle
from scoringSystem import *
import twl
from player import *
from gamestate import *


class Scrabble:
    moveCount = 0

    def __init__(self, debug, players, num_players):
        self.debug = debug
        self.SBoard = [
            [None]*15 for _ in range(15)
        ]
        self.bag = Bag()
        self.players = players
        self.current_player_index = 1
        self.num_players = num_players

        if isinstance(players, dict):
            self.players = players
        else:
            self.players = {1: players}

        self.current_player_index = 1

    def current_player(self):
        return self.players[self.current_player_index]

    def switch_turn(self):
        self.current_player_index = 1 if self.current_player_index == 2 else 2  # Switch between player 1 and 2
        print("It's now player", self.current_player_index, "'s turn.")

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
        print("Rack: ", self.current_player()._player_rack)
        return self.current_player()._player_rack

    def submit_turn(self, tiles):
        """
        Given a list of tiles (i, j, letter), check if valid, place on to board
        and add to player score.
        """
        print("Tiles submitted:", tiles)
        if self._is_valid_move(tiles):
            self.current_player()._score_turn(tiles)
            self._place_move(tiles)
            self.current_player()._update_player_rack(tiles)
            if self.num_players == 2:
                self.switch_turn()
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
            self.current_player()._all_letters_from_rack(letters) and
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

            for row in range(start, end + 1):
                if row not in rows and self.SBoard[row][col] == None:
                    if self.debug:
                        print("Validation: Tiles are not contiguous")
                    return False

        else:
            start = min(cols)
            end = max(cols)
            row = rows[0]

            for col in range(start, end + 1):
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
                # Check if the submitted tile is placed on an existing tile
                if self.SBoard[row][col] is not None:
                    return True

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

                self.current_player()._score_word(self.SBoard, (start, col), (end, col), letters)

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
                    if len(tiles) == 1 and Scrabble.moveCount == 0:
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

                self.current_player()._score_word(self.SBoard, (row, start_h), (row, end_h), letters)

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

            self.current_player()._score_word(self.SBoard, (row, start), (row, end), letters)

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

                self.current_player()._score_word(self.SBoard, (start_v, col), (end_v, col), letters)

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


def test():
    scrabble = Scrabble(True, players=Player(Bag()), num_players=2)

    scrabble._print_board()


if __name__ == '__main__':
    test()

