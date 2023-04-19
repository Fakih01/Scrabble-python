import sys

import scrabble
import resourceFile
from board import ScrabbleBoard as SB
import player
import deck
import pygame
from scoringSystem import *

import scrabble
from scrabble import Scrabble


# The rest is code where you implement your game using the Scenes model
def tile_to_pixel(x, y):
    """
    Takes an x, y coordinate of the board and translates into the
    corresponding pixel coordinate.

    Note: 0, 0 is top left of board.
    """
    pixel_x = 2 + 50*x
    pixel_y = 2 + 50*y
    return pixel_x, pixel_y


def pixel_to_tile(x, y):
    """
    Takes an x, y coordinate of the cursor and translates into the
    corresponding tile coordinate.
    """
    tile_x = (x - 2)//50
    tile_y = (y - 2)//50
    return tile_x, tile_y


class Tile(pygame.sprite.Sprite):
    def __init__(self, letter, SBoardInstance, spritesheet, location):
        pygame.sprite.Sprite.__init__(self)
        self.tileBlock = spritesheet.imageFrom(LETTER_COORDINATES[letter])
        self.letter = letter
        self.board_x = None
        self.board_y = None
        self.rect = self.tileBlock.get_rect()
        self.rect.left, self.rect.top = location
        self.tray_position = location
        self.on_board = False  # changed to true and printed a bunch of stuff
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
            #print("after add move", self.board_y, self.board_x, letter, self.on_board)
            #print(self.bTiles)
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

    def tile(self):
        """Returns the tuple (board_x, board_y, letter)."""
        print(f"printing from tile function: board_x={self.board_x}, board_y={self.board_y}, letter={self.letter}")
        return self.board_x, self.board_y, self.letter

    def rerack(self):
        """Moves the tile back to the rack."""
        self.on_board = False
        print("back to rack")
        raise Exception("Rerack needed")


class Player:
    '''
    A representation of the player, complete with current score and hand.
    Should only draw the player's own hand, and not the current move.
    '''

    def __init__(self, position, scrabbleInstance):
        '''
        initialises score and hand.
        hand should only have characters (max size 7).
        '''
        self.scrabbleInstance = scrabbleInstance
        self.scrabble = scrabbleInstance
        self.position = position
        self.currentMove = Tile(letter=True, SBoardInstance=self.scrabble)
        self.size = (7 * resourceFile.Tile_Size[0],
                     resourceFile.Tile_Size[1])
        self.rect = pygame.Rect(self.position, self.size)
        rack = self.scrabble._player_rack
        self.rackList = list(rack)

    def __contains__(self, position):
        '''
        Returns true if point is inside player hand rectangle, and false if
        otherwise.
        Uses pygame Rect.collidepoint method to compact code.
        '''
        return self.rect.collidepoint(position)

    def get_tile_pos(self, position):
        '''
        Returns the index of the tile, if it exists at position pos.
        Otherwise, return -1. Assumes that the position is already in the player
        hand.
        '''
        # Normalize the position
        position[0] -= self.position[0]

        ind = position[0] // resourceFile.Tile_Size[0]
        if ind < len(self.scrabble._player_rack):
            print("this is in position", ind)  # positioning of tile from hand
            return ind

        else:
            return -1

    def get_tile(self, position):
        '''
        Returns a single character from the position from hand.
        If the character doesn't exist, raises an exception.
        '''
        ind = self.get_tile_pos(position)

        if ind == -1:
            raise Exception("error: that isn't a tile")

        t = self.scrabble._player_rack[ind]
        print("this is the letter", t, "at position:", ind)
        return t

    def deck_draw(self, deck, n):
        '''
        Draws n tiles from deck   # might not be needed as have the function in scrabble.py
        '''
        print("deck_draw", self.scrabble._player_rack)
        #self.rackList.extend(deck.take(n))  #not acc drawing any tiles

    def get_the_rack(self):
        """
        Returns a copy of the player's rack
        """
        print("get_the_rack called", self.scrabble._player_rack)  # trying
        print("Now we need a new rack. fix it.")
        return self.scrabble._player_rack

    def deck_exchange(self, deck, l):
        '''
        Exchanges tiles in hand (list l) with random tiles in deck.
        First checks to see that the list is a subset of hand.
        '''
        if not all(map(lambda i: i in self.rackList, l)):
            raise Exception("error: cannot exchange non-existent board_tiles")

        deck.place(l)

        for i in l:
            self.rackList.remove(i)

    def drawHand(self, scrn, resourceManagement, position):
        '''
        Draws player's hand
        '''
        for i in range(len(self.scrabble._player_rack)):
            scrn.blit(resourceManagement.board_tiles[self.scrabble._player_rack[i]],
                      (position[0] + resourceFile.Tile_Size[0] * i,
                       position[1]))


class GameState:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement, ai=False):
        self.rackList = []
        self.scrabble = Scrabble(True)
        self.ai = ai
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.p1 = Player((0, 750), self.scrabble)
        #self.p2 = player.Player((0, 750), self.scrabble)
        self.deck = deck.Deck()
        #self.turn = "1"             # Player 1 always goes first
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []
        self.current_move = False

        for i, letter in enumerate(self.scrabble.get_rack()):
            tileObject = Tile(letter, self.scrabble)
            self.player_tiles.append(tileObject)  # section not fully working
            #clean up print("for i loop rack =", [self.rackList])

        # Place players into dictionary for less if-statements
        #self.gs = {"1": self.p1, "2": self.p2}

        # First, draw 7 tiles
        self.p1.deck_draw(self.deck, 7)
        #self.p2.deck_draw(self.deck, 7)

        self.currentMove = Tile(letter, self.scrabble)

    def handle_event(self, evt):
        if evt.type == pygame.MOUSEBUTTONUP:
            position = list(pygame.mouse.get_pos())
            if position in self.board:
                ind = self.board.get_tile_pos(position)
                if self.selectedTile is None:
                    # Handles the removal of tile
                    try:
                        l = self.currentMove.remove_move(*ind)
                        self.selectedTile = l
                    except:
                        return
                else:
                    # Handles the placing of the selected tile onto the board
                    if self.board.board_tiles[ind[0]][ind[1]] is None:
                        try:
                            self.currentMove.add_move(ind[0], ind[1], self.selectedTile)
                            self.selectedTile = None
                        except:
                            self.scrabble._player_rack.append(self.selectedTile)
                            self.selectedTile = None

            elif position in self.p1:
                ind = self.p1.get_tile_pos(position)
                if self.selectedTile is None:
                    # Handles the tile selection and removal
                    try:
                        self.selectedTile = self.p1.get_tile(position)
                        self.scrabble._player_rack.remove(self.selectedTile)
                    except:
                        return
                else:
                    # Handles the replacing of selected tile into hand
                    if ind == -1:
                        self.scrabble._player_rack.append(self.selectedTile)
                    else:
                        self.scrabble._player_rack.insert(ind, self.selectedTile)
                    self.selectedTile = None

        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evt.key == pygame.K_RETURN:
                self._submit_turn()
            elif evt.key == pygame.K_p:
                self.scrabble._print_board()

    def draw(self, scrn):
        self.board.draw(scrn, self.currentMove)
        playerRack_position = (0, 750)


        self.p1.drawHand(scrn, self.resourceManagement, playerRack_position)


        if self.selectedTile is not None:
            x, y = pygame.mouse.get_pos()
            scrn.blit(self.resourceManagement.board_tiles[self.selectedTile],
                      (x - resourceFile.Tile_Size[0] / 2,
                       y - resourceFile.Tile_Size[1] / 2))

    def return_tiles_to_rack(self):
        for x, y, letter in self.currentMove.m:
            self.scrabble._player_rack.append(letter)
            self.board.board_tiles[x][y] = None
        self.currentMove.m.clear()

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
        for x, y, letter in self.currentMove.m:  # Use currentMove.m to get the updated coordinates
            tile_info = (x, y, letter)
            print("Tile info:", tile_info)
            tileList.append(tile_info)
        print("tileList is still", tileList)

        # Not a turn if there's no tiles on board
        if len(tileList) == 0:
            return

        if self.scrabble.submit_turn(tileList):
            for x, y, letter in tileList:
                if letter in self.scrabble._player_rack:
                    self.scrabble._player_rack.remove(letter)
            # Valid turn, move all played tiles to game.
            for tileTest in self.player_tiles:
                if tileTest.on_board:
                    self.game_tiles.append(tileTest)
                    tileTest.submitted = True


            # Update the player tiles
            self.player_tiles = []
            for i, letter in enumerate(self.scrabble.get_rack()):
                self.player_tiles.append(Tile(letter, self.scrabble))  # self.resourceManagement.board_tiles[self.rackList[i]])

            # Clear the current move's tile list
            self.currentMove.m.clear()  # Add this line here

            #word = [tile.letter for tile in self.game_tiles]
            #print("printing self.game tiles", self.game_tiles)
            #print("Your word is:", ''.join(word))  # prints tile rack rather than submitted tiles because all r set to true in move class
        else:
            # Invalid turn, return all tiles to rack
            for tileTest in self.player_tiles:
                self.Tile.rerack()
