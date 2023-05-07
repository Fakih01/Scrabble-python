import pygame
import itertools
from concurrent.futures import ThreadPoolExecutor
from twl import *
from gamestate import *
from scrabble import *


def ScrabbleDict():
    word_list = set(iterator())
    return Trie(word_list)


class AIScrabble(Scrabble):
    def __init__(self, debug, scrabbleInstance, num_players):
        self.cross_check_results = None
        self.scrabbleInstance = scrabbleInstance
        self.direction = None
        self.dictionary = ScrabbleDict()
        self.memo_cross_check = {}
        self.memo_extend_after = {}
        super().__init__(debug, num_players)

    def _is_valid_word(self, word):
        print("word is:", word, "and it is valid!")
        return check(word)
    # need to search board for words and return anagrams first.

    def get_tile(self, pos):
        row, col = pos
        tile = self.scrabbleInstance.SBoard[row][col]
        if tile is not None:
            tile = tile.lower()
        #print("get tile:", tile)
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
        print("Letter list should be:", LetterList)
        return LetterList

    def set_tile(self, pos, BoardTile):
        row, col = pos
        self.scrabbleInstance.SBoard[row][col] = BoardTile
        print("Set Tile", BoardTile) #not working

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

    def copy(self):
        # Create a new AIScrabble instance with the same debug and num_players settings
        new_instance = AIScrabble(debug=True,scrabbleInstance=Scrabble(True, 2), num_players=2)

        # Set the tiles in the new_instance based on the current instance's tiles
        for pos in self.all_positions():
            new_instance.set_tile(pos, self.get_tile(pos))

        # Set the direction and cross_check_results in the new_instance
        new_instance.direction = self.direction
        new_instance.cross_check_results = self.cross_check_results

        # Set the player rack in the new_instance
        new_instance.player._player_rack = self.player._player_rack.copy()

        # Return the new instance
        return new_instance

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
        print("Rack: ", self.player._player_rack)
        #prints scrabble board to see if same  being used across code.

    def legal_move(self, word, last_pos):
        print("Rack is", self.player._player_rack)
        print("LEGAAAAAAAAAAAAAAAALLLLLLLLLLLLLLLL MOVVVVVVVVVVVVVEEEEEEEEEEEEEEEEEE")
        print('found a word:', word) # need to optimize to run faster. already cached but still slow because of size of word list. also need to optimise based on scores?
        board_if_we_played_that = self.copy()
        play_pos = last_pos
        word_idx = len(word) - 1
        while word_idx >= 0:
            board_if_we_played_that.set_tile(play_pos, word[word_idx])
            word_idx -= 1
            play_pos = self.prev_coord(play_pos)
        print(board_if_we_played_that)
        print()

    def cross_checker(self):
        if self.direction in self.memo_cross_check:
            return self.memo_cross_check[self.direction]
        result = dict()
        for pos in self.all_positions():
            if self.is_filled(pos):
                print("cross check, is filled")
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
                legal_here = list('abcdefghijklmnopqrstuvwxyz')
            else:
                legal_here = []
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    word_formed = letters_before + letter + letters_after
                    if self.dictionary.is_word(word_formed):
                        legal_here.append(letter)
            result[pos] = legal_here
        self.memo_cross_check[self.direction] = result
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
        print("finding anchors:", anchors)  #works
        return anchors

    def left_part(self, partial_word, current_node, anchor_pos, limit):
        #print("In before_part")
        #print("partial_word:", partial_word)
        #print("anchor_pos:", anchor_pos)
        #print("current_node:", current_node)
        #print("Calling extend_after from before_part")
        self.extend_right(partial_word, current_node, anchor_pos, False)
        #print("Called extend_after from before_part")
        if limit > 0:
            for next_letter in current_node.children.keys():
                if next_letter in self.player._player_rack:
                    self.player._player_rack.remove(next_letter)
                    self.left_part(partial_word + next_letter, current_node.children[next_letter], anchor_pos,
                                   limit - 1)
                    self.player._player_rack.append(next_letter)

    def extend_right(self, partial_word, current_node, next_pos, anchor_filled):
        cache_key = (partial_word, current_node, next_pos, anchor_filled)
        if cache_key in self.memo_extend_after:
            return self.memo_extend_after[cache_key]
        print("In extend_after, checking conditions")
        print("anchor_filled:", anchor_filled)
        # Check if there are enough spaces left on the board to place remaining letters
        if len(partial_word) + len(self.player._player_rack) > 14:
            return
        if not self.is_filled(next_pos) and current_node.is_word and anchor_filled:
            print("Calling legal_move from extend_after")
            self.legal_move(partial_word, self.prev_coord(next_pos))
            print("Called legal_move from extend_after")
        if self.in_bounds(next_pos):
            if self.is_empty(next_pos):
                print("Entering loop for next_letter")
                print(f"Player rack: {self.player._player_rack}")
                print(f"Cross check results for next_pos {next_pos}: {self.cross_check_results[next_pos]}")
                for next_letter in current_node.children.keys():
                    if next_letter in self.player._player_rack and next_letter in self.cross_check_results[next_pos]:
                        print(f"Conditions met for next_letter: {next_letter}")
                        self.player._player_rack.remove(next_letter)
                        print("removing from rack", self.player._player_rack)
                        self.extend_right(partial_word + next_letter, current_node.children[next_letter],
                                          self.next_coord(next_pos), True)
                        print("Exited loop for next_letter")
                        #print("Called extend_after recursivelyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
                        self.player._player_rack.append(next_letter)
                    else:
                        print(f"Conditions not met for next_letter: {next_letter}")
            else:
                existing_letter = self.get_tile(next_pos)
                if existing_letter in current_node.children.keys():
                    self.extend_right(partial_word + existing_letter, current_node.children[existing_letter],
                                      self.next_coord(next_pos), True)
        self.memo_extend_after[cache_key] = None

    def find_possible_words(self):
        print("finding possible words")
        self.find_letters_on_board()
        self.print_board_here()

        def search_in_direction(direction):
            self.direction = direction
            anchors = self.finding_anchors()
            self.cross_check_results = self.cross_checker()
            for anchor_pos in anchors:
                if self.is_filled(self.prev_coord(anchor_pos)):
                    scan_pos = self.prev_coord(anchor_pos)
                    partial_word = self.get_tile(scan_pos)
                    while self.is_filled(self.prev_coord(scan_pos)):
                        scan_pos = self.prev_coord(scan_pos)
                        partial_word = self.get_tile(scan_pos) + partial_word
                    pw_node = self.dictionary.search(partial_word)
                    if pw_node is not None:
                        self.extend_right(
                            partial_word,
                            pw_node,
                            anchor_pos,
                            False
                        )
                else:
                    limit = 0
                    scan_pos = anchor_pos
                    while self.is_empty(self.prev_coord(scan_pos)) and self.prev_coord(scan_pos) not in anchors:
                        limit = limit + 1
                        scan_pos = self.prev_coord(scan_pos)
                    self.left_part("", self.dictionary.root, anchor_pos, limit)

        # Use ThreadPoolExecutor to parallelize searches
        with ThreadPoolExecutor() as executor:
            executor.map(search_in_direction, ['across', 'down'])


class TrieNode:
    def __init__(self, is_word):
        self.is_word = is_word
        self.children = dict()


class Trie:
    def __init__(self, words):
        self.root = TrieNode(False)
        for word in words:
            current_node = self.root
            for letter in word:
                if letter not in current_node.children.keys():
                    current_node.children[letter] = TrieNode(False)
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
