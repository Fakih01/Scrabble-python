import sys
from random import shuffle

import gamestate
import tileModule
import resourceFile
import move
import pygame

from scoringSystem import DISTRIBUTION
#from scrabble import Scrabble


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
        rack = scrabbleInstance._player_rack
        self.rackList = list(rack)

    def __contains__(self, position):
        '''
        Returns true if point is inside player hand rectangle, and false if
        otherwise.
        Uses pygame Rect.collidepoint method to compact code.
        '''
        return self.rect.collidepoint(position)

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
        print("get_the_rack called", self.rackList)  # trying
        print("Now we need a new rack. fix it.")
        return self.rackList

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

    def drawHand(self, scrn, resourceManagement, position):
        '''
        Draws player's hand
        '''
        for i in range(len(self.scrabble._player_rack)):
            scrn.blit(resourceManagement.board_tiles[self.scrabble._player_rack[i]],
                      (position[0] + resourceFile.Tile_Size[0] * i,
                       position[1]))

