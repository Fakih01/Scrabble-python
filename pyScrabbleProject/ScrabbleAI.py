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
        possible_words = list(children(word)) #uses the word as a prefix, is there a way it can also use each indiv letter as a prefix too?
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

    def find_words_to_play(self, word):
        possible_letters = list(children(word))
        print("Possible letters to use in next move: ", possible_letters)

        # Combine rack letters with possible_letters from the board
        combined_letters = self.player._player_rack + possible_letters

        # Find all unique combinations of letters of lengths ranging from 2 to the length of combined_letters
        all_combinations = []
        for i in range(2, len(combined_letters) + 1):
            all_combinations.extend(list(itertools.combinations(combined_letters, i)))

        # Find all unique permutations of each combination
        all_permutations = set()
        for combination in all_combinations:
            all_permutations.update(itertools.permutations(combination))

        # Check if any permutation forms a valid word
        valid_words = []
        for perm in all_permutations:
            candidate_word = ''.join(perm)
            if self._is_valid_word(candidate_word):  # Assuming _is_valid_word() checks if a word is valid
                valid_words.append(candidate_word)

        print("Words that can be made with rack and board letters: ", valid_words)
        return valid_words

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




