import time
import _thread
import pygame
import os

def get_enemy_list(player, players_dict):
    return [enemy for enemy in players_dict.values() if enemy != player]


def get_speed_powerup(*args):
    player = args[0]
    player.player_vel *= 1.5
    time.sleep(9)
    player.player_vel /= 1.5


def inflict_speed_powerup(*args):
    player, players_dict = args[0], args[1]
    for enemy in get_enemy_list(player, players_dict):
        _thread.start_new_thread(get_speed_powerup, (enemy, ))


def get_slow_powerup(*args):
    player = args[0]
    player.player_vel /= 1.5
    time.sleep(9)
    player.player_vel *= 1.5


def inflict_slow_powerup(*args):
    player, players_dict = args[0], args[1]
    for enemy in get_enemy_list(player, players_dict):
        _thread.start_new_thread(get_slow_powerup, (enemy, ))


def get_switch_binds(*args):
    args[0], args[1] = args[1], args[0]
    time.sleep(9)
    args[0], args[1] = args[1], args[0]


POWER_UPS_DICT = {'speedself': get_speed_powerup, 'speedrest': inflict_speed_powerup,
                  'slowself': get_slow_powerup, 'slowrest': inflict_slow_powerup}

location = os.path.dirname(__file__)
POWER_UPS_IMAGES = {powerup: pygame.image.load(f'{location}/{powerup}.png') for powerup in POWER_UPS_DICT}
