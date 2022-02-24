import math
import achtung_exceptions

PLAYER_VEL = 1
GAME_SIZE = (800, 600)

class Player:
    def __init__(self, first_pos):
        self.pos_list = [(0, 0), first_pos]

    def next_pos(self, ang, reverse, players):
        slope = self.get_slope(self.pos_list[-1], self.pos_list[-2])
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
        if self.check_new_pos(new_pos, players) is False:
            raise achtung_exceptions.CollisionError
        self.pos_list.append(new_pos)
        return reverse

    def check_new_pos(self, new_pos, players):
        for player in list(players):
            for i in range(1, len(player.pos_list) - 2):
                if self.intersect(player.pos_list[i], player.pos_list[i+1], self.pos_list[-1], new_pos):
                    return False
        for axis in (0, 1):
            if new_pos[axis] <= 0 or new_pos[axis] >= GAME_SIZE[axis]:
                return False
        return True

    def get_pos_list(self):
        return self.pos_list

    @staticmethod
    def get_slope(pos1, pos2):
        return (pos1[1] - pos2[1]) / (pos1[0] - pos2[0])

    @staticmethod
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    @staticmethod
    def intersect(A, B, C, D):
        return Player.ccw(A, C, D) != Player.ccw(B, C, D) and Player.ccw(A, B, C) != Player.ccw(A, B, D)