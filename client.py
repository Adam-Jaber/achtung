import pygame
import requests
import json
import _thread
from player import Player
import achtung_exceptions
from power_ups import *


HOST_ADRESS = 'http://10.0.0.15:5000'

setup_list = json.loads(requests.get(f'{HOST_ADRESS}/setup').json())
#get this dicts, player_list and your player from server
players_list = setup_list[0]
start_pos_dict = setup_list[1]
angle_dict = setup_list[2]
reverse_dict = setup_list[3]
my_player = setup_list[4]


SCREEN_SIZE = (800, 600)
GAME_SIZE = (600, 600)


players_dict = dict()
for player_color in players_list:
    players_dict[player_color] = Player(start_pos_dict[player_color])

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
game_surface = pygame.Surface(GAME_SIZE)

lost_players = []

def get_color(str):
    return tuple((int(i) for i in str.split(',')))


def check_rotation(player_color):
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


# initialize waiting loop's parameters
header_font = pygame.font.Font('freesansbold.ttf', 32)
text = header_font.render('Please enter your name', True, (200, 200, 200), (50, 50, 50))

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
done = False
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
                    requests.post(f'{HOST_ADRESS}/ready?myplayer={my_player}')
                    requests.post(f'{HOST_ADRESS}/names?player={my_player}&name={input_text}')

                    ready = not ready
                    if not ready:
                        text = header_font.render('Please enter your name', True,
                                                  (200, 200, 200), (50, 50, 50))
                    else:
                        text = header_font.render('Waiting for all players to ready up', True, (200, 200, 200),
                                                  (50, 50, 50))
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

    screen.fill((50,50,50))
    screen.blit(text, textRect)
    if not ready:
        input_txt_surface = header_font.render(input_text, True, (200, 200, 200), (50, 50, 50))
        input_box.w = max(200, input_txt_surface.get_width() + 10)
        screen.blit(input_txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, input_color, input_box, 2)
    pygame.display.update()

    game_ready = json.loads(requests.get(f'{HOST_ADRESS}/ready').json())
    if game_ready:
        waiting = False


score_font = pygame.font.Font('freesansbold.ttf', 12)
name_dict = json.loads(requests.get(f'{HOST_ADRESS}/names').json())


def round():
    """ this function represents a single frame in a round of the game"""
    screen.fill((200, 200, 200))
    screen.blit(game_surface, (0, 0))
    game_surface.fill((0, 0, 0))

    # get players angle send to server and wait for server to return all players angles when synchronized
    new_angle = check_rotation(my_player)
    requests.post(f'{HOST_ADRESS}/running?myplayer={my_player}&angle={new_angle}')
    while True:
        try:
            angle_dict = json.loads(requests.get(f'{HOST_ADRESS}/running?myplayer={my_player}').json())
            if type(angle_dict) is dict:
                break
        except:
            pass
    # render to screen all players, if players still alive generate their next position.
    for player_color in players_list:
        if player_color not in lost_players:
            try:
                reverse_dict[player_color] = players_dict[player_color].next_pos(angle_dict[player_color],
                                                                                 reverse_dict[player_color],
                                                                                 players_dict.values())
            except achtung_exceptions.CollisionError:
                lost_players.append(player_color)
                for player in [player for player in players_list if player not in lost_players]:
                    players_dict[player].score += 1 # if a player dies increment others score

        pygame.draw.aalines(game_surface, get_color(player_color), False, players_dict[player_color].get_pos_list()[1:])

        # this portion handles rendering a scoreboard for the player
        score_text = score_font.render(f'{name_dict[player_color]}: {players_dict[player_color].score}', True, (255, 255, 255),
                                       (200, 200, 200))
        score_Rect = text.get_rect()
        score_Rect.center = (975, (SCREEN_SIZE[1] // 6) * (players_list.index(player_color) + 1))
        screen.blit(score_text, score_Rect)

    # get active powerup from server and render it to screen, if a colision accours activate.
    powerup_list = json.loads(requests.get(f"{HOST_ADRESS}/activepower").json())
    for powerup, pos in powerup_list:
        game_surface.blit(POWER_UPS_IMAGES[powerup], pos)
        head_x, head_y = players_dict[my_player].get_head()
        if pos[0] <= head_x <= pos[0] + 40 and pos[1] <= head_y <= pos[1] + 40:
            requests.post(f'{HOST_ADRESS}/activepower')
            use_powerup(powerup)

    pygame.display.update()


def restart():
    """reset basic parameters of the game"""
    global start_pos_dict, reverse_dict
    start_pos_dict, reverse_dict = json.loads(requests.get(f"{HOST_ADRESS}/reset").json())
    lost_players.clear()
    for player in players_dict:
        players_dict[player].reset(start_pos_dict[player])


def won(player):
    """render winning screen
    player: str = 'int,int,int'
    """
    screen.fill((0, 0, 0))

    win_text = header_font.render(f'{name_dict[player]} WON!', True, (255, 255, 255), (0, 0, 0))
    win_rect = win_text.get_rect()
    win_rect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
    screen.blit(win_text, win_rect)

    pygame.display.update()

def handle_powerups(player_):
    """activate player's active powerups - run powerup in parallel to the game
    player_: str = 'int,int,int'
    """
    power_ups_list = requests.get(f'{HOST_ADRESS}/powerups?player={player_}').json()
    for powerup, user in power_ups_list:
        _thread.start_new_thread(POWER_UPS_DICT[powerup], (players_dict[user], players_dict))

def use_powerup(powerup):
    """post to server using a powerup
    powerup: str from server.POWER_UPs_LIST
    """
    requests.post(f'{HOST_ADRESS}/powerups?powerup={powerup}&player={my_player}')

# main game loop
win_screen = False
winner = None
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                use_powerup('speedself')
            if event.key == pygame.K_DOWN:
                use_powerup('speedrest')

    handle_powerups(my_player)

    if len(lost_players) == 3:
        restart()

    if not win_screen:
        round()
    else:
        won(winner)

    for player in players_list:
        if players_dict[player].score >= 25:
            winner = player
            win_screen = True