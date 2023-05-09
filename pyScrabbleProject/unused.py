import sys
from random import shuffle

import gamestate
import tileModule
import resourceFile
import move
import pygame

from scoringSystem import DISTRIBUTION
#from scrabble import Scrabble


'''if evt.type == pygame.MOUSEBUTTONUP:
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
            self.selectedTile = None'''


'''
                    if row != 14 and self.scrabbleInstance.SBoard[row + 1][col] == None:
                        if len(LetterTest) == 1:
                            LetterTest += self.scrabbleInstance.SBoard[row][col]
                            LetterList.append(LetterTest)
                        LetterTest = ''
                        
                    if col != 14 and self.scrabbleInstance.SBoard[row][col + 1] == None:
                        if len(LetterTest) == 1:
                            LetterTest += self.scrabbleInstance.SBoard[row][col]
                            LetterList.append(LetterTest)
                        LetterTest = ''


'''

'''
class TrieNode:
    def __init__(self, char=None):
        self.children = {}
        self.is_end_of_word = False
        self.char = char


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def find_words(self, prefix, rack, node=None, path=None, words=None):
        if words is None:
            words = set()
        if path is None:
            path = []
        if node is None:
            node = self.root

        # Iterate through the characters in the prefix
        for char in prefix:
            if char not in node.children:
                return words
            node = node.children[char]

        if node.is_end_of_word and len(path) > 0:
            words.add("".join(path))

        for child in node.children.values():
            if child.char in rack:
                rack_copy = list(rack)
                rack_copy.remove(child.char)
                self.find_words(prefix, rack_copy, node=child, path=path + [child.char], words=words)
        print("words", words)
        return words
'''

'''
    def find_words_on_board(self):
        words = []
        # Search for horizontal words
        for row in range(15):
            word = ''
            for col in range(15):
                if self.scrabbleInstance.SBoard[row][col] != None:
                    word += self.scrabbleInstance.SBoard[row][col]

                else:
                    if len(word) > 1:
                        words.append(word)
                    word = ''
            if len(word) > 1:
                words.append(word)

        # Search for vertical words
        for col in range(15):
            word = ''
            for row in range(15):
                if self.scrabbleInstance.SBoard[row][col] != None:
                    word += self.scrabbleInstance.SBoard[row][col]

                else:
                    if len(word) > 1:
                        words.append(word)
                    word = ''
            if len(word) > 1:
                words.append(word)

        return words

    def find_letters_on_board(self):
        LetterList = []
        # Search for horizontal free Letters
        for row in range(15):
            LetterTest = ''
            for col in range(15):
                if self.scrabbleInstance.SBoard[row][col] is not None:
                    if col != 14 and self.scrabbleInstance.SBoard[row][col + 1] == None:
                        if len(LetterTest) < 2:
                            LetterTest += self.scrabbleInstance.SBoard[row][col]
                            LetterList.append((LetterTest, row, col, 'horizontal'))
                        LetterTest = ''

                else:
                    if len(LetterTest) < 2:
                        LetterList.append((LetterTest, row, col, 'horizontal'))
                    LetterTest = ''
            if len(LetterTest) < 2:
                LetterList.append((row, col, 'horizontal'))

        # Search for vertical free Letters
        for col in range(15):
            LetterTest = ''
            for row in range(15):
                if self.scrabbleInstance.SBoard[row][col] != None:
                    if row != 14 and self.scrabbleInstance.SBoard[row + 1][col] == None:
                        if len(LetterTest) < 2:
                            LetterTest += self.scrabbleInstance.SBoard[row][col]
                            LetterList.append((row, col, 'vertical'))
                        LetterTest = ''
                else:
                    if len(LetterTest) < 2:
                        LetterList.append((row, col, 'vertical'))
                    LetterTest = ''
                if len(LetterTest) < 2:
                    LetterList.append((row, col, 'vertical'))
        print("Letter list should be:", LetterList)
        return LetterList

    # Usage: Call this function with the board as an argument
    def find_valid_words(self, word):
        valid_words = list(anagram(word))
        print("valid words: ", valid_words)
        return valid_words

    def find_valid_words_from_letters(self, letter):
        WordsThatCanBeMade = list(anagram(letter))
        print("2Extra Words that can be made based on available letters on board", WordsThatCanBeMade)
        return WordsThatCanBeMade

    def find_possible_words(self, word):
        possible_words = list(children(word)) #uses the word as a prefix
        print("Possible letters to use in next move: ", possible_words)
        matchingLetter = ','
        matchingLetters = []

        for letter in possible_words:
            letter = letter.upper()
            if letter in self.player._player_rack:
                print("Rack contains letter:", letter)
                matchingLetter += letter
                matchingLetters.append(matchingLetter)
        print("Matching letters from rack and possible_words are: ", matchingLetters)
        #now to figure out way that it acc tells us the words that can be made
        return possible_words

    def find_possible_words_from_letters(self, letter1):
        possible_words_from_letter = list(children(letter1)) #uses the letter as a prefix
        #print("letter found is", letter1)
        #print("2Possible letters to use in next move: ", possible_words_from_letter)
        matchingLetter1 = ','
        matchingLetters1 = []

        for letter1 in possible_words_from_letter:
            letter1 = letter1.upper()
            if letter1 in self.player._player_rack:
                print("2Rack contains letter:", letter1)
                matchingLetter1 += letter1
                matchingLetters1.append(matchingLetter1)
        print("2Matching letters from rack and possible_words are: ", matchingLetters1)
        #now to figure out way that it acc tells us the words that can be made
        return possible_words_from_letter
'''

'''    def process_anchor(self, anchor_pos):
        if self.is_filled(self.prev_coord(anchor_pos)):
            scan_pos = self.prev_coord(anchor_pos)
            partial_word = self.get_tile(scan_pos)
            while self.is_filled(self.prev_coord(scan_pos)):
                scan_pos = self.prev_coord(scan_pos)
                partial_word = self.get_tile(scan_pos) + partial_word
            pw_node = self.dictionary.search(partial_word)
            if pw_node is not None:
                self.extend_right(partial_word, pw_node, anchor_pos, False)
        else:
            limit = 0
            scan_pos = anchor_pos
            while self.is_empty(self.prev_coord(scan_pos)) and self.prev_coord(scan_pos) not in anchors:
                limit = limit + 1
                scan_pos = self.prev_coord(scan_pos)
            self.left_part("", self.dictionary.root, anchor_pos, limit)'''

#rack = self._player_rack
        #words_on_board = self.AIscrabbleInstance.find_words_on_board()
        #letters_on_board = self.AIscrabbleInstance.find_letters_on_board()
        # letters_on_board if sboard row col next to letter = None then can use letter otherwise not
        #for item in words_on_board:
            #item = item.lower()
        #AIScrabbleInstance.find_valid_words(item)
        #AIScrabbleInstance.find_possible_words(item)
        #valid_words = self.AIscrabbleInstance.find_words_to_play()
        #print("Words that can be made with rack and board letters: ", valid_words)
        #for item1 in letters_on_board:
            #item1 = item1.lower()
        #AIScrabbleInstance.find_valid_words_from_letters(item1)
        #AIScrabbleInstance.find_possible_words_from_letters(item1)


        #best_move = self.find_best_move()

        #if best_move is None:
         #   print("No valid moves found for the AI player.")
          #  return

        #score, word, start_pos, direction = best_move
        #tiles = [(start_pos[0] + i * direction[0], start_pos[1] + i * direction[1], letter) for i, letter in
         #        enumerate(word)]

       # if self.AIscrabbleInstance.submit_turn(tiles):
       #     print(f"AI placed the word '{word}' with a score of {score}.")
