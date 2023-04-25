import pygame
import gamestate as gs
import resourceFile
import TwoPlayerMode


class ScrabbleGame:
    def __init__(self):
        pygame.init()

        self.resourceManagement = resourceFile.ResourceManager()

    def play(self, ai):  # Manages game states

        # Constants
        SIZE = (1000, 800)

        # Variables
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()
        running = True
        currentState = gs.GameState(self.resourceManagement, ai)  # reference to the GameState class

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

        pygame.QUIT

    def TwoPlayer(self, ai):  # Manages game states

        # Constants
        SIZE = (1000, 800)

        # Variables
        screen = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()
        running = True
        currentState = TwoPlayerMode.TwoPlayerGame(self.resourceManagement, ai)  # reference to the GameState class

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

        pygame.QUIT


game = ScrabbleGame()


class SceneBase:
    def __init__(self):
        self.next = self

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)


class StartPage(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def process_input(self, events, pressed_keys):
        self.needs_update = False
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(game.play(False))
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(game.TwoPlayer(False))
                self.needs_update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                print("You have chosen help")

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
        font = pygame.font.Font('freesansbold.ttf', 32)

        # create a text surface object,
        # on which text is drawn on it.
        text = font.render('''Welcome to Scrabble!''', True, black)

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
        text2 = font2.render('''Press 'Enter' to start Single Player Mode''', True, black)
        textRect2 = text.get_rect()
        textRect2.center = (X - 10, Y + 100)
        screen.blit(text2, textRect2)

        font3 = pygame.font.Font('freesansbold.ttf', 17)
        text3 = font3.render('''Press 'h' to visit the help page''', True, black)
        textRect3 = text.get_rect()
        textRect3.center = (X + 55, Y + 250)
        screen.blit(text3, textRect3)

        font4 = pygame.font.Font('freesansbold.ttf', 20)
        text4 = font4.render('''Press '2' to start 2 player mode''', True, black)
        textRect4 = text.get_rect()
        textRect4.center = (X + 20, Y + 150)
        screen.blit(text4, textRect4)

        pygame.display.set_caption("Scrabble Menu")

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


