import math

PLAYER_VEL = 0.1
GAME_SIZE = (800, 600)

class Player:
    def __init__(self, first_pos):
        self.pos_list = [(0,0),first_pos]

    def next_pos(self, ang, reverse):
        slope = (self.pos_list[-1][1] - self.pos_list[-2][1]) / (self.pos_list[-1][0] - self.pos_list[-2][0])
        if slope > 0:
            new_slope_ang = ang + math.degrees(math.atan(slope))
        else:
            new_slope_ang = ang + (math.degrees(math.atan(slope)) + 180)
        new_slope = math.tan(math.radians(new_slope_ang))
        if (ang > 0 and slope > 0 and new_slope < 0) or (ang < 0 and slope < 0 and new_slope > 0):
            reverse = not reverse
        if reverse:
            x_change = - PLAYER_VEL / math.sqrt(1 + math.pow(new_slope, 2))
        else:
            x_change = PLAYER_VEL / math.sqrt(1 + math.pow(new_slope, 2))
        new_x = self.pos_list[-1][0] + x_change
        new_y = self.pos_list[-1][1] + new_slope * x_change
        new_pos = (new_x, new_y)
        self.pos_list.append(new_pos)
        return reverse

    def check_new_pos(self, new_pos, players_dict):
        for player in players_dict:
            if new_pos in player.pos_list:
                return False
        for axis in (0, 1):
            if new_pos[axis] <= 0 or new_pos[axis] >= GAME_SIZE[axis]:
                return False
        return True

    def get_pos_list(self):
        return  self.pos_list

