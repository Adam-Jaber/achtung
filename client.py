import pygame
import requests
import json
from player import Player
import achtung_exceptions


HOST_ADRESS = 'http://192.168.28.1:5000'

setup_list = json.loads(requests.get(f'{HOST_ADRESS}/setup').json())
#get this dicts, player_list and your player from server
players_list = setup_list[0]
start_pos_dict = setup_list[1]
angle_dict = setup_list[2]
reverse_dict = setup_list[3]
my_player = setup_list[4]


SCREEN_SIZE = (800, 600)
GAME_SIZE = (600,600)


players_dict = dict()
for player_color in players_list:
    players_dict[player_color] = Player(start_pos_dict[player_color])

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)

lost_players = []

def get_color(str):
    return tuple((int(i) for i in str.split(',')))


def check_rotation(player_color):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        return -1.5
    elif keys[pygame.K_RIGHT]:
        return 1.5
    else:
        return 0

font = pygame.font.Font('freesansbold.ttf', 32)
text = font.render('Waiting for all players to ready up', True, (200, 200, 200), (100, 100, 100))

textRect = text.get_rect()
textRect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

ready = False
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                requests.post(f'{HOST_ADRESS}/ready?myplayer={my_player}')
                if not ready:
                    text = font.render('Waiting for the rest of the players to ready up', True, (200, 200, 200), (100, 100, 100))
                else:
                    text = font.render('Waiting for all players to ready up', True, (200, 200, 200), (100, 100, 100))
                ready = not ready
    screen.fill((100,100,100))
    screen.blit(text, textRect)
    pygame.display.update()

    game_ready = json.loads(requests.get(f'{HOST_ADRESS}/ready').json())
    if game_ready:
        waiting = False



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    screen.fill((200,200,200))

    game_surface = pygame.Surface(GAME_SIZE)
    game_surface.fill((0,0,0))

    new_angle = check_rotation(my_player)
    angle_dict = json.loads(requests.post(f'{HOST_ADRESS}/running?myplayer={my_player}&angle={new_angle}').json())

    for player_color in players_list:
        if player_color not in lost_players:
            try:
                reverse_dict[player_color] = players_dict[player_color].next_pos(angle_dict[player_color], reverse_dict[player_color], players_dict.values())
            except achtung_exceptions.CollisionError:
                lost_players.append(player_color)
        pygame.draw.lines(screen, get_color(player_color), False, players_dict[player_color].get_pos_list()[1:])
    pygame.display.update()
