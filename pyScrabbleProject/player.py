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

