import random
import sys
import twl
from LettersSpritesheet import SpriteSheet
import resourceFile
from board import ScrabbleBoard as SB
import pygame
from scoringSystem import *
from scrabble import *
import itertools
import threading
from gamestate import *
from ScrabbleAI import *


class AIPlayer(Player):
    def __init__(self, AIscrabbleInstance):
        self.AIscrabbleInstance = AIscrabbleInstance
        super().__init__()

    def make_ai_move(self):
        self.AIscrabbleInstance.find_possible_words()
        tiles_to_submit_and_move = self.AIscrabbleInstance.make_best_move()
        return tiles_to_submit_and_move


AIScrabbleInstance = AIScrabble(debug=True, scrabbleInstance=Scrabble(True, 2), num_players=2)
ai_player = AIPlayer(AIScrabbleInstance)


class ComputerGame:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement, ai=False):
        self.player = player
        self.scrabble = Scrabble(True, 2)
        self.scrabble_ai = AIScrabble(True, self.scrabble, 1)
        self.ai = ai
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.letterTiles = SpriteSheet('resources/images/LetterSprite.png')
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []
        self.running_score = 0
        # Initialize two players
        self.players = {1: Player(), 2: AIPlayer(self.scrabble_ai)}
        self.currentPlayer = self.players[1]
        self.currentPlayerKey = 1
        self.player_scores = {1: 0, 2: 0}

        # Update the initial tiles for both players
        for i, letter in enumerate(self.player.get_rack()):
            self.player_tiles.append(
                Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))  # section not fully working

        self.currentMove = Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i])

    def computer_move(self):
        print("Computer move.")
        move_tiles = self.players[2].make_ai_move()
        # Iterate through the tiles to move
        for (row, col, letter) in move_tiles:
            # Search for the tile with the corresponding letter in the player's rack
            for tile in self.player_tiles:
                if tile.letter == letter and not tile.on_board:
                    # Move the tile to the correct position on the board
                    tile.board_x = row
                    tile.board_y = col
                    tile.on_board = True
                    tile.rect.topleft = tile_to_pixel(row, col)
                    break

    def drawHand(self, scrn):
        '''
        Draws player's hand
        '''
        for tile in self.player_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

        for tile in self.game_tiles:
            scrn.blit(tile.tileBlock, tile.rect)

    def update_player_tiles(self):
        self.player_tiles = []
        for i, letter in enumerate(self.player.get_rack()):
            self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

    def update_player_score(self):
        score = self.player.get_turn_score()
        self.player_scores[self.currentPlayerKey] += score
        return score

    def total_player_score(self):
        self.runni_score = 0

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
            elif evt.key == pygame.K_p:
                self.scrabble._print_board()
            elif evt.key == pygame.K_e:
                old_tiles = self.player._player_rack
                self.player.exchange_tiles(old_tiles)
                self.update_player_tiles()  # Update player tiles after the exchange
                print("Your new exchanged tiles are: ", self.player._player_rack)

    # Add a method to render the score
    def render_score(self, scrn):
        p1_score = self.player_scores[1]
        CP_score = self.player_scores[2]
        p1_score_text = f"Player 1 Score: {p1_score}"
        CP_score_text = f"CP Score: {CP_score}"
        font = pygame.font.Font('freesansbold.ttf', 15)
        p1_score_surface = font.render(p1_score_text, True, (255, 255, 255))
        CP_score_surface = font.render(CP_score_text, True, (255, 255, 255))
        scrn.blit(p1_score_surface, (800, 80))
        scrn.blit(CP_score_surface, (800, 100))

    def render_turn(self, scrn):
        """Renders the text displaying the current player's turn."""
        if self.currentPlayerKey ==1:
            turn_text = f"Player {self.currentPlayerKey}'s Turn!"
        else:
            turn_text = f" Computer's turn!"
        font = pygame.font.Font('freesansbold.ttf', 23)
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        scrn.blit(turn_surface, (770, 20))

    def draw(self, scrn):
        self.board.draw(scrn, self.currentMove)
        self.render_score(scrn)
        self.render_turn(scrn)
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

    def _submit_turn(self):
        """
        Submits the turn to the scrabble backend. Moves the player tiles to
        game tiles and updates the player tiles.
        """
        print("move submitted")  # player.submit_move(self, self.board)  # currently broken
        print(f"Submitting move with move_count = {self.scrabble.moveCount}")
        #  print("Your word is", self.player_tiles)  # word isn't rly printing rn
        currentPlayer = self.currentPlayer
        # Get a list of tiles that will be submitted
        tileList = []
        for tile in self.player_tiles:
            if tile.on_board:
                tileList.append(tile.tile())

        # Not a turn if there's no tiles on board
        if len(tileList) == 0:
            return
        if self.scrabble.submit_turn(tileList):
            # Valid turn, move all played tiles to game.
            for tile in self.player_tiles:
                if tile.on_board:
                    self.game_tiles.append(tile)

            # Update the player tiles
            currentPlayer.player_tiles = []
            currentPlayer.totalScore = 0
            for i, letter in enumerate(currentPlayer.get_rack()):
                currentPlayer.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))
            currentPlayer.totalScore += self.update_player_score()
            print("total player score for", f"Player {self.currentPlayerKey}", "is", currentPlayer.totalScore)

            self.update_player_tiles()

            # Switch to the other player
            self.switch_turn()

        else:
            # Invalid turn, return all tiles to rack
            for tile in self.player_tiles:
                tile.rerack()

    def computer_move_thread(self):
        self.computer_move()
        self.update_player_tiles()

    def switch_turn(self):
        self.currentPlayerKey = 3 - self.currentPlayerKey
        self.currentPlayer = self.players[self.currentPlayerKey]
        if self.currentPlayerKey == 1:
            print("Player", self.currentPlayerKey, "'s turn!")

        else:
            self.currentPlayer = self.players[self.currentPlayerKey]
            print("Computer's turn!")
            # Start the computer move in a separate thread
            computer_move_thread = threading.Thread(target=self.computer_move_thread)
            computer_move_thread.start()