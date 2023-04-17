import random
import scoringSystem as sS


class Deck:
    '''
    An entire class dedicated to the operations surrounding the Scrabble deck.
    On initialization, fills in self.d, and shuffles it.
    '''
    def __init__(self):
        self._player_rack = []
        self.init_deck()

    def init_deck(self):
        self.d = []
        for letter, freq in sS.DISTRIBUTION.items():
            # Blows up letter frequency into long repeated string, then converts
            # into list and uses said list to extend the dictionary. Repeat for
            # all the letters, and you get a nice repetitive deck
            self.d.extend(list(letter * freq))

        # Shuffle it
        random.shuffle(self.d)

    def take(self, n):
        '''
        Tries to get the first n letters of the deck. Shuffles deck afterwards.
        '''
        ret = self.d[:n]
        del self.d[:n]
        random.shuffle(self.d)

        return ret

    def place(self, l):
        '''
        Appends all tiles from list l to end of deck. Shuffles deck afterwards.
        '''
        self.d.extend(l)
        random.shuffle(self.d)
