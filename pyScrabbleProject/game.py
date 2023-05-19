import pygame
import gamestate as gs
import resourceFile
import TwoPlayerMode
import computerplayer
from ScrabbleAI import AIScrabble


class ScrabbleGame:
    def __init__(self):
        pygame.init()

        self.resourceManagement = resourceFile.ResourceManager()

    def play(self):  # Manages game states

        # Constants
        SIZE = (1000, 800)

        # Variables
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()
        running = True
        currentState = gs.GameState(self.resourceManagement)  # reference to the GameState class

        pygame.display.set_caption("Scrabble Game")

        while running:  # in game?
            # Event handling
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
                else:
                    currentState.handle_event(evt)  # here's where it directs to the handle function in gamestate!!!!!!!

            # Draws state
            screen.fill((0, 0, 0))
            currentState.draw(screen)
            pygame.display.flip()

            # Updating the state
            currentState.update(clock.tick(60) / 1e3)

    def TwoPlayer(self):  # Manages game states

        # Constants
        SIZE = (1000, 800)

        # Variables
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()
        running = True
        currentState = TwoPlayerMode.TwoPlayerGame(self.resourceManagement)  # reference to the TP class

        pygame.display.set_caption("Scrabble Game")

        while running:  # in game?
            # Event handling
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
                else:
                    currentState.handle_event(evt)  # here's where it directs to the handle function in gamestate!!!!!!!

            # Draws state
            screen.fill((0, 0, 0))
            currentState.draw(screen)
            pygame.display.flip()

            # Updating the state
            currentState.update(clock.tick(60) / 1e3)

    def CompPlayer(self):  # Manages game states

        # Constants
        SIZE = (1000, 800)

        # Variables
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()
        running = True
        currentState = computerplayer.ComputerGame(self.resourceManagement)  # reference to the CP class

        pygame.display.set_caption("Scrabble Game")

        while running:  # in game?
            # Event handling
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
                else:
                    currentState.handle_event(evt)  # here's where it directs to the handle function in gamestate!!!!!!!

            # Draws state
            screen.fill((0, 0, 0))
            currentState.draw(screen)

            # Updating the state
            currentState.update(clock.tick(60) / 1e3)

            pygame.display.flip()



game = ScrabbleGame()


class SceneBase:
    def __init__(self):
        self.next = self

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)


class HelpPage(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # Or any other key you prefer
                # Switch back to the StartPage when Space is pressed
                self.SwitchToScene(StartPage())

    def update(self):
        pass

    def titlePage(self, screen):
        # For the sake of brevity, the help page is a white screen with text
        screen.fill((255, 255, 255))
        black = (0, 0, 0)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 22)

        # create a text surface object,
        # on which text is drawn on it.
        text = font.render('''This is a game of scrabble where your intelligence will be put to the test!''', True,
                           black)

        # create a rectangular object for the
        # text surface object
        text_rect = text.get_rect()
        text_rect.center = (screen.get_width() // 2, screen.get_height() // 2 - 200)
        screen.blit(text, text_rect)

        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render('''Press 'SPACE' to return to the menu''', True, black)
        text_rect2 = text.get_rect()
        text_rect2.center = (screen.get_width() // 2, screen.get_height() // 2)
        screen.blit(text2, text_rect2)


class StartPage(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.show_difficulty_popup = False

    def process_input(self, events, pressed_keys):
        self.needs_update = False
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(game.play())
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(game.TwoPlayer())
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.show_difficulty_popup = True  # show the popup when 'c' is pressed
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.SwitchToScene(game.CompPlayer())
                AIScrabble.min_score = 0
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                self.SwitchToScene(game.CompPlayer())
                AIScrabble.min_score = 10
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                self.SwitchToScene(HelpPage())
                self.needs_update = True

    def update(self):
        pass

    def titlePage(self, screen):
        # For the sake of brevity, the title scene is a white screen with text
        screen.fill((255, 255, 255))
        black = (0, 0, 0)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 56)

        # create a text surface object,
        # on which text is drawn on it.
        text = font.render('''Welcome to Scrabble!''', True, black)

        # create a rectangular object for the
        # text surface object
        text_rect = text.get_rect()
        text_rect.center = (screen.get_width() // 2, screen.get_height() // 2 - 200)
        screen.blit(text, text_rect)

        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render('''Press 'Enter' to start Single Player Mode''', True, black)
        text_rect2 = text2.get_rect()
        text_rect2.center = (screen.get_width() // 2, screen.get_height() // 2 - 100)
        screen.blit(text2, text_rect2)

        text3 = font2.render('''Press 'h' to visit the help page''', True, black)
        text_rect3 = text3.get_rect()
        text_rect3.center = (screen.get_width() // 2, screen.get_height() // 2)
        screen.blit(text3, text_rect3)

        text4 = font2.render('''Press '2' to start 2 player mode''', True, black)
        text_rect4 = text4.get_rect()
        text_rect4.center = (screen.get_width() // 2, screen.get_height() // 2 + 100)
        screen.blit(text4, text_rect4)

        text5 = font2.render('''Press 'C' to play against the computer''', True, black)
        text_rect5 = text5.get_rect()
        text_rect5.center = (screen.get_width() // 2, screen.get_height() // 2 + 200)
        screen.blit(text5, text_rect5)

        pygame.display.set_caption("Scrabble Menu")

        if self.show_difficulty_popup:  # render the popup if the flag is True
            self.choose_level(screen)

    def helpPage(self, screen):
        # For the sake of brevity, the help page is a white screen with text
        screen.fill((255, 255, 255))
        black = (0, 0, 0)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 32)

        # create a text surface object,
        # on which text is drawn on it.
        text = font.render('''This is a game of scrabble where your intelligence will be put to the test!.''', True, black)

        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()
        X = 400
        Y = 300
        # set the center of the rectangular object.
        textRect.center = (X, Y)
        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        screen.blit(text, textRect)

        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render('''Press 'SPACE' to start the game''', True, black)
        textRect2 = text.get_rect()
        textRect2.center = (X + 20, Y + 100)
        screen.blit(text2, textRect2)

    def choose_level(self, screen):
        # For the sake of brevity, the help page is a white screen with text
        screen.fill((255, 255, 255))
        black = (0, 0, 0)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 42)

        # create a text surface object,
        # on which text is drawn on it.
        text = font.render('''Choose your difficulty.''', True, black)

        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()
        textRect.center = (screen.get_width() // 2, screen.get_height() // 2 - 100)
        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        screen.blit(text, textRect)

        font2 = pygame.font.Font('freesansbold.ttf', 30)
        text2 = font2.render('''Press 'E' for easy mode or 'D' for Difficult mode''', True, black)
        textRect2 = text.get_rect()
        textRect2.center = (screen.get_width() // 2 - 100, screen.get_height() // 2)
        screen.blit(text2, textRect2)


def run_game(width, height, fps, starting_scene):  # only for starting scene
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True


            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.process_input(filtered_events, pressed_keys)
        active_scene.update()
        active_scene.titlePage(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)


run_game(800, 800, 30, StartPage())


