import sys
from random import shuffle

import gamestate
import tile
import resourceFile
import move
import pygame

from scoringSystem import DISTRIBUTION
from scrabble import Scrabble


class Player:
    '''
    A representation of the player, complete with current score and hand.
    Should only draw the player's own hand, and not the current move.
    '''

    def __init__(self, position, scrabbleInstance):
        '''
        initialises score and hand.
        hand should only have characters (max size 7).
        '''
        self.scrabbleInstance = scrabbleInstance
        self.scrabble = scrabbleInstance
        self.position = position
        self.currentMove = gamestate.Tile(letter=True, SBoardInstance=self.scrabble)
        self.size = (7 * resourceFile.Tile_Size[0],
                     resourceFile.Tile_Size[1])
        self.rect = pygame.Rect(self.position, self.size)
        rack = scrabbleInstance.rackList
        self.rackList = list(rack)
        self._populate_bag()
        self.shuffle_bag()

    def __contains__(self, position):
        '''
        Returns true if point is inside player hand rectangle, and false if
        otherwise.
        Uses pygame Rect.collidepoint method to compact code.
        '''
        return self.rect.collidepoint(position)

    def _populate_bag(self):
        """
        Fills the bag with the starting letter frequencies.
        """
        self._bag = []
        for letter in DISTRIBUTION:
            for _ in range(DISTRIBUTION[letter]):
                self._bag.append(letter)

    def shuffle_bag(self):
        """
        Randomizes the contents of the bag.
        """
        shuffle(self._bag)

    def all_letters_from_rack(self, letters):
        """
        Determines if all letters are present in the player's rack.
        """
        rack = self.rackList[:]
        for letter in letters:
            if letter in rack:
                rack.remove(letter)
            else:
                if self.debug:
                    print("Validation: Not all letters are from the rack")
                return False

    def num_remaining_tiles(self):
        """
        Returns how many tiles remain in the bag.
        """
        return len(self._bag)

    def exchange_tiles(self, old):
        """
        Returns the old tiles to the bag and draws an equal number to replace
        them.
        """
        # Only can return letters from the player's rack
        if self.all_letters_from_rack(old):
            # Make sure there is enough letters to exchange
            if len(old) > len(self._bag):
                return

            # Add the new tiles to the rack
            self.draw_tiles(len(old))

            # Remove the old from the rack and add them to the bag
            for letter in old:
                self.rackList.remove(letter)
                self._bag.append(letter)

            self.shuffle_bag()

    def update_player_rack(self, tiles):
        """
        Removed the letters from the player rack and draw new ones.
        """
        for _, _, letter in tiles:
            self.rackList.remove(letter)

        self.draw_tiles(len(tiles))

    def get_tile_pos(self, position):
        '''
        Returns the index of the tile, if it exists at position pos.
        Otherwise, return -1. Assumes that the position is already in the player
        hand.
        '''
        # Normalize the position
        position[0] -= self.position[0]

        ind = position[0] // resourceFile.Tile_Size[0]
        if ind < len(self.rackList):
            print("this is in position", ind)  # positioning of tile from hand
            return ind

        else:
            return -1

    def get_tile(self, position):
        '''
        Returns a single character from the position from hand.
        If the character doesn't exist, raises an exception.
        '''
        ind = self.get_tile_pos(position)

        if ind == -1:
            raise Exception("error: that isn't a tile")

        t = self.rackList[ind]
        print("this is the letter", t, "at position:", ind)
        return t

    def make_move(self, x, y, letter):  # not used
        '''
        Removes tile from hand and places it into active move (and ideally, the
        board).
        '''
        if letter not in self.rackList:
            raise Exception("error: cannot move what is not yours")
        else:
            print('make move')
            self. currentMove.add_move(x, y, letter)

        #self.get_tile(position)
        #self.get_tile_pos(position)
        #self.hand.remove(letter)

    def takeback_move(self, x, y): # not used
        '''
        Removes tile from active move (placed on board) and replace it back into
        hand.
        '''
        letter = self.currentMove.remove_move(x, y)
        self.rackList.append(letter)

    def deck_draw(self, deck, n):
        '''
        Draws n tiles from deck   # might not be needed as have the function in scrabble.py
        '''
        print("deck_draw", self.rackList)
        #self.rackList.extend(deck.take(n))  #not acc drawing any tiles

    def get_the_rack(self):
        """
        Returns a copy of the player's rack
        """
        print("get_the_rack called", self.rackList[:])  # trying
        print("Now we need a new rack. fix it.")
        return self.rackList[:]

    def deck_exchange(self, deck, l):
        '''
        Exchanges tiles in hand (list l) with random tiles in deck.
        First checks to see that the list is a subset of hand.
        '''
        if not all(map(lambda i: i in self.rackList, l)):
            raise Exception("error: cannot exchange non-existent board_tiles")

        deck.place(l)

        for i in l:
            self.rackList.remove(i)

    def drawHand(self, scrn, resourceManagement):  # could move to scrabble.py file now as fully working
        '''
        Draws player's hand
        '''
        for i in range(len(self.rackList)):
            scrn.blit(resourceManagement.board_tiles[self.rackList[i]],
                      (self.position[0] + resourceFile.Tile_Size[0] * i,
                       self.position[1]))

