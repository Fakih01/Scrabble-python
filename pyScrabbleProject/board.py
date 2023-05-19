import pygame
import colours
from scrabble import *
import tileModule
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
        self.moveCount = 0
        self.position = position  # Stores the position of the scrabble board
        self.bag = Bag()
        self.player = Player(self.bag)
        self.scrabble = Scrabble(True, self.player, 2)
        self.board_tiles = self.scrabble.SBoard  # 2d array of size 15x15 to store tiles currently on the board
        self.resourceManagement = resourceManagement  # The resource manager
        self.boardSize = (15 * resourceFile.Tile_Size[0],
                     15 * resourceFile.Tile_Size[1])  # size of the scrabble board
        self.boardRect = pygame.Rect(self.position, self.boardSize)  # rectangle representing the scrabble board
        self.clean = True  # flag to indicate if the board is clean or not


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


    def update(self, delta):
        '''
        Updates the scrabble board.
        '''
        pass
