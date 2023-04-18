import sys

import scrabble
import resourceFile
from board import ScrabbleBoard as SB
import player
import deck
import pygame

import scrabble
from scrabble import Scrabble


class Tile:
    def __init__(self, letter, SBoardInstance):
        self.letter = letter
        self.board_x = None
        self.board_y = None
        self.on_board = True  # changed to true and printed a bunch of stuff
        self.m = []
        self.UsedLetters = []
        self.SBoardInstance = SBoardInstance
        self.bTiles = SBoardInstance.SBoard
        self.submitted = False

    def add_move(self, x, y, letter):
        print("add move is called in move class originating from gs class")  # works
        # Appends word onto move array and checks for letters that are in the same position.

        for i, j, l in self.m:
            if i == x and j == y:
                print("error: attempt to place letter in same position")
                raise Exception("error: attempt to place letter in same position")

        self.m.append((x, y, letter))
        print(f"Tile '{letter}' placed at ({x}, {y})")
        #  print(self.m)
        #  print(self.worddd)

        if 0 <= x < 15 and 0 <= y < 15:  # working but self.board_x etc just not updating
            self.on_board = True
            self.board_x = x  # now is updating
            self.board_y = y  # same
            print("tile status= ", self.on_board)
            self.UsedLetters.append(letter)
            word = ''.join(self.UsedLetters)
            self.bTiles[x][y] = letter
            print("The letters you have used are", word)
            # board.ScrabbleBoard.get_tile_pos(self,position)
            print("after add move", self.board_y, self.board_x, letter, self.on_board)
            print(self.bTiles)
        else:
            self.on_board = False
            print("tile status =", self.on_board)
            raise Exception("not on board")

        return self.board_x, self.board_y, letter, self.on_board

    def remove_move(self, x, y):  # Returns the removed letter

        rem = None
        for i, j, l in self.m:
            if i == x and j == y:
                # A match!
                rem = (i, j, l)

        if rem is None:
            raise Exception("error: letter doesn't exist and cannot be removed")

        self.m.remove(rem)
        self.on_board = False
        return rem[2]

    def tileTest(self):
        """Returns the tuple (board_x, board_y, letter)."""
        print(f"printing from TileTest: board_x={self.board_x}, board_y={self.board_y}, letter={self.letter}")
        return self.board_x, self.board_y, self.letter

    def rerackTest(self):
        """Moves the tile back to the rack."""
        self.on_board = False
        print("back to rack")


class GameState:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement, ai=False):
        self.rackList = []
        self.scrabble = Scrabble(True)
        self.ai = ai
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.p1 = player.Player((0, 750), self.scrabble)
        self.p2 = player.Player((0, 750), self.scrabble)
        self.deck = deck.Deck()
        self.turn = "1"             # Player 1 always goes first
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []

        for i, letter in enumerate(self.scrabble.get_rack()):
            tilee = Tile(letter, self.scrabble)
            self.player_tiles.append(tilee)  # section not fully working
            #clean up print("for i loop rack =", [self.rackList])

        # Place players into dictionary for less if-statements
        self.gs = {"1": self.p1, "2": self.p2}

        # First, draw 7 tiles
        self.p1.deck_draw(self.deck, 7)
        #self.p2.deck_draw(self.deck, 7)

        self.currentMove = Tile(letter, self.scrabble)

    def handle(self, evt):
        '''
        Handles all events passed into the state.
        '''
        if evt.type == pygame.MOUSEBUTTONUP:
            position = list(pygame.mouse.get_pos())
            if position in self.board:
                if self.selectedTile is None:
                    # Removes selected tile from board, and thus, from moveset
                    self.handle_board_removal(position)
                else:
                    # Places selected tile into moveset, and thus, places tile
                    # onto board
                    self.handle_board_place(position)

            elif position in self.gs[self.turn]:
                if self.selectedTile is None:
                    # Select tile, and remove from correct hand
                    self.handle_hand_select(position)
                else:
                    # Replaces removed tile from hand
                    self.handle_hand_replace(position)
        if evt.type == pygame.KEYDOWN:  # right place?
            if evt.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evt.key == pygame.K_RETURN:  # move is submitted here
                self._submit_turn()

            elif evt.key == pygame.K_p:  #prints board when p is pressed
                self.scrabble._print_board()

    def handle_board_removal(self, position):
        '''
        Handles the removal of tile. If the tile isn't in the current moveset,
        don't remove anything. Because that is cheating.'''
        ind = self.board.get_tile_pos(position)

        try:
            l = self.gs[self.turn].currentMove.remove_move(*ind)
            self.selectedTile = l
        except:
            return

    def handle_board_place(self, position):
        '''
        Handles the placing of the selected tile onto the board. Assumes that
        there is already a selected tile.
        '''
        ind = self.board.get_tile_pos(position)
        #print("board tiles" ,self.board.board_tiles)

        if self.board.board_tiles[ind[0]][ind[1]] is None:
            try:
                # Stops people from trying to place tiles on a non-empty tile
                # that is in move set (it throws a nasty little error when it
                # does).
                self.gs[self.turn].currentMove.add_move(ind[0], ind[1], self.selectedTile)
                self.selectedTile = None
            except:
                self.gs[self.turn].scrabble._player_rack.append(self.selectedTile)  # add selected tile back to rack
                self.selectedTile = None
            '''Works because the print statement is called and add move is functioning meaning the tiles are appended
            to the board_tiles list 
            so nxt step should involve the reading of these tiles before validating them'''

    def handle_hand_replace(self, position):
        '''
        Handles the replacing of selected tile into hand.
        '''
        # Gets the tile index, if any
        ind = self.gs[self.turn].get_tile_pos(position)

        # Places tile into hand
        if ind == -1:
            self.gs[self.turn].scrabble._player_rack.append(self.selectedTile)
        else:
            self.gs[self.turn].scrabble._player_rack.insert(ind, self.selectedTile)

        # Removes selected tile
        self.selectedTile = None

    def handle_hand_select(self, position):
        '''
        Handles the tile selection and removal (from the corresponding hand, of
        course).
        '''
        # Grab tile from hand and place into tile selection
        try:
            self.selectedTile = self.gs[self.turn].get_tile(position)
        except:
            return

        # Removes tile from hand
        #self.gs[self.turn].scrabble._player_rack.remove(self.selectedTile)  # updates list by removing(surely counts as currentmove?)
        print(self.gs[self.turn].scrabble._player_rack)

    def draw(self, scrn):
        '''
        Draws the state onto the screen scrn.
        '''
        self.board.draw(scrn, self.gs[self.turn].currentMove)
        player_position = (0, 750)
        if self.turn == "1":
            self.p1.drawHand(scrn, self.resourceManagement, player_position)
        else:
            self.p2.drawHand(scrn, self.resourceManagement, player_position)

        if self.selectedTile is not None:
            # Tile is selected and should hang onto the mouse
            x, y = pygame.mouse.get_pos()
            scrn.blit(self.resourceManagement.board_tiles[self.selectedTile],
                      (x - resourceFile.Tile_Size[0] / 2,
                       y - resourceFile.Tile_Size[1] / 2))

    def return_tiles_to_rack(self):
        for x, y, letter in self.gs[self.turn].currentMove.m:
            self.gs[self.turn].scrabble._player_rack.append(letter)
            self.board.board_tiles[x][y] = None
        self.gs[self.turn].currentMove.m.clear()

    def update(self, delta):
        '''
        Updates the state as a whole.
        '''
        pass

    def _submit_turn(self):
        """
        Submits the turn to the scrabble backend. Moves the player tiles to
        game tiles and updates the player tiles.
        """
        print("move submitted")  # player.submit_move(self, self.board)  # currently broken
        #  print("Your word is", self.player_tiles)  # word isn't rly printing rn

        # Get a list of tiles that will be submitted
        tileList = []
        for x, y, letter in self.gs[self.turn].currentMove.m:  # Use currentMove.m to get the updated coordinates
            tile_info = (x, y, letter)
            print("Tile info:", tile_info)
            tileList.append(tile_info)
        print("tileList is still", tileList)

        # Not a turn if there's no tiles on board
        if len(tileList) == 0:
            return

        if self.scrabble.submit_turn(tileList):
            for x, y, letter in tileList:
                if letter in self.gs[self.turn].scrabble._player_rack:
                    self.gs[self.turn].scrabble._player_rack.remove(letter)
            # Valid turn, move all played tiles to game.
            for tileTest in self.player_tiles:
                if tileTest.on_board:
                    self.game_tiles.append(tileTest)
                    tileTest.submitted = True

            # Update the player tiles
            self.player_tiles = []
            for i, letter in enumerate(self.gs[self.turn].get_the_rack()):
                self.player_tiles.append(Tile(letter, self.scrabble))  # self.resourceManagement.board_tiles[self.rackList[i]])

            #word = [tile.letter for tile in self.game_tiles]
            #print("printing self.game tiles", self.game_tiles)
            #print("Your word is:", ''.join(word))  # prints tile rack rather than submitted tiles because all r set to true in move class
        else:
            # Invalid turn, return all tiles to rack
            for tileTest in self.player_tiles:
                self.return_tiles_to_rack()