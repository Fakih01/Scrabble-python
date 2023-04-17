import scoringSystem


class tileCheck:
    def __init__(self, letter):
        '''
        All letters are uppercase unless it is lowercase, in which case, it is a
        blank tile.
        '''
        self.isblank = letter.islower()
        self.letter = letter.upper()
        self.value = scoringSystem.POINTS(letter)

        if self.isblank:
            self.value = 0

    def draw(self, scrn, position, resourceManagement):
        '''
        '''
        #scrn.blit(resourceManagement.board_tiles[self.letter], position)


class Bonus:
    def __init__(self, b):
        self.b = b

    def draw(self, scrn, position, resourceManagement):
        '''
        '''
        scrn.blit(resourceManagement.board_tiles[self.b], position)
