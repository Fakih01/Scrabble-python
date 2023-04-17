import pygame
import colours
import player
import scrabble
import tile
import resourceFile
import scoringSystem as sS


class ScrabbleBoard:
    '''
    Scrabble board class that stores information about
    bonus system, board tiles, and whether or not a move
    is valid.
    '''
    def __init__(self, position, resourceManagement):  # a new object of the class is created.
        '''
        initialises positions, tiles, and bonuses. Tiles have tile items,
        whereas bonuses have surfaces as items.
        '''
        self._move_count = 0
        self.position = position  # Stores the position of the scrabble board
        self.scrabs = scrabble.Scrabble(debug=True)
        self.board_tiles = self.scrabs.SBoard  # 2d array of size 15x15 to store tiles currently on the board
        self.resourceManagement = resourceManagement  # The resource manager
        self.boardSize = (15 * resourceFile.Tile_Size[0],
                     15 * resourceFile.Tile_Size[1])  # size of the scrabble board
        self.boardRect = pygame.Rect(self.position, self.boardSize)  # rectangle representing the scrabble board
        self.clean = True  # flag to indicate if the board is clean or not
        #self.letter = letter


        # Initialises bonus system
        self.initialise_bonus_system("resources/board_data.txt")

    def __contains__(self, position):
        '''
        Returns true if point is inside Scrabble board, and false if otherwise.
        Uses pygame Rect.collidepoint method to compact code.
        '''
        return self.boardRect.collidepoint(position)

    def draw(self, scrn, ms):
        '''
        Draws the scrabble board along with all the tiles.
        If tile is none, draw bonus
        if not, draw tiles (draw tile first, then bonus)
        If there is an active moveset, draws it as well
        '''
        for x in range(len(self.board_tiles)):
            # Draw the tiles (bonus or bust)
            for y in range(len(self.board_tiles[x])):
                if self.board_tiles[x][y] is None:
                    # Draw the bonus if there is no tile
                    scrn.blit(self.resourceManagement.board_tiles[self.bonus[x][y]], (x * 50, y * 50))
                else:
                    # Draw the tile otherwise
                    scrn.blit(self.resourceManagement.board_tiles[self.board_tiles[x][y]], (x * 50, y * 50))

        for x, y, l in ms.m:
            scrn.blit(self.resourceManagement.board_tiles[l], (x * 50, y * 50))

        # Draw the lines between the tiles
        for i in range(15):
            pygame.draw.aaline(scrn,
                               colours.BLACK,
                               (0, i * 50),
                               (800, i * 50))
            pygame.draw.aaline(scrn,
                               colours.BLACK,
                               (i * 50, 0),
                               (i * 50, 800))

    def initialise_bonus_system(self, fn):
        '''
        initialises bonuses using the file.
        '''
        self.bonus = [[]]
        f = open(fn, 'r')
        for line in f.readlines():
            for sym in line.rstrip().split():
                self.bonus[-1].append(sym)
            self.bonus.append([])

        f.close()

    def _find_connected_words(self, m, ms):
        '''
        Finds all the words that are connected either horizontally or vertically
        to the single letter in move m (in a moveset, of course).

            (pos0, word, pos1)

        Where:
            pos0 - Starting point of the word
            word - The word itself
            pos1 - Ending point of the word

        Returns a list (max size 2) of words in the above format.
        '''
        x, y, l = m
        # Horizontal word
        hw_0, hw_w, hw_1 = (x, y), "", (x, y)
        # Go left
        for i in range(x, -1, -1):
            # First, try to get a tile
            item = None
            if self.board_tiles[i][y] is None:
                try:
                    item = ms.get_item(i, y)
                    hw_0 = (i, y)       # In edge cases
                except ValueError:
                    # If there are no more tiles left, get out
                    hw_0 = (i + 1, y)
                    break
            else:
                ms.is_chain = True
                item = (i, y, self.board_tiles[i][y])
                hw_0 = (i, y)           # In edge cases

            # Add letter to front of word
            hw_w = item[2] + hw_w

        # Go right
        for i in range(x + 1, 15):
            # First, try to get a tile
            item = None
            if self.board_tiles[i][y] is None:
                try:
                    item = ms.get_item(i, y)
                    hw_1 = (i, y)
                except ValueError:
                    hw_1 = (i - 1, y)
                    break
            else:
                ms.is_chain = True
                item = (i, y, self.board_tiles[i][y])
                hw_1 = (i, y)

            hw_w += item[2]

        # Vertical word
        vw_0, vw_w, vw_1 = None, "", None
        # Go up
        for j in range(y, -1, -1):
            # First, try to get a tile
            item = None
            if self.board_tiles[x][j] is None:
                try:
                    item = ms.get_item(x, j)
                    vw_0 = (x, j)
                except ValueError:
                    # If there are no more tiles left, get out
                    vw_0 = (x, j + 1)
                    break
            else:
                ms.is_chain = True
                item = (x, j, self.board_tiles[x][j])
                vw_0 = (x, j)

            # Add letter to front of word
            vw_w = item[2] + vw_w

        # Go right
        for j in range(y + 1, 15):
            # First, try to get a tile
            item = None
            if self.board_tiles[x][j] is None:
                try:
                    item = ms.get_item(x, j)
                    vw_1 = (x, j)
                except ValueError:
                    vw_1 = (x, j - 1)
                    break
            else:
                ms.is_chain = True
                item = (x, j, self.board_tiles[x][j])
                vw_1 = (x, j)

            vw_w += item[2]

        # Filter out all the single-letters, as they don't do anything (not
        # connected to anything, and is just there by itself).
        ret = []
        if len(hw_w) > 1:
            ret.append((hw_0, hw_w, hw_1))

        if len(vw_w) > 1:
            ret.append((vw_0, vw_w, vw_1))

        return ret

    def find_connected_words(self, ms):
        '''
        Finds all the words that are connected either horizontally or vertically
        to any of the letters in the moveset. To ensure that duplicates are
        eliminated, the list of words are returned as such:

            (pos0, word, pos1)

        Where:
            pos0 - Starting point of the word
            word - The word
            pos1 - Ending point of the word
        '''
        words = []
        for m in ms.m:
            words.extend(self._find_connected_words(m, ms))

        return list(set(words))

    def validate_moveset(self, ms, wl):
        '''
        Returns true if the moveset on the board contains valid scrabble words.
        Returns false otherwise.
        '''
        # TODO consider caching
        words = map(lambda item: item[1], self.find_connected_words(ms))
        print("all valid")
        return all(map(wl.isValid, words))

    def execute(self, ms):
        assert(ms.t == 'M')

        for x, y, l in ms.m:
            if self.board_tiles[x][y] is None:
                self.board_tiles[x][y] = l
            else:
                raise Exception('cannot place move - there is something here!')

    def get_word_score(self, ms, word):
        '''
        Returns the score of a particular word on the board, given all the
        bonuses gotten from moveset ms. Doesn't validate the moveset, though.
        '''
        word_bonus = 1
        score = 0
        if word[0][1] == word[2][1]:
            # Horizontal word (y is same)
            for x in range(word[0][0], word[2][0] + 1):
                # Tries to obtain the letter in moveset and check that there is
                # also a bonus tile of significant nature
                try:
                    i, j, l = ms.get_item(x, word[0][1])
                    # This tile is going to be placed on the board, so check if
                    # it exists in the bonus
                    letter_bonus = 1
                    if self.bonus[x][word[0][1]] in ['MD', 'DW']:
                        # Double word
                        word_bonus *= 2
                    elif self.bonus[x][word[0][1]] == 'DL':
                        # Double letter
                        letter_bonus = 2
                    elif self.bonus[x][word[0][1]] == 'TW':
                        # Triple word
                        word_bonus *= 3
                    elif self.bonus[x][word[0][1]] == 'TL':
                        # Triple letter
                        letter_bonus *= 3

                    score += sS.letterScore(word[1][x - word[0][0]]) * letter_bonus
                except:
                    # This tile is already on the board, so just count the score
                    score += sS.letterScore(word[1][x - word[0][0]])
        elif word[0][0] == word[2][0]:
            # Vertical word (x is same)
            for y in range(word[0][1], word[2][1] + 1):
                try:
                    i, j, l = ms.get_item(word[0][1], y)
                    # This tile is going to be placed on the board, so check if
                    # it exists in the bonus
                    letter_bonus = 1
                    if self.bonus[word[0][0]][y] in ['MD', 'DW']:
                        # Double word
                        word_bonus *= 2
                    elif self.bonus[word[0][0]][y] == 'DL':
                        # Double letter
                        letter_bonus = 2
                    elif self.bonus[word[0][0]][y] == 'TW':
                        # Triple word
                        word_bonus *= 3
                    elif self.bonus[word[0][0]][y] == 'TL':
                        # Triple letter
                        letter_bonus *= 3

                    score += sS.letterScore(word[1][y - word[0][1]]) * letter_bonus
                except:
                    # This tile is already on the board, so just count the score
                    score += sS.letterScore(word[1][y - word[0][1]])
        else:
            raise Exception('invalid word: neither horizontal nor vertical')

        if len(ms.m) == 7:
            return score * word_bonus + sS.BINGO_BONUS
        else:
            return score * word_bonus

    def get_score(self, ms):
        '''
        Returns the score of a particular moveset ms on the board, considering
        all the different bonuses it gets. Doesn't validate the moveset, though.
        '''
        words = self.find_connected_words(ms)
        return sum(map(lambda w: self.get_word_score(ms, w), words))

    def validate(self, ms, wl):
        '''
        Returns true if the moveset on the board is valid, and false if
        otherwise.
        '''
        if ms.t == "M":
            # It is a move
            # Moves are only valid if:
            #  - there exists at least 1 placed tile
            #  - placed tiles are in a line
            #  - placed tiles are adjacent to tiles (unless first move)
            #  - words that placed tiles make are valid with dictionary
            #  - if it is the first move, a tile must be on the center square
            return len(ms.m) > 0 and\
                   ms.validate(self.board_tiles) and\
                   self.validate_moveset(ms, wl)
        elif ms.t == "E":
            # It is an exchange
            # Exchanges are only valid if there are tiles placed on the board
            return len(ms.m) > 0
        elif ms.t == "P":
            # It is a pass
            # Passes are always valid
            return True
        else:
            # Throw an error for nothing that we've ever seen before
            raise Exception("error: invalid move type %s" % ms.t)

    def get_tile_pos(self, position):
        '''
        Returns the 2D indices for position pos. Since the board is of constant
        size, it is assumed that position pos is already inside board. It will
        always return a position, and won't error.
        '''
        # Normalize position
        position[0] -= self.position[0]
        position[1] -= self.position[1]

        # Calculate integer division
        return (position[0] // resourceFile.Tile_Size[0],
                position[1] // resourceFile.Tile_Size[1])

    def get_tile(self, position):
        '''
        Returns the character on the tile. If it is empty, returns None.
        '''
        ind = self.get_tile_pos(position)
        return self.board_tiles[ind[0]][ind[1]]

    def remove_tile(self, position):
        '''
        Replaces the character at position pos on the board with None value.
        If it is empty (None), it doesn't do a thing.
        '''
        ind = self.get_tile_pos(position)
        self.board_tiles[ind[0]][ind[1]] = None

    def place(self, position, letter):
        '''
        Converts letter to be placed into tile.Tile type.
        '''
        x, y = position
        if self.board_tiles[x][y] is not None:
            raise Exception("error: tile exists")

        self.board_tiles[x][y] = tile.tileCheck(letter)

    def take_back(self, position):
        '''
        Removes letter and returns it.
        '''
        x, y = position
        t = self.board_tiles[x][y]

        if t is None:
            raise Exception("error: tile doesn't exist")

        self.board_tiles[x][y] = None
        return t

    def submit_turn(self, ms, wl, position, word, letter):
        """
        Given a list of tiles (i, j, letter), check if valid, place on to board
        and add to player score.
        """
        if self.validate(ms, wl):
            self.get_word_score(ms, word)
            self.place(position, letter)
            #  self._update_player_rack(tiles)
            return True
        else:
            return False

    def handle(self, ms, wl, position, word, letter):  # use?
        '''
        Handles all events, like dragging of tiles and typing.
        '''
        print("In board class now")
        #  self.get_score()
        self.submit_turn(ms, wl, position, word, letter)

    def update(self, delta):
        '''
        Updates the scrabble board.
        '''
        pass
