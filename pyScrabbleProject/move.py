import board

#don't think i acc need this anymore


class Move:

    def __init__(self, letter):
        self.m = []
        self.UsedLetters = []
        self.SB = board.ScrabbleBoard

        # The type of move can be one of 3 characters:
        # 'M' -> Your standard move (placing tiles on board)
        # 'E' -> Exchange (the placed tiles on board get swapped with others in
        #        the deck
        # 'P' -> Pass (all placed tiles return to hand and the next turn
        #        happens)
        # Defaults to 'M'
        self.t = 'M'

        # If the move is chained together with other tiles on the board, it will be true, otherwise, false.
        self.is_chain = False
        self.vert, self.horz = None, None

    def get_item(self, x, y):

        # Finds the move with coordinates equal to (x, y). Error if move doesn't exist.

        for i, j, l in self.m:
            if i == x and j == y:
                return (i, j, l)
        raise ValueError('invalid indices (%d, %d)' % (x, y))



