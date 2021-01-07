from move import Move
# from pprint import pprint
from helper_classes import Map, Units

WORKER_TYPE = 'worker'
MELEE_TYPE = 'melee'

class GridPlayer:
    def __init__(self) -> None:
        self.safe_turns = 0

    def tick(self, game_map: Map, your_units: Units, enemy_units: Units,
             resources: int, turns_left: int) -> [Move]:

        return []