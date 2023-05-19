import unittest
import pytest
import pygame
from unittest.mock import Mock, patch
from computerplayer import AIPlayer, ComputerGame
from player import Player, Bag
from resourceFile import ResourceManager
from scrabble import Scrabble
from ScrabbleAI import AIScrabble
pygame.init()
resource_management = ResourceManager()


def test():
    scrabble = Scrabble(True, players=Player(Bag()), num_players=2)


    # Test 1: Test the '_is_valid_word' method with a valid word
    print("Test 1: Valid Word Test")
    assert scrabble._is_valid_word('cat')
    print("Passed Valid Word Test!")

    # Test 2: Test the '_is_valid_word' method with an invalid word
    print("Test 2: Invalid Word Test")
    assert not scrabble._is_valid_word('notaword')
    print("Passed Invalid Word Test!")


    # Test 3: Test the 'submit_turn' method with an invalid turn
    print("Test 3: Invalid Turn Test")
    assert not scrabble.submit_turn([(7, 7, 'C'), (8, 8, 'A'), (9, 9, 'T')])
    print("Passed Invalid Turn Test!")

    # Test 4: Test the 'switch_turn' method
    print("Test 4: Switch Turn Test")
    scrabble.switch_turn()
    assert scrabble.current_player_index == 2
    scrabble.switch_turn()
    assert scrabble.current_player_index == 1
    print("Passed Switch Turn Test!")

    # Test 5: Test '_is_colinear' method with a colinear and non-colinear inputs
    print("Test 5: Colinear Test")
    assert scrabble._is_colinear([1, 1, 1], [1, 2, 3])
    assert not scrabble._is_colinear([1, 2, 3], [1, 2, 3])
    print("Passed Colinear Test!")


def test_ai_player():
    bag = Bag()
    scrabble_instance = Scrabble(True, {1: Player(bag), 2: None}, 2)
    ai_scrabble = AIScrabble(True, None, scrabble_instance, min_score=0, max_score=100)
    ai_player = AIPlayer(bag, ai_scrabble)
    assert ai_player.bag == bag
    assert ai_player.AIscrabbleInstance == ai_scrabble



class TestAIScrabble(unittest.TestCase):
    def setUp(self):
        self.scrabble = Scrabble(debug=True, players=Player(Bag()),num_players=1)
        self.ai_scrabble = AIScrabble(debug=True, player=Player(Bag()),
                                      scrabbleInstance=self.scrabble,
                                      min_score=10, max_score=100)

    def test_set_state(self):
        # Assuming you have valid player_rack and board_state
        player_rack = ['a', 'b', 'c']
        board_state = [[' ']*15 for _ in range(15)] # example board state

        result = self.ai_scrabble.set_state(player_rack, board_state)
        self.assertEqual(result, (player_rack, board_state))

    def test_is_valid_word(self):
        # Assuming 'hello' is a valid word
        result = self.ai_scrabble._is_valid_word('hello')
        self.assertTrue(result)

    def test_in_bounds(self):
        pos = (7, 7)  # Should be within the 15x15 board
        result = self.ai_scrabble.in_bounds(pos)
        self.assertTrue(result)

        pos = (15, 15)  # Outside the 15x15 board
        result = self.ai_scrabble.in_bounds(pos)
        self.assertFalse(result)



if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    test()


