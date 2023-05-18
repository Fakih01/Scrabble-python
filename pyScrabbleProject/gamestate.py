import sys
from random import shuffle

from LettersSpritesheet import SpriteSheet
import resourceFile
from board import ScrabbleBoard as SB
import pygame

from pyScrabbleProject.player import Player
from scoringSystem import *
from scrabble import *


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
            self.board_x = tile_x  # now is updating
            self.board_y = tile_y  # same
            self.rect.topleft = tile_to_pixel(tile_x, tile_y)
            print("tile status= ", self.on_board)
        else:
            self.on_board = False
            self.rect.topleft = self.tray_position
            print("tile status =", self.on_board)
            #raise Exception("not on board")

    def tile(self):
        """Returns the tuple (board_x, board_y, letter)."""
        print(f"printing from tile function: board_x={self.board_x}, board_y={self.board_y}, letter={self.letter}")
        return self.board_x, self.board_y, self.letter

    def rerack(self):
        """Moves the tile back to the rack."""
        self.on_board = False
        self.rect.topleft = self.tray_position
        print(self.letter, "back to rack")


class GameState:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement):
        self.bag = Bag()
        self.player = Player(self.bag)
        self.scrabble = Scrabble(True, self.player, 1)
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.letterTiles = SpriteSheet('resources/images/LetterSprite.png')
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []

        for i, letter in enumerate(self.player.get_rack()):
            self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))  # section not fully working


        self.currentMove = Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i])

    def drawHand(self, scrn):
        '''
        Draws player's hand
        '''
        for tile in self.player_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

        for tile in self.game_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

    def pass_rack(self):
        return

    def update_player_tiles(self):
        self.player_tiles = []
        for i, letter in enumerate(self.player.get_rack()):
            self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

    def handle_event(self, evt):
        if evt.type == pygame.MOUSEBUTTONUP:
            position = list(pygame.mouse.get_pos())
            if position in self.board:
                ind = self.board.get_tile_pos(position)
                if evt.button == 1:
                    if self.selectedTile:
                        if self._hits_tile(evt.pos, self.selectedTile):
                            self.selectedTile.rerack()
                        else:
                            self.selectedTile.move(evt.pos)

                        # Not selected anymore
                        self.selectedTile = None
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 1:
                for tile in self.player_tiles:
                    if tile.rect.collidepoint(evt.pos):
                        self.selectedTile = tile
                        mouse_x, mouse_y = evt.pos
                        self.offset_x = tile.rect.left - mouse_x
                        self.offset_y = tile.rect.top - mouse_y
        elif evt.type == pygame.MOUSEMOTION:
            if self.selectedTile:
                mouse_x, mouse_y = evt.pos
                self.selectedTile.rect.left = mouse_x + self.offset_x
                self.selectedTile.rect.top = mouse_y + self.offset_y

        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evt.key == pygame.K_RETURN:
                self._submit_turn()
            elif evt.key == pygame.K_1:
                self.scrabble._print_board()
            elif evt.key == pygame.K_TAB:
                old_tiles = self.player._player_rack
                self.player.exchange_tiles(old_tiles)
                self.update_player_tiles()  # Update player tiles after the exchange
                print("Your new exchanged tiles are: ", self.player._player_rack)
            elif evt.key == pygame.K_SPACE:
                if self.selectedTile:
                    self.selectedTile.rerack()
                    self.selectedTile = None
            # Add the following lines to handle when a blank tile is selected and a letter key is pressed
            elif self.selectedTile and self.selectedTile.is_blank and evt.unicode.isalpha():
                letter = evt.unicode.lower()
                self.selectedTile.letter = letter
                self.selectedTile.tileBlock = self.letterTiles.image_at(LETTER_COORDINATES[letter])
                blank_index = self.player_tiles.index(self.selectedTile)
                self.player._player_rack[blank_index] = letter

    # Add a method to render the score
    def render_score(self, scrn):
        score = self.player.get_total_score()
        score_text = f"Score: {score}"
        font = pygame.font.Font('freesansbold.ttf', 32)
        score_surface = font.render(score_text, True, (255, 255, 255))
        scrn.blit(score_surface, (800, 50))

    def draw(self, scrn):
        self.board.draw(scrn, self.currentMove)
        self.render_score(scrn)
        self.drawHand(scrn)

    def update(self, delta):
        '''
        Updates the state as a whole.
        '''
        pass

    def _hits_tile(self, pos, ignore=None):
        """Returns true if the position hits a tile."""
        for tile in self.player_tiles + self.game_tiles:
            if tile == ignore:
                continue
            if tile.rect.collidepoint(pos):
                print("tilehit")
                return True
        return False

    def is_game_over(self):
        return len(self.bag._bag) == 0 and len(self.player.get_rack()) == 0

    def _submit_turn(self):
        """
        Submits the turn to the scrabble backend. Moves the player tiles to
        game tiles and updates the player tiles.
        """
        print("move submitted")  # player.submit_move(self, self.board)  # currently broken
        #  print("Your word is", self.player_tiles)  # word isn't rly printing rn

        # Get a list of tiles that will be submitted
        tileList = []
        for tile in self.player_tiles:
            if tile.on_board:
                tileList.append(tile.tile())

        # Not a turn if there's no tiles on board
        if len(tileList) == 0:
            return

        if self.scrabble.submit_turn(tileList):
            self.player.num_remaining_tiles()

            self.scrabble.moveCount = + 1
            # Valid turn, move all played tiles to game.
            for tile in self.player_tiles:
                if tile.on_board:
                    self.game_tiles.append(tile)

            # Update the player tiles
            self.player_tiles = []
            for i, letter in enumerate(self.player.get_rack()):
                self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

        else:
            # Invalid turn, return all tiles to rack
            for tile in self.player_tiles:
                tile.rerack()

        if self.is_game_over():
            # You need to decide what should happen when the game is over.
            print("Game Over!")
            print(f"Final score: {self.player.get_total_score()}")
            pygame.quit()
            sys.exit()
