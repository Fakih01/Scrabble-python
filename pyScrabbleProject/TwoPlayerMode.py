import sys

from LettersSpritesheet import SpriteSheet
import resourceFile
from board import ScrabbleBoard as SB
import pygame
from scoringSystem import *
from scrabble import *
from player import *
from singleplayer import *
from tileModule import *


class TwoPlayerGame:  # Loads everything necessary and starts the game.
    def __init__(self, resourceManagement):
        self.bag = Bag()
        self.players = {1: Player(self.bag), 2: Player(self.bag)}
        self.Player_skip = 0
        self.players_skip = {1: 0, 2: 0}
        self.player_exchange = 0
        self.scrabble = Scrabble(True, self.players, 2)
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.letterTiles = SpriteSheet('resources/images/LetterSprite.png')
        self.selectedTile = None    # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []
        self.running_score = 0
        # Initialize two players
        self.currentPlayer = self.players[1]
        self.currentPlayerKey = 1
        self.player_scores = {1: 0, 2: 0}
        self.screen = pygame.display.set_mode((1000, 800))
        self.instructions = [
            'Instructions:',
            '1. Drag and drop tiles to the board',
            '2. Press Enter to submit turn',
            '3. Press Tab to exchange tiles',
            '4. Press Space to rerack selected tile',
            '5. When a blank tile is selected,',
            'press any letter key to alter it',
            '6.Press LCTRL to skip your turn',
            '7. Press Esc to quit game'
        ]


        # Update the initial tiles for both players
        for i, letter in enumerate(self.currentPlayer.get_rack()):
            self.player_tiles.append(
                Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))  # section not fully working

        self.currentMove = Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i])

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
        for i, letter in enumerate(self.currentPlayer.get_rack()):
            self.player_tiles.append(Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

    def update_player_score(self):
        score = self.currentPlayer.get_turn_score()
        self.player_scores[self.currentPlayerKey] += score
        return score

    def handle_event(self, evt):
        if evt.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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
                old_tiles = self.currentPlayer._player_rack
                self.currentPlayer.exchange_tiles(old_tiles)
                self.scrabble.players[self.currentPlayerKey].exchange_tiles(old_tiles)
                self.update_player_tiles()  # Update player tiles after the exchange
                print("Your new exchanged tiles are: ", self.currentPlayer._player_rack)
                self.player_exchange +=1
                self.scrabble.switch_turn()
                self.switch_turn()
                self.update_player_tiles()
            elif evt.key == pygame.K_SPACE:
                if self.selectedTile:
                    self.selectedTile.rerack()
                    self.selectedTile = None
            elif self.selectedTile and self.selectedTile.is_blank and evt.unicode.isalpha():
                letter = evt.unicode.lower()
                self.selectedTile.letter = letter
                self.selectedTile.tileBlock = self.letterTiles.image_at(LETTER_COORDINATES[letter])
                blank_index = self.player_tiles.index(self.selectedTile)
                self.currentPlayer._player_rack[blank_index] = letter
            elif evt.key == pygame.K_LCTRL:
                print("Skipped turn")
                self.players_skip[self.currentPlayerKey] += 1
                if self.players_skip[self.currentPlayerKey] == 2:
                    self.game_over()
                else:
                    self.switch_turn()

    # Add a method to render the score
    def render_score(self, scrn):
        p1_score = self.player_scores[1]
        p2_score = self.player_scores[2]
        p1_score_text = f"Player 1 Score: {p1_score}"
        p2_score_text = f"Player 2 Score: {p2_score}"
        font = pygame.font.Font('freesansbold.ttf', 18)
        p1_score_surface = font.render(p1_score_text, True, (255, 255, 255))
        p2_score_surface = font.render(p2_score_text, True, (255, 255, 255))
        scrn.blit(p1_score_surface, (800, 80))
        scrn.blit(p2_score_surface, (800, 400))

    def render_turn(self, scrn):
        """Renders the text displaying the current player's turn."""
        turn_text = f"Player {self.currentPlayerKey}'s Turn!"
        font = pygame.font.Font('freesansbold.ttf', 23)
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        scrn.blit(turn_surface, (770, 20))

    def render_instructions(self, scrn):
        font = pygame.font.Font('freesansbold.ttf', 11)  # Change the size as needed
        y_offset = 0  # This will be used to move each line down
        for instruction in self.instructions:
            instruction_surface = font.render(instruction, True, (255, 255, 255))
            scrn.blit(instruction_surface, (800, 500 + y_offset))  # Change the coordinates as needed
            y_offset += 30  # Change this value to adjust the space between line

    def draw(self, scrn):
        self.board.draw(scrn, self.currentMove)
        self.render_score(scrn)
        self.render_turn(scrn)
        self.drawHand(scrn)
        self.render_instructions(scrn)

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
        return len(self.bag._bag) == 0 and len(self.currentPlayer.get_rack()) == 0

    def game_over(self):
        print("Game Over!")
        self.running = False

        # Calculate the winner
        if self.players_skip[1] == 2:
            winner = "Player 2"
        elif self.players_skip[2] == 2:
            winner = "Player 1"
        elif self.player_scores[1] > self.player_scores[2]:
            winner = "Player 1"
        elif self.player_scores[1] < self.player_scores[2]:
            winner = "Player 2"
        else:
            winner = "It's a Tie"

        # Create a game over surface and position it in the middle of the screen
        font = pygame.font.Font('freesansbold.ttf', 64)
        font2 = pygame.font.Font('freesansbold.ttf', 44)
        game_over_surface = font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_surface.get_rect(center=(400, 200))
        winner_surface = font.render(winner + " Wins!", True, (255, 255, 255))
        winner_rect = winner_surface.get_rect(center=(500, 350))
        text_surface = font2.render("Press 'ESC' to close screen", True, (255, 255, 255))
        text_surface_rect = text_surface.get_rect(center=(500, 500))

        while not self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

            # Draw the game over surface
            self.screen.fill((0, 0, 0))
            self.screen.blit(game_over_surface, game_over_rect)
            self.screen.blit(winner_surface, winner_rect)
            self.screen.blit(text_surface, text_surface_rect)
            pygame.display.flip()

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
            self.currentPlayer.num_remaining_tiles()
            self.players_skip[self.currentPlayerKey] = 0
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
            self.switch_turn()
            self.update_player_tiles()

        else:
            # Invalid turn, return all tiles to rack
            for tile in self.player_tiles:
                tile.rerack()

        if self.is_game_over():
            # You need to decide what should happen when the game is over.
            print("Game Over!")
            print(f"Final score: {self.currentPlayer.get_total_score()}")
            pygame.quit()
            sys.exit()

    def switch_turn(self):
        self.currentPlayerKey = 3 - self.currentPlayerKey
        self.currentPlayer = self.players[self.currentPlayerKey]
        if self.currentPlayerKey == 1:
            print("Player", self.currentPlayerKey, "'s turn!")

        else:
            self.currentPlayer = self.players[self.currentPlayerKey]
            print("Player", self.currentPlayerKey, "'s turn!")

