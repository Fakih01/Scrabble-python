import pygame
import itertools
from twl import *
from gamestate import *
from scrabble import *


class AIScrabble(Scrabble):
    def __init__(self, debug, scrabbleInstance, num_players):
        self.scrabbleInstance = scrabbleInstance
        super().__init__(debug, num_players)

    def _is_valid_word(self, word):
        print("word:", word)
        check(word)
    # need to search board for words and return anagrams first.

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

    # Usage: Call this function with the board as an argument

    def find_valid_words(self, word):
        valid_words = list(anagram(word))
        print("valid words: ", valid_words)
        return valid_words

    def find_possible_words(self, word):
        possible_words = list(children(word))
        print("Possible words: ", possible_words)


    def find_valid_moves(self):
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
        #prints scarbble board to see if same  being used across code.




