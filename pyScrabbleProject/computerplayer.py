import random
import sys
import word_dictionary
from LettersSpritesheet import SpriteSheet
import resourceFile
from board import ScrabbleBoard as SB
import pygame
from scoringSystem import *
from scrabble import *
import itertools
import threading
from tileModule import *
from gamestate import *
from ScrabbleAI import *
from player import *


class AIPlayer(Player):
    def __init__(self, bag, AIscrabbleInstance):
        super().__init__(bag)
        self.AIscrabbleInstance = AIscrabbleInstance

    def make_ai_move(self):
        self.AIscrabbleInstance.find_possible_words(AIScrabble.min_score)
        tiles_to_move_and_submit = self.AIscrabbleInstance.make_random_move()
        print("Tiles to move and submit", tiles_to_move_and_submit)
        return tiles_to_move_and_submit


class ComputerGame:  # Loads everything necessary and starts the game.
    min_score = 0

    def __init__(self, resourceManagement):
        self.Player_help = 0
        self.player_exchange = 0
        self.player_skip = 0
        self.Computer_skips = 0
        self.Computer_exchanges = 0
        self.bag = Bag()
        self.resourceManagement = resourceManagement
        self.board = SB((0, 0), self.resourceManagement)
        self.letterTiles = SpriteSheet('resources/images/LetterSprite.png')
        self.selectedTile = None  # Selected tile should be a letter only
        self.player_tiles = []
        self.game_tiles = []
        self.running_score = 0
        self.instructions = [
            'Instructions:',
            '1. Drag and drop tiles to the board',
            '2. Press Enter to submit turn',
            '3. Press Tab to exchange tiles',
            '4. Press Space to rerack selected tile',
            '5. When a blank tile is selected,',
            'press any letter key to alter it',
            '6. Press Esc to quit game'
        ]
        # Initialize players
        self.players = {1: Player(self.bag), 2: None}  # We'll set player 2 (AI player) later
        self.player_scores = {1: 0, 2: 0}
        self.screen = pygame.display.set_mode((1000, 800))

        # Create scrabble instance
        self.scrabble = Scrabble(True, self.players, 2)
        self.ai_player = AIPlayer(self.bag, None)

        # Now that we have a scrabble instance, we can create an AIPlayer with AIScrabble
        self.scrabble_ai = AIScrabble(True, self.ai_player, self.scrabble)
        self.ai_player = AIPlayer(self.bag, self.scrabble_ai)
        self.players[2] = self.ai_player  # Now we set player 2 to be the AI player
        self.currentPlayer = self.players[1]
        self.currentPlayerKey = 1


        # Update the initial tiles for both players
        for i, letter in enumerate(self.currentPlayer.get_rack()):
            self.player_tiles.append(
                Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i]))

        self.currentMove = Tile(letter, self.letterTiles, PLAYER_TILE_POSITIONS[i])

    def computer_move(self):
        print("Computer move.")
        self.scrabble_ai.set_state(self.players[2]._player_rack, self.scrabble.SBoard)
        for i in range(5):  # Try to make a move 5 times
            move_tiles = self.players[2].make_ai_move()
            if move_tiles is not None:
                break  # If a valid move is found, break the loop

        # If no valid move is found after 5 tries, check if it's possible to exchange tiles
        if move_tiles is None and self.Computer_exchanges < 6:  # If not yet reached the limit of exchanges
            print("No valid move found after 5 tries, exchange tiles and try again.")
            print("Computer exchanges =", self.Computer_exchanges)
            old_tiles = self.players[2]._player_rack
            self.players[2].exchange_tiles(old_tiles)
            self.update_player_tiles()
            self.Computer_exchanges += 1
            move_tiles = self.players[2].make_ai_move()
        # If no valid move is found after retrying, skip the turn

        if move_tiles is None:
            if self.Computer_skips < 6:  # If not yet reached the limit of skips
                print("No valid move found after exchanging tiles. Skipping turn.")
                self.Computer_skips += 1
                print("Computer skips =", self.Computer_skips)
                self.switch_turn()
            else:  # If reached the limit of skips
                print("No valid move found and skip limit reached. Game over.")
                self.game_over()
            return

        if move_tiles is not None:
            print("computer move = ", move_tiles)
            self.handle_ai_moves(move_tiles)
            self.update_player_tiles()
            return

    def handle_ai_moves(self, move_tiles):
        print("move tiles are", move_tiles)
        print("player tiles", self.player_tiles)
        used_tiles = set()
        # Iterate through the tiles to move
        for (row, col, letter) in move_tiles:
            # Search for the tile with the corresponding letter in the player's rack
            for tile in self.player_tiles:
                if tile.letter == letter and not tile.on_board and tile not in used_tiles:
                    # Move the tile to the correct position on the board
                    tile.board_x = row
                    tile.board_y = col
                    tile.on_board = True
                    tile.rect.topleft = tile_to_pixel(row, col)
                    used_tiles.add(tile)
                    break
        self._submit_turn()

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
                self.update_player_tiles()  # Update player tiles after the exchange
                print("Your new exchanged tiles are: ", self.currentPlayer._player_rack)
                print("Switching turns")
                self.player_exchange += 1
                self.switch_turn()
            elif evt.key == pygame.K_SPACE:
                if self.selectedTile:
                    self.selectedTile.rerack()
                    self.selectedTile = None
            elif evt.key == pygame.K_LCTRL:
                print("You have skipped your turn")
                self.switch_turn()
                self.player_skip += 1
            elif evt.key == pygame.K_QUESTION:
                print("You have asked for help")
                self.Player_help += 1
            elif self.selectedTile and self.selectedTile.is_blank and evt.unicode.isalpha():
                letter = evt.unicode.lower()
                self.selectedTile.letter = letter
                self.selectedTile.tileBlock = self.letterTiles.image_at(LETTER_COORDINATES[letter])
                blank_index = self.player_tiles.index(self.selectedTile)
                self.currentPlayer._player_rack[blank_index] = letter

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

    def is_game_over(self):
        return len(self.bag._bag) == 0 and len(self.currentPlayer.get_rack()) == 0

    def game_over(self):
        print("Game Over!")
        # Stop the game loop
        self.running = False

        # Create a game over surface and position it in the middle of the screen
        font = pygame.font.Font('freesansbold.ttf', 64)
        font2 = pygame.font.Font('freesansbold.ttf', 44)
        game_over_surface = font.render("Game Over", True, (0, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(400, 400))
        text_surface = font2.render("Press 'ESC' to close screen", True, (0, 0, 0))
        text_surface_rect = text_surface.get_rect(center=(500, 500))

        while not self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Draw the game over surface
            self.screen.blit(game_over_surface, game_over_rect, text_surface, text_surface_rect)

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

    def _submit_turn(self):
        """
        Submits the turn to the scrabble backend. Moves the player tiles to
        game tiles and updates the player tiles.
        """
        print("move submitted")  # player.submit_move(self, self.board)  # currently broken
        print(f"Submitting move with move_count = {self.scrabble.moveCount}")
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

            # Switch to the other player
            self.switch_turn()
            self.update_player_tiles()
            self.scrabble_ai.clear_possible_moves()

        else:
            # Invalid turn, return all tiles to rack
            for tile in self.player_tiles:
                tile.rerack()
            if self.currentPlayerKey == 2:
                print("Computer tries again!")
                self.computer_move()
                #self.Computer_exchanges +=1

        if self.is_game_over():
            # You need to decide what should happen when the game is over.
            print("Game Over!")
            print(f"Final score: {self.currentPlayer.get_total_score()}")
            pygame.quit()
            sys.exit()

    def computer_move_thread(self):
        self.computer_move()
        self.update_player_tiles()

    def switch_turn(self):
        self.currentPlayerKey = 3 - self.currentPlayerKey
        self.currentPlayer = self.players[self.currentPlayerKey]
        self.update_player_tiles()
        if self.currentPlayerKey == 1:
            print("Player", self.currentPlayerKey, "'s turn!")

        else:
            self.currentPlayer = self.players[self.currentPlayerKey]
            print("Computer's turn!")
            # Start the computer move in a separate thread
            computer_move_thread = threading.Thread(target=self.computer_move_thread)
            computer_move_thread.start()


