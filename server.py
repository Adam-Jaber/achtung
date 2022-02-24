from flask import Flask
from flask_restful import Resource, Api, reqparse
import random
import json

GAME_SIZE = (600, 600)
COLORS = ['0,255,0', '255,0,0', '0,0,255', '255,255,0']

app = Flask(__name__)
api = Api(app)

reverse_dict = {color: random.choice((False, True)) for color in COLORS}
start_pos_dict = {color: (random.randrange(0, GAME_SIZE[0]), random.randrange(0, GAME_SIZE[1])) for color in COLORS}
angle_dict = {color: 0 for color in COLORS}
players_list = random.sample(COLORS, 4)

ready_dict = {color: False for color in COLORS}



class Initialize(Resource):
    player = 0
    def get(self):
        player_color = players_list[Initialize.player]
        Initialize.player += 1
        return json.dumps([players_list, start_pos_dict, angle_dict, reverse_dict, player_color])


class Connect(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('myplayer', required=True)
        args = parser.parse_args()

        ready_dict[args['myplayer']] = not ready_dict[args['myplayer']]

    def get(self):
        is_ready = True
        for bool_ in ready_dict.values():
            if bool_ is False:
                is_ready = False

        return json.dumps(is_ready)

class Degrees(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('myplayer', required=True)
        parser.add_argument('angle', required=True)

        args = parser.parse_args()

        angle_dict[args['myplayer']] = float(args['angle'])

        return json.dumps(angle_dict)

class Reset(Resource):
    call_num = 0
    def get(self):
        Reset.call_num += 1
        if Reset.call_num % 4 == 0:
            global reverse_dict, start_pos_dict, ready_dict

            start_pos_dict = {color: (random.randrange(0, GAME_SIZE[0]), random.randrange(0, GAME_SIZE[1]))
                              for color in COLORS}
            reverse_dict = {color: random.choice((False, True)) for color in COLORS}

        return json.dumps([start_pos_dict, reverse_dict])


api.add_resource(Initialize, '/setup')
api.add_resource(Degrees, '/running')
api.add_resource(Connect, '/ready')
api.add_resource(Reset, '/reset')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
