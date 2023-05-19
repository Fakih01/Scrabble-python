import pygame
import colours
import scoringSystem as sS

Scrabble_Number_Font = "Futura9"
Scrabble_Tile_Font = "Futura40"
Scrabble_Board_Font = "Futura20"
Tile_Size = (50, 50)
'''
Helps with loading the different fonts and their corresponding sizes.
Format:
    (base_name_of_font,
     font_file_name,
     list_of_font_sizes)
'''
Fonts_Config = [
    # Used for scrabble tiles
    ('Futura',      'FuturaExtended.ttf',       [9, 20, 40]),
    # Used for everything else
    ('OpenSans',    'OpenSans-Regular.ttf',     [50])
]
'''
Helps with loading the different types of board tiles (i.e. where they are on
the tile map).
Format:
    (tile_shortname,
     should_render_shortname?,
     (x, y, w, h))
'''
Board_Tiles = [
    ('NM', False, ( 50,  0, 50, 50)),     # Normal tile
    ('MD', False, (100,  0, 50, 50)),     # That tile in the middle
    ('DL',  True, (150,  0, 50, 50)),     # Double letter
    ('TL',  True, (200,  0, 50, 50)),     # Double word
    ('DW',  True, (250,  0, 50, 50)),     # Triple letter
    ('TW',  True, (300,  0, 50, 50))      # Triple word
]


class ResourceManager:
    '''
    The resource man(ager). Tracks all the resources and provides
    references to them for all the other classes to use (and draw).
    Must be initialised and linked at the start of the program.
    '''
    def __init__(self):
        pygame.init()
        self.fonts = {}
        self.board_tiles = {}

        self.init_tiles("resources/images/tile_resources.png")

        self.finishedLoading = True

    def init_tiles(self, fn):
        '''
        initialises self.tiles dictionary for fast lookup of
        tile surfaces.
        '''
        # Load tiles
        self.tilesMap = pygame.image.load(fn)

        # Load fonts (for font writing)
        self.init_fonts()

        # Loads tiles on the board
        self.init_board_tiles()

    def init_fonts(self):
        '''
        Loads all the fonts into memory.
        '''
        for key, fn, sizes in Fonts_Config:
            for size in sizes:
                self.fonts[key + str(size)] = pygame.font.Font('./resources/fonts/' + fn, size)

    def init_board_tiles(self):
        '''
        Loads all the board tiles into memory.
        '''
        for key, render, rect in Board_Tiles:
            t = self.tilesMap.subsurface(*rect).copy()

            if render:
                # Render bonuses
                letter_s = self.fonts[Scrabble_Board_Font].render(
                                        key,
                                        True,
                                        colours.BLACK)
                letter_sx = (Tile_Size[0] - letter_s.get_width())  / 2
                letter_sy = (Tile_Size[1] - letter_s.get_height()) / 2
                t.blit(letter_s, (letter_sx, letter_sy))

            self.board_tiles[key] = t
