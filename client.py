import math

import pygame
import requests
import json
import _thread
from player import Player
import achtung_exceptions
from power_ups import POWER_UPS_DICT, POWER_UPS_IMAGES
SCREEN_SIZE = (800, 600)
GAME_SIZE = (600, 600)

class Game_client:

    def __init__(self, host, screen):
        self.screen = screen
        self.host = host
        self.game_surface = pygame.Surface(GAME_SIZE)

        self.score_font = pygame.font.Font('freesansbold.ttf', 12)
        self.header_font = pygame.font.Font('freesansbold.ttf', 32)

        self.setup()
        self.wait_for_game()
        self.name_dict = json.loads(requests.get(f'{self.host}/names').json())


        self.main_loop()


    def setup(self):
        setup_list = json.loads(requests.get(f'{self.host}/setup').json())
        # get this dicts, player_list and your player from server
        self.players_list = setup_list[0]
        self.start_pos_dict = setup_list[1]
        self.angle_dict = setup_list[2]
        self.reverse_dict = setup_list[3]
        self.my_player = setup_list[4]

        # create and store a player object for each of the players
        self.players_dict = dict()
        for player_color in self.players_list:
            self.players_dict[player_color] = Player(self.start_pos_dict[player_color])
        self.lost_players = []

    @staticmethod
    def get_color(str_):
        return tuple((int(i) for i in str_.split(',')))

    @staticmethod
    def check_rotation():
        """get the player's angle for the frame
        player_color: str = 'int,int,int'
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return -3.5
        elif keys[pygame.K_RIGHT]:
            return 3.5
        else:
            return 0

    def wait_for_game(self):
        # initialize waiting loop's parameters

        text = self.header_font.render('Please enter your name', True, (200, 200, 200), (50, 50, 50))

        textRect = text.get_rect()
        textRect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

        ready = False
        waiting = True

        input_box = pygame.Rect(SCREEN_SIZE[0]//2 - 100, SCREEN_SIZE[1]//2 + 100, 140, 32)
        color_inactive = pygame.Color(255, 255, 255)
        color_active = pygame.Color('dodgerblue2')
        input_color = color_inactive
        active = False
        input_text = ''
        # game setup loop - wait for all players to report ready to the server
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    # Change the current color of the input box.
                    input_color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:  # add typed characters to the input box (except of a backspace)
                        if event.key == pygame.K_RETURN:
                            requests.post(f'{self.host}/ready?myplayer={self.my_player}')
                            requests.post(f'{self.host}/names?player={self.my_player}&name={input_text}')

                            ready = not ready
                            if not ready:
                                text = self.header_font.render('Please enter your name', True,
                                                          (200, 200, 200), (50, 50, 50))
                            else:
                                text = self.header_font.render('Waiting for all players to ready up', True, (200, 200, 200),
                                                          (50, 50, 50))
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode

            self.screen.fill((50,50,50))
            self.screen.blit(text, textRect)
            if not ready:
                input_txt_surface = self.header_font.render(input_text, True, (200, 200, 200), (50, 50, 50))
                input_box.w = max(200, input_txt_surface.get_width() + 10)
                self.screen.blit(input_txt_surface, (input_box.x+5, input_box.y+5))
                pygame.draw.rect(self.screen, input_color, input_box, 2)
            pygame.display.update()

            game_ready = json.loads(requests.get(f'{self.host}/ready').json())
            if game_ready:
                waiting = False

    def round(self):
        """ this function represents a single frame in a round of the game"""
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.game_surface, (0, 0))
        self.game_surface.fill((0, 0, 0))

        # get players angle send to server and wait for server to return all players angles when synchronized
        new_angle = self.check_rotation()
        requests.post(f'{self.host}/running?myplayer={self.my_player}&angle={new_angle}')
        while True:
            self.angle_dict = json.loads(requests.get(f'{self.host}/running?myplayer={self.my_player}').json())
            if type(self.angle_dict) is dict:
                break
        # render to screen all players, if players still alive generate their next position.
        for player_color in self.players_list:
            if player_color not in self.lost_players:
                try:
                    self.reverse_dict[player_color] = self.players_dict[player_color].next_pos(self.angle_dict[player_color],
                                                                                               self.reverse_dict[player_color],
                                                                                               self.players_dict.values())
                except achtung_exceptions.CollisionError:
                    self.lost_players.append(player_color)
                    for player in [player for player in self.players_list if player not in self.lost_players]:
                        self.players_dict[player].score += 1     # if a player dies increment others score

            pygame.draw.aalines(self.game_surface, self.get_color(player_color), False, self.players_dict[player_color].get_pos_list()[1:])

            # this portion handles rendering a scoreboard for the player
            score_text = self.score_font.render(f'{self.name_dict[player_color]}: {self.players_dict[player_color].score}', True, (255, 255, 255),
                                           (200, 200, 200))
            score_Rect = score_text.get_rect()
            score_Rect.center = (700, (SCREEN_SIZE[1] // 6) * (self.players_list.index(player_color) + 1))
            self.screen.blit(score_text, score_Rect)

        # get active powerup from server and render it to screen, if a colision accours activate.
        powerup_list = json.loads(requests.get(f"{self.host}/activepower").json())
        for powerup, pos in powerup_list:
            self.game_surface.blit(POWER_UPS_IMAGES[powerup], pos)
            head_x, head_y = self.players_dict[self.my_player].get_head()
            # check for collision of player with powerup
            if math.sqrt((pos[0] + 20 - head_x)**2 + (pos[1] + 20 - head_y)**2) <= 20:
                requests.post(f'{self.host}/activepower')
                self.use_powerup(powerup)

        pygame.display.update()


    def restart(self):
        """reset basic parameters of the game"""
        self.start_pos_dict, self.reverse_dict = json.loads(requests.get(f"{self.host}/reset").json())
        self.lost_players.clear()
        for player in self.players_dict:
            self.players_dict[player].reset(self.start_pos_dict[player])


    def won(self, player):
        """render winning screen
        player: str = 'int,int,int'
        """
        self.screen.fill((0, 0, 0))

        win_text = self.header_font.render(f'{self.name_dict[player]} WON!', True, (255, 255, 255), (0, 0, 0))
        win_rect = win_text.get_rect()
        win_rect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        self.screen.blit(win_text, win_rect)

        pygame.display.update()

    def handle_powerups(self):
        """activate player's active powerups - run powerup in parallel to the game
        player_: str = 'int,int,int'
        """
        power_ups_list = requests.get(f'{self.host}/powerups?player={self.my_player}').json()
        for powerup, user in power_ups_list:
            _thread.start_new_thread(POWER_UPS_DICT[powerup], (self.players_dict[user], self.players_dict))

    def use_powerup(self, powerup):
        """post to server using a powerup
        powerup: str from server.POWER_UPs_LIST
        """
        requests.post(f'{self.host}/powerups?powerup={powerup}&player={self.my_player}')

    def main_loop(self):
        # main game loop
        win_screen = False
        winner = None
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

            self.handle_powerups()

            if len(self.lost_players) == 3:
                self.restart()

            if not win_screen:
                self.round()
            else:
                self.won(winner)

            for player in self.players_list:
                if self.players_dict[player].score >= 25:
                    winner = player
                    win_screen = True
