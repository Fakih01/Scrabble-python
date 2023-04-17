import sys

import pygame
from board import ScrabbleBoard
from move import Move
import player
import random
import string

import resourceFile


class State:

    '''
    An abstract class with all the functions that you
    should implement in an actual game state class.
    '''
    def __init__(self):
        pass

    def handle(self, evt):
        pass

    def draw(self, scrn):
        pass

    def update(self, delta):
        pass

