import pygame
from collections import defaultdict
import random
from player import Bag
from word_dictionary import *
from singleplayer import *
from scrabble import *


def ScrabbleDict():
    word_list = set(iterator())
    return Trie(word_list)


class AIScrabble(Scrabble):
    min_score = 0
    max_score= 0

    def __init__(self, debug, player, scrabbleInstance, min_score, max_score):
        self.possible_moves = []
        self.this_move_score = 0
        self.this_move = None
        self.cross_check_results = None
        self.scrabbleInstance = scrabbleInstance
        self.direction = None
        self.dictionary = ScrabbleDict()
        self.player = player
        self.min_score = min_score
        self.max_score = max_score
        AIScrabble.min_score = self.min_score
        AIScrabble.max_score = self.max_score
        super().__init__(debug, self.player, 2)
        print("min score is", self.min_score, "max score is", self.max_score)
        if self.min_score == 0:
            print("You chose easy level")
        else:
            print("you have chosen hard level")

    def set_players(self, players):
        self.players = players

    def _is_valid_word(self, word):
        print("word is:", word, "and it is valid!")
        return check(word)
    # need to search board for words and return anagrams first.

    def get_tile(self, pos):
        row, col = pos
        tile = self.scrabbleInstance.SBoard[row][col]
        if tile is not None:
            tile = tile.lower()
        return tile

    def find_letters_on_board(self):
        LetterList = []
        for r in range(15):  # Changed variable name from row to r
            for c in range(15):  # Changed variable name from col to c
                if self.scrabbleInstance.SBoard[r][c] is not None:
                    letter = self.scrabbleInstance.SBoard[r][c]
                    pos = (r, c)
                    LetterList.append((pos, letter))
                    self.set_tile(pos, letter)
        #print("Letter list should be:", LetterList)
        return LetterList

    def set_tile(self, pos, BoardTile):
        row, col = pos
        self.scrabbleInstance.SBoard[row][col] = BoardTile
        #print("Set Tile", BoardTile) #not working

    def in_bounds(self, pos):
        row, col = pos
        return row >= 0 and row <= 14 and col >= 0 and col <= 14

    def is_empty(self, pos):
        return self.in_bounds(pos) and self.get_tile(pos) == None

    def is_filled(self, pos):
        return self.in_bounds(pos) and self.get_tile(pos) != None

    def all_positions(self):
        for r in range(15):
            for c in range(15):
                pos = (r, c)
                yield pos

    def prev_coord(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row, col - 1
        else:
            return row - 1, col

    def next_coord(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row, col + 1
        else:
            return row + 1, col

    def prev_cross_coord(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row - 1, col
        else:
            return row, col - 1

    def next_cross_coord(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row + 1, col
        else:
            return row, col + 1

    def get_col(self, pos):
        return pos[1]

    def print_board_here(self):
        for i in range(15):
            for j in range(15):
                if self.scrabbleInstance.SBoard[j][i] == None:
                    print('_', end='')
                elif self.scrabbleInstance.SBoard[j][i] == ' ':
                    print('-', end='')
                else:
                    print(self.scrabbleInstance.SBoard[j][i], end='')
            print('')
        print("Rack: ", self.player_rack)
        #prints scrabble board to see if same  being used across code.

    def legal_move(self, word, last_pos, min_score):
        word_len = len(word)
        start = last_pos
        end = last_pos
        for _ in range(word_len - 1):
            start = self.prev_coord(start)

        letters = {}
        temp_pos = start
        for letter in word:
            while self.is_filled(temp_pos) and self.get_tile(temp_pos) != letter:
                temp_pos = self.next_coord(temp_pos)
            letters[temp_pos] = letter
            temp_pos = self.next_coord(temp_pos)
        score = self._score_word_for_best_move(start, end, letters, word)
        if score > self.min_score and score <= self.max_score:
            self.this_move = (word, start, end, letters)
            self.this_move_score = score
            self.possible_moves.append((self.this_move, self.this_move_score))
            return True
        return False

    def _score_word_for_best_move(self, start, end, letters, word):
        """
        Adds the score of the valid word between start and end.
        """
        score = 0
        multiplier = 1
        for row in range(start[0], end[0] + 1):
            for col in range(start[1], end[1] + 1):
                if (row, col) in letters:
                    # Check for score modifiers
                    multiplier *= WORD_MULTIPLIERS.get((row, col), 1)
                    score += POINTS[letters[(row, col)]]*LETTER_MULTIPLIERS.get((row, col), 1)
                else:
                    # Tile must be on board, add it's value
                    score += POINTS[self.scrabbleInstance.SBoard[row][col]]
        self.word_score = 0
        self.word_score += score*multiplier
        return self.word_score

    def make_random_move(self):
        if self.possible_moves:  # Check if there are any possible moves
            #print("make moves only possib;le starting with letter A")
            move = random.choice(self.possible_moves)  # Select a random move

            #print("chosen move = ", move)
            word, start, end, letters = move[0]
            # Find the letters on the board
            letters_on_board = self.find_letters_on_board()
            tiles = [(row, col, letter) for (row, col), letter in letters.items() if
                     ((row, col), letter) not in letters_on_board]

            #print("Your tiles for submission are:", tiles)
            print(f"Random move is '{word}' with a score of {move[1]}")
            return tiles

        else:
            print("No moves found.")

    def clear_possible_moves(self):
        self.possible_moves = []  # Clear the possible moves for the next round

    def cross_checker(self, anchors):
        result = dict()

        # Create a list of positions to cross-check
        positions_to_check = set()
        for anchor in anchors:
            positions_to_check.add(anchor)
            positions_to_check.add(self.prev_coord(anchor))
            positions_to_check.add(self.next_coord(anchor))

        for pos in positions_to_check:
            if self.is_filled(pos):
                continue

            letters_before = ""
            scan_pos = pos
            while self.is_filled(self.prev_cross_coord(scan_pos)):
                scan_pos = self.prev_cross_coord(scan_pos)
                letters_before = self.get_tile(scan_pos) + letters_before

            letters_after = ""
            scan_pos = pos
            while self.is_filled(self.next_cross_coord(scan_pos)):
                scan_pos = self.next_cross_coord(scan_pos)
                letters_after = letters_after + self.get_tile(scan_pos)

            if len(letters_before) == 0 and len(letters_after) == 0:
                legal_here = list('a')
            else:
                legal_here = []
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    word_formed = letters_before + letter + letters_after
                    if self.dictionary.is_word(word_formed):
                        legal_here.append(letter)

            result[pos] = legal_here

        return result

    def finding_anchors(self):
        anchors = []
        for pos in self.all_positions():
            empty = self.is_empty(pos)
            neighbor_filled = self.is_filled(self.prev_coord(pos)) or \
                              self.is_filled(self.next_coord(pos)) or \
                              self.is_filled(self.prev_cross_coord(pos)) or \
                              self.is_filled(self.next_cross_coord(pos))
            if empty and neighbor_filled:
                anchors.append(pos)
        #print("finding anchors:", anchors)  #works
        return anchors

    def left_part(self, partial_word, current_node, anchor_pos, limit):
        self.extend_right(partial_word, current_node, anchor_pos, False)
        if limit > 0:
            for next_letter in current_node.children.keys():
                if next_letter in self.player_rack:
                    self.player_rack.remove(next_letter)
                    self.left_part(partial_word + next_letter, current_node.children[next_letter], anchor_pos,
                                   limit - 1)
                    self.player_rack.append(next_letter)

    def extend_right(self, partial_word, current_node, next_pos, anchor_filled):
        if len(partial_word) + len(self.player_rack) > 14:
            return

        if not self.is_filled(next_pos) and current_node.is_word and anchor_filled:
            self.legal_move(partial_word, self.prev_coord(next_pos), self.min_score)

        if self.in_bounds(next_pos):
            if self.is_empty(next_pos):
                for next_letter in current_node.children.keys():
                    if next_letter in self.player_rack and next_pos in self.cross_check_results and next_letter in \
                            self.cross_check_results[next_pos]:
                        self.player_rack.remove(next_letter)
                        self.extend_right(partial_word + next_letter, current_node.children[next_letter],
                                          self.next_coord(next_pos), True)
                        self.player_rack.append(next_letter)
            else:
                existing_letter = self.get_tile(next_pos)
                if existing_letter in current_node.children.keys():
                    self.extend_right(partial_word + existing_letter, current_node.children[existing_letter],
                                      self.next_coord(next_pos), True)

    def set_state(self, player_rack, board_state):
        """Updates the AI's view of the game state."""
        self.player_rack = player_rack
        self.board_state = board_state
        return self.player_rack, self.board_state

    def find_possible_words(self, min_score):
        print(min_score)
        print("finding all options")
        self.find_letters_on_board()  # Call to find_letters_on_board here
        word_counter = 0  # Add a counter for words found
        for direction in ['across', 'down']:
            self.direction = direction
            anchors = self.finding_anchors()
            self.cross_check_results = self.cross_checker(anchors)
            for anchor_pos in anchors:
                if self.is_filled(self.prev_coord(anchor_pos)):
                    scan_pos = self.prev_coord(anchor_pos)
                    partial_word = self.get_tile(scan_pos)
                    while self.is_filled(self.prev_coord(scan_pos)):
                        scan_pos = self.prev_coord(scan_pos)
                        partial_word = self.get_tile(scan_pos) + partial_word
                    pw_node = self.dictionary.search(partial_word)
                    if pw_node is not None:
                        if self.extend_right(partial_word, pw_node, anchor_pos, False):
                            word_counter += 1
                            if word_counter >= 5:
                                return
                else:
                    limit = 0
                    scan_pos = anchor_pos
                    while self.is_empty(self.prev_coord(scan_pos)) and self.prev_coord(scan_pos) not in anchors:
                        limit = limit + 1
                        scan_pos = self.prev_coord(scan_pos)
                    if self.left_part("", self.dictionary.root, anchor_pos, limit):
                        word_counter += 1
                        if word_counter >= 5:
                            return


class TrieNode:
    def __init__(self, is_word):
        self.is_word = is_word
        self.children = defaultdict(lambda: TrieNode(False))


class Trie:
    def __init__(self, words):
        self.root = TrieNode(False)
        for word in words:
            current_node = self.root
            for letter in word:
                current_node = current_node.children[letter]
            current_node.is_word = True

    def search(self, word):
        current_node = self.root
        for letter in word:
            if letter not in current_node.children.keys():
                return None
            current_node = current_node.children[letter]
        return current_node

    def is_word(self, word):
        word_node = self.search(word)
        if word_node is None:
            return False
        return word_node.is_word

