import pygame

from scoringSystem import *


class tileCheck:
    def __init__(self, letter):
        '''
        All letters are uppercase unless it is lowercase, in which case, it is a
        blank tile.
        '''
        self.isblank = letter.islower()
        self.letter = letter.upper()
        self.value = POINTS(letter)

        if self.isblank:
            self.value = 0

    def draw(self, scrn, position, resourceManagement):
        '''
        '''
        #scrn.blit(resourceManagement.board_tiles[self.letter], position)


class Bonus:
    def __init__(self, b):
        self.b = b

    def draw(self, scrn, position, resourceManagement):
        '''
        '''
        scrn.blit(resourceManagement.board_tiles[self.b], position)

# The rest is code where you implement your game using the Scenes model
def tile_to_pixel(x, y):
    """
    Takes an x, y coordinate of the board and translates into the
    corresponding pixel coordinate.

    Note: 0, 0 is top left of board.
    """
    pixel_x = 1 + 50*x
    pixel_y = 1 + 50*y
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
    def __init__(self, letter, spritesheet, location):
        pygame.sprite.Sprite.__init__(self)
        self.tileBlock = spritesheet.image_at(LETTER_COORDINATES[letter])
        self.letter = letter
        self.board_x = None
        self.board_y = None
        self.rect = self.tileBlock.get_rect()
        self.rect.left, self.rect.top = location
        self.tray_position = location
        self.on_board = False  # changed to true and printed a bunch of stuff
        self.m = []
        self.is_blank = (letter == ' ')
        self.UsedLetters = []
        self.submitted = False

    def move(self, pos):
        tile_x, tile_y = pixel_to_tile(*pos)
        if 0 <= tile_x < 15 and 0 <= tile_y < 15:  # working but self.board_x etc just not updating
            self.on_board = True
            self.board_x = tile_x
            self.board_y = tile_y
            self.rect.topleft = tile_to_pixel(tile_x, tile_y)
        else:
            self.on_board = False
            self.rect.topleft = self.tray_position

    def tile(self):
        """Returns the tuple (board_x, board_y, letter)."""
        return self.board_x, self.board_y, self.letter

    def rerack(self):
        """Moves the tile back to the rack."""
        self.on_board = False
        self.rect.topleft = self.tray_position

