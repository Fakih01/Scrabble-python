import sys
from LettersSpritesheet import SpriteSheet
from board import ScrabbleBoard as SB
import deck
import pygame
from scoringSystem import *
from scrabble import Scrabble
import twl


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
        self.UsedLetters = []
        #self.SBoardInstance = SBoardInstance
        #self.bTiles = SBoardInstance.SBoard
        self.submitted = False

    def add_move(self, x, y, letter, pos):
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
        self.UsedLetters.append(letter)
        word = ''.join(self.UsedLetters)
        #self.bTiles[x][y] = letter
        print("The letters you have used are", word)
        # board.ScrabbleBoard.get_tile_pos(self,position)
        #print("after add move", self.board_y, self.board_x, letter, self.on_board)
        #print(self.bTiles)

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
            raise Exception("not on board")

    def tile(self):
        """Returns the tuple (board_x, board_y, letter)."""
        print(f"printing from tile function: board_x={self.board_x}, board_y={self.board_y}, letter={self.letter}")
        return self.board_x, self.board_y, self.letter

    def rerack(self):
        """Moves the tile back to the rack."""
        self.on_board = False
        self.rect.topleft = self.tray_position
        print(self.letter, "back to rack")


class Player:
    def __init__(self, player_id, scrabble_instance, letter_tiles):
        self.player_id = player_id
        self.scrabble = scrabble_instance
        self.letterTiles = letter_tiles
        self.player_tiles = []
        self.game_tiles = []


class ComputerPlayer:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement, ai=False):
        self.rackList = []
        self.scrabble = Scrabble(True)
        self.ai = ai
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.letterTiles = SpriteSheet('resources/images/LetterSprite.png')
        self.deck = deck.Deck()
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []
        # Initialize two players
        self.players = {}
        self.players[1] = Player(1, Scrabble(True), self.letterTiles)
        self.players[2] = Player(2, Scrabble(True), self.letterTiles)
        self.currentPlayer = 1

        # Update the initial tiles for both players
        for player_id, player in self.players.items():
            for i, letter in enumerate(player.scrabble.get_rack()):
                player.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

        self.currentMove = Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i])

    def drawHand(self, scrn):
        '''
        Draws player's hand
        '''
        currentPlayer = self.players[self.currentPlayer]
        for tile in currentPlayer.player_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

        for tile in self.game_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

    def update_player_tiles(self):
        self.player_tiles = []
        for i, letter in enumerate(self.scrabble.get_rack()):
            self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

    def handle_event(self, evt):
        currentPlayer = self.players[self.currentPlayer]
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
                for tile in currentPlayer.player_tiles:
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
            elif evt.key == pygame.K_p:
                self.scrabble._print_board()
            elif evt.key == pygame.K_e:
                old_tiles = self.scrabble._player_rack
                self.scrabble.exchange_tiles(old_tiles)
                self.update_player_tiles()  # Update player tiles after the exchange
                print("Your new exchanged tiles are: ", self.scrabble._player_rack)

    # Add a method to render the score
    def render_score(self, scrn):
        player_score = self.players[1].scrabble.get_total_score()
        computer_score = self.players[2].scrabble.get_total_score()
        player_score_text = f"Player Score: {player_score}"
        computer_score_text = f"Computer Score: {computer_score}"
        font = pygame.font.Font('freesansbold.ttf', 15)
        player_score_surface = font.render(player_score_text, True, (255, 255, 255))
        computer_score_surface = font.render(computer_score_text, True, (255, 255, 255))
        scrn.blit(player_score_surface, (800, 80))
        scrn.blit(computer_score_surface, (800, 100))

    def render_turn(self, scrn):
        """Renders the text displaying the current player's turn."""
        turn_text = f"Player {self.currentPlayer}'s Turn!"
        font = pygame.font.Font('freesansbold.ttf', 23)
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        scrn.blit(turn_surface, (770, 20))

    def draw(self, scrn):
        self.board.draw(scrn, self.currentMove)
        self.render_score(scrn)
        self.render_turn(scrn)
        self.drawHand(scrn)

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

    def _hits_tile(self, pos, ignore=None):
        """Returns true if the position hits a tile."""
        for tile in self.player_tiles + self.game_tiles:
            if tile == ignore:
                continue
            if tile.rect.collidepoint(pos):
                print("tilehit")
                return True
        return False

    def generate_computer_move(self):
        # You can use your own AI algorithm here to generate the best move for the computer.
        # For simplicity, we'll just use the first available tile and place it on a random position on the board.

        import random

        currentPlayer = self.players[self.currentPlayer]
        available_letters = currentPlayer.scrabble.get_rack()
        letter_to_play = available_letters[0]

        random_row = random.randint(0, 14)
        random_col = random.randint(0, 14)

        return [(random_row, random_col, letter_to_play)]

    def _submit_turn(self):
        """
        Submits the turn to the scrabble backend. Moves the player tiles to
        game tiles and updates the player tiles.
        """
        print("move submitted")  # player.submit_move(self, self.board)  # currently broken
        print(f"Submitting move with move_count = {self.scrabble.moveCount}")
        #  print("Your word is", self.player_tiles)  # word isn't rly printing rn
        currentPlayer = self.players[self.currentPlayer]
        # Get a list of tiles that will be submitted
        # Check if the current player is the computer player (Player 2)
        if self.currentPlayer == 2 and self.ai:
            # Get the computer's move and update the board
            tileList = self.generate_computer_move()
            # Update the player_tiles to reflect the computer's move
            for tile in tileList:
                currentPlayer.player_tiles.remove(tile)
                self.game_tiles.append(tile)
        else:
            tileList = []
            for tile in currentPlayer.player_tiles:
                if tile.on_board:
                    tileList.append(tile.tile())

            # Not a turn if there's no tiles on board
            if len(tileList) == 0:
                return
            if currentPlayer.scrabble.submit_turn(tileList):
                # Valid turn, move all played tiles to game.
                self.scrabble.moveCount += 1
                print("Move count=",self.scrabble.moveCount)
                for tile in currentPlayer.player_tiles:
                    if tile.on_board:
                        self.game_tiles.append(tile)

                # Update the player tiles
                currentPlayer.player_tiles = []
                for i, letter in enumerate(currentPlayer.scrabble.get_rack()):
                    currentPlayer.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

                # Switch to the other player
                self.currentPlayer = 3 - self.currentPlayer
                print("Player", self.currentPlayer, "'s turn!")
            else:
                # Invalid turn, return all tiles to rack
                for tile in currentPlayer.player_tiles:
                    tile.rerack()
