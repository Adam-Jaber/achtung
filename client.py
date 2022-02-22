import pygame
import requests
import json
from player import Player
import achtung_exceptions


setup_list = json.loads(requests.get('http://127.0.0.1:5000/setup').json())
print(setup_list)
print((setup_list[1]))
print(type(setup_list[1]))
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
        return -0.3
    elif keys[pygame.K_RIGHT]:
        return 0.3
    else:
        return 0




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((200,200,200))

    game_surface = pygame.Surface(GAME_SIZE)
    game_surface.fill((0,0,0))

    new_angle = check_rotation(my_player)
    angle_dict = json.loads(requests.post(f'http://127.0.0.1:5000/running?myplayer={my_player}&angle={new_angle}').json())

    for player_color in players_list:
        if player_color not in lost_players:
            try:
                reverse_dict[player_color] = players_dict[player_color].next_pos(angle_dict[player_color], reverse_dict[player_color], players_dict.values())
            except achtung_exceptions.CollisionError:
                lost_players.append(player_color)
        pygame.draw.lines(screen, get_color(player_color), False, players_dict[player_color].get_pos_list()[1:])
    pygame.display.update()
