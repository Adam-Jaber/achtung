import time

def get_enemy_list(player, players_dict):
    return [enemy for enemy in players_dict.values() if enemy != player]

def get_speed_powerup(player):
    player.player_vel *= 1.5
    time.sleep(5)
    player.player_vel /= 1.5

def inflict_speed_powerup(player, players_dict):
    for enemy in get_enemy_list(player, players_dict):
        get_speed_powerup(enemy)

def get_slow_powerup(player):
    player.player_vel /= 1.5
    time.sleep(5)
    player.player_vel *= 1.5

def inflict_slow_powerup(player, players_dict):
    for enemy in get_enemy_list(player, players_dict):
        get_slow_powerup(enemy)