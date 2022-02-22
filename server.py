from flask import Flask
from flask_restful import Resource, Api, reqparse
import random
import json

GAME_SIZE = (800,600)
COLORS = ['0,255,0', '255,0,0', '0,0,255', '255,255,0']

app = Flask(__name__)
api = Api(app)

reverse_dict = {color: random.choice((False, True)) for color in COLORS}
start_pos_dict = {color: (random.randrange(0, GAME_SIZE[0]), random.randrange(0, GAME_SIZE[1])) for color in COLORS}
angle_dict = {color: 0 for color in COLORS}
players_list = random.sample(COLORS, 4)



class Initialize(Resource):
    player = 0
    def get(self):
        player_color = players_list[Initialize.player]
        Initialize.player += 1
        return json.dumps([players_list, start_pos_dict, angle_dict, reverse_dict, player_color])



class Degrees(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('myplayer', required=True)
        parser.add_argument('angle', required=True)

        args = parser.parse_args()

        angle_dict[args['myplayer']] = args['angle']

        return json.dumps(angle_dict)


api.add_resource(Initialize, '/setup')
api.add_resource(Degrees, '/running')

if __name__ == '__main__':
    app.run()
