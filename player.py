from shapely.geometry import LineString
import math
import achtung_exceptions

DEFAULT_VEL = 2.5
GAME_SIZE = (600, 600)


class Player:
    def __init__(self, first_pos):
        self.pos_list = [(0, 0), first_pos]
        self.score = 0
        self.player_vel = DEFAULT_VEL

    def next_pos(self, ang, reverse, players):
        slope = self.get_slope(self.pos_list[-1], self.pos_list[-2])
        if slope > 0:
            new_slope_ang = ang + math.degrees(math.atan(slope))
        else:
            new_slope_ang = ang + (math.degrees(math.atan(slope)) + 180)
        if new_slope_ang == 90:     # this section is meant to insure that at no point is the player perpendicular to x
            if ang > 0:
                new_slope_ang = 89.5
            else:
                new_slope_ang = 90.5

        new_slope = math.tan(math.radians(new_slope_ang))
        if (ang > 0 and slope > 0 and new_slope < 0) or (ang < 0 and slope < 0 and new_slope > 0):
            reverse = not reverse
        if reverse:
            x_change = - self.player_vel / math.sqrt(1 + math.pow(new_slope, 2))
        else:
            x_change = self.player_vel / math.sqrt(1 + math.pow(new_slope, 2))
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
                if self.intersects(player.pos_list[i], player.pos_list[i + 1], self.pos_list[-1], new_pos):
                    self.pos_list.append(self.get_intersection_point((player.pos_list[i], player.pos_list[i + 1]),
                                                                     (self.pos_list[-1], new_pos)))
                    return False
        for axis in (0, 1):
            if new_pos[axis] <= 0 or new_pos[axis] >= GAME_SIZE[axis]:
                self.pos_list.append(new_pos)
                return False
        return True

    def get_pos_list(self):
        return self.pos_list

    def get_head(self):
        return self.pos_list[-1]

    def reset(self, first_pos):
        self.pos_list = [(0, 0), first_pos]

    @staticmethod
    def get_slope(pos1, pos2):
        return (pos1[1] - pos2[1]) / (pos1[0] - pos2[0])

    @staticmethod
    def intersects(A, B, C, D):
        line = LineString([A, B])
        other = LineString([C, D])
        return line.intersects(other)

    @staticmethod
    def get_intersection_point(line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y
