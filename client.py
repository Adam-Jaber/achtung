import pygame
import random
import _thread
from player import Player
import achtung_exceptions

#get this dicts, player_list and your player from server
reverse_dict = {(0,255,0): False}
start_pos_dict = {(0,255,0):(200,200)}
angle_dict = {(0,255,0): 50}
players_list = [(0,255,0)]
my_player = (0,255,0)


SCREEN_SIZE = (800, 600)
GAME_SIZE = (600,600)
PLAYER_VEL = 5


players_dict = dict()
for player_color in players_list:
    players_dict[player_color] = Player(start_pos_dict[player_color])

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)

lost_players = []

def check_rotation(player_color):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle_dict[player_color] = -0.3
    elif keys[pygame.K_RIGHT]:
        angle_dict[player_color] = 0.3
    else:
        angle_dict[player_color] = 0




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((200,200,200))

    game_surface = pygame.Surface(GAME_SIZE)
    game_surface.fill((0,0,0))

    check_rotation(my_player)

    for player_color in players_list:
        if player_color not in lost_players:
            try:
                reverse_dict[player_color] = players_dict[player_color].next_pos(angle_dict[player_color], reverse_dict[player_color], players_dict.values())
            except achtung_exceptions.CollisionError:
                lost_players.append(player_color)
        pygame.draw.lines(screen, player_color, False, players_dict[player_color].get_pos_list()[1:])
    pygame.display.update()
