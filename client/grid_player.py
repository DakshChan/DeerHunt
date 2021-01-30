from helper_classes import *
import math
import random


class GridPlayer:

    def __init__(self):
        self.foo = True
        self.turns_taken = 0
        self.resource_reserve = 50
        self.min_melee = 2
        self.melee_hold_points = {}

    def tick(self, game_map: Map, your_units: Units, enemy_units: Units,
             resources: int, turns_left: int) -> [Move]:

        self.game_map = game_map
        self.your_units = your_units
        self.enemy_units = enemy_units
        self.resources = resources
        self.turns_left = turns_left

        self.moves = []

        print('resources', resources)

        self.workers = self.your_units.get_all_unit_of_type('worker')
        for w in self.workers:
            print(w.attr)

        self.melees = self.your_units.get_all_unit_of_type('melee')
        print("workers", len(self.workers), self.workers)
        print("melees", len(self.melees), self.melees)

        print('melee move')
        try:
            self.move_melees()
        except:
            pass

        print('worker move')
        try:
            self.optimize_worker_paths()
        except:
            pass

        self.turns_taken += 1
        print(turns_left)
        if self.turns_taken == 35:
            self.resource_reserve = 200


        if self.turns_taken == 50:
            self.min_melee += 2


        if self.turns_taken == 100:
            self.min_melee += 1


        return self.moves

    def optimize_worker_paths(self):

        available_to_move = []

        resources = self.game_map.find_all_resources()
        print(len(resources))
        worker_count = len(self.workers)
        print(worker_count)

        for worker in self.workers:
            if self.worker_busy(worker):
                print("busy")
                pass
            elif self.worker_in_danger(worker):
                print('danger')
                self.worker_danger_avoidance(worker)
            elif (worker_count < int(len(resources) * 0.75) or self.min_melee > len(self.melees)) and self.resources >= self.resource_reserve:
                print('spawn')
                if self.min_melee > len(self.melees) and self.resources >= 150:
                    self.worker_spawn(worker, 'melee')
                    self.resources -= 100
                elif worker_count < len(resources):
                    print(worker_count, resources)
                    self.worker_spawn(worker, 'worker')
                    worker_count += 1
                    self.resources -= 50
                else:
                    print('spawn melee')
                    self.worker_spawn(worker, 'melee')
                    self.resources -= 100

            elif self.game_map.is_resource(worker.x, worker.y):
                print('mine')
                self.moves.append(worker.mine())
            else:
                print('path')
                available_to_move.append(worker)

        print(len(resources))
        for worker in self.workers:
            if (worker.x, worker.y) in resources:
                resources.remove((worker.x, worker.y))
                print('worker ontop')
        print(len(resources))

        # node_work = zip(available_to_move, sorted(resources))
        # for worker, resource in node_work:
        #     self.moves.append(worker.move_towards(self.game_map.bfs((worker.x, worker.y), resource)[1]))

        for worker in available_to_move:
            min_x_y = ()
            min_dist = 9999999
            bfs_min_path = None
            for r in resources:
                blocks = self.bfs_blocks()
                if (worker.x, worker.y) in blocks:
                    blocks.remove((worker.x, worker.y))
                if r in blocks:
                    blocks.remove(r)
                bfs = self.better_bfs(self.game_map, (worker.x, worker.y), r,
                                      blocks)
                # print('bfs', bfs)
                if bfs is None:
                    continue

                if len(bfs) < min_dist:
                    min_dist = len(bfs)
                    min_x_y = r
                    bfs_min_path = bfs

            if min_x_y != ():
                resources.remove(min_x_y)

            if bfs_min_path:
                self.moves.append(worker.move_towards(bfs_min_path[1]))
                print(worker.x, worker.y, bfs_min_path[:2])

        # avg_dist = []
        # worker_dist = {}
        # for worker in available_to_move:
        #     move_dist = []
        #     sum_dist = 0
        #     for resource in resources:
        #         bfs_moves = self.game_map.bfs((worker.x, worker.y), resource)
        #         sum_dist += len(bfs_moves)
        #         move_dist.append((len(bfs_moves), bfs_moves, resource))
        #     move_dist.sort()
        #     worker_dist[worker.id] = move_dist
        #     move_dist = move_dist[:3]
        #     avg_dist.append((sum_dist / len(move_dist), worker))
        #
        # avg_dist.sort(reverse=True, key=lambda x: x[0])
        # for _, worker in avg_dist:
        #     for possible_moves in worker_dist[worker.id]:
        #         if possible_moves[2] in resources:
        #             print((worker.x, worker.y), possible_moves[1][1])
        #             print(possible_moves[1])
        #             self.moves.append(worker.move_towards(possible_moves[1][1]))
        #             resources.remove(possible_moves[2])
        #             break

    def move_melees(self):
        ids = self.your_units.get_all_unit_ids()
        dead = [x for x in self.melee_hold_points.keys() if str(x) not in ids]
        # print('debug')
        # print(ids)
        # print(dead)
        for i in dead:
            print('melee dead')
            self.melee_hold_points.pop(i)

        resources_held = []
        for val in self.melee_hold_points.values():
            resources_held.append(val)

        resources_free = [x for x in self.game_map.find_all_resources() if x not in resources_held]
        print('res free', resources_free)
        print('res held', resources_held)

        for melee in self.melees:
            if melee.id not in self.melee_hold_points.keys():
                # assign point
                max_x_y = ()
                max_dist = -1
                bfs_max_path = None

                for r in resources_free:
                    blocks = self.bfs_blocks(enemy=False)
                    if (melee.x, melee.y) in blocks:
                        blocks.remove((melee.x, melee.y))

                    bfs = self.better_bfs(self.game_map, (melee.x, melee.y), r,
                                          blocks)
                    # print('bfs', bfs)
                    if bfs is None:
                        continue

                    if len(bfs) > max_dist:
                        max_dist = len(bfs)
                        max_x_y = r
                        bfs_max_path = bfs

                if max_x_y != ():
                    resources_free.remove(max_x_y)

                if bfs_max_path:
                    self.moves.append(melee.move_towards(bfs_max_path[1]))
                    print(melee.x, melee.y, bfs_max_path[:2])

                if max_x_y != ():
                    self.melee_hold_points[melee.id] = max_x_y
                    print(max_x_y)

                pass
            if melee.id not in self.melee_hold_points.keys():
                continue
            point = self.melee_hold_points[melee.id]
            if point == ():
                continue
            print(point)
            print('dist', abs(melee.x - point[0]) + abs(melee.y - point[1]) > 2)
            t = melee.nearby_enemies_by_distance(self.enemy_units)

            if t and t[0][1] < 7:
                # enemy near
                enemy = self.enemy_units.get_unit(t[0][0])
                print('enemy near')
                q = melee.can_attack(self.enemy_units)
                if q:
                    self.moves.append(melee.attack(q[0][1]))
                    continue
                if t[0][1] == 2 and enemy.attr['type'] == 'melee' and enemy.attr['stun_status'] == 0:
                    b = melee.can_stun(self.enemy_units)
                    b = [x for x in b if x[0].attr['type'] == 'melee']
                    if b:
                        if self.resources >= 50:
                            self.resources -= 50
                            self.moves.append(melee.stun(b[0][1]))
                            print('stunned')
                            continue
                    pass

                blocks = self.bfs_blocks(enemy=False)
                if (melee.x, melee.y) in blocks:
                    blocks.remove((melee.x, melee.y))
                bfs = self.better_bfs(self.game_map, (melee.x, melee.y), (enemy.x, enemy.y), blocks)
                if bfs is None:
                    self.moves.append(melee.move(melee.direction_to((enemy.x, enemy.y))))
                else:
                    self.moves.append(melee.move(melee.direction_to(bfs[1])))

            elif (abs(melee.x - point[0]) + abs(melee.y - point[1]) > 2):
                # move towards point
                blocks = self.bfs_blocks(enemy=False)
                if (melee.x, melee.y) in blocks:
                    blocks.remove((melee.x, melee.y))
                if point in blocks:
                    blocks.remove(point)
                print('point', point, 'melee pos', (melee.x, melee.y))
                bfs = self.better_bfs(self.game_map, (melee.x, melee.y), point, [])
                if bfs is None:
                    print('bfs is none')
                    continue
                print(bfs[1])
                self.moves.append(melee.move(melee.direction_to(bfs[1])))
                # self.moves.append(melee.move_towards(point))
                pass
            else:
                if self.game_map.is_resource(melee.x, melee.y):
                    self.moves.append(melee.move(random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])))



    def mini_max(self, melee):
        pass

    def mini_max_localizer(self):
        pass

    def worker_danger_avoidance(self, worker):

        enemies = worker.nearby_enemies_by_distance(self.enemy_units)
        enemies = [self.enemy_units.get_unit(e[0]) for e in enemies]
        enemies = [e for e in enemies if e.attr['type'] == 'melee']
        enemy = enemies[0]
        dir = worker.direction_to((enemy.x, enemy.y))
        if dir == 'UP':
            dir = 'DOWN'
        elif dir == 'DOWN':
            dir = 'UP'
        elif dir == 'LEFT':
            dir = 'RIGHT'
        elif dir == 'RIGHT':
            dir = 'LEFT'
        self.moves.append(worker.move(dir))

    def bfs_blocks(self, enemy=True):
        if enemy:
            blocks = [(u.x, u.y) for u in (self.workers + self.melees
                                           + self.enemy_units.get_all_unit_of_type('worker')
                                           + self.enemy_units.get_all_unit_of_type('melee'))]
        else:
            blocks = [(u.x, u.y) for u in (self.workers + self.melees)]

        # print(blocks)
        for move in self.moves:
            unit, dir = move.to_tuple()
            # print(unit, dir)
            unit = self.your_units.get_unit(str(unit))
            if dir[0] in ['UP','DOWN','LEFT','RIGHT']:
                blocks.append(coordinate_from_direction(unit.x,unit.y,dir[0]))
                if (unit.x, unit.y) in blocks:
                    blocks.remove((unit.x, unit.y))
            if 'DUPLICATE' in dir[0]:
                blocks.append(coordinate_from_direction(unit.x,unit.y,dir[1]))

        # print(blocks)
        blocks = list(set(blocks))
        return blocks


    def worker_in_danger(self, worker) -> bool:
        enemies = worker.nearby_enemies_by_distance(self.enemy_units)
        enemies = [self.enemy_units.get_unit(e[0]) for e in enemies]
        enemies = [e for e in enemies if e.attr['type'] == 'melee']
        if enemies:
            enemy = enemies[0]
            enemy_moves = self.better_bfs(self.game_map, (enemy.x, enemy.y),
                                          (worker.x, worker.y), [])
            if enemy_moves is None:
                return False
            # if len(enemy_moves) <= worker.attr['mining_status'] + worker.attr['mining_status'] + worker.attr['stun_status'] + 1:
            if len(enemy_moves) <= 3:
                return True
        return False

    def worker_busy(self, worker) -> bool:
        attr = worker.attr
        if attr['mining_status'] > 0 or attr['duplication_status'] > 0 \
                or attr['stun_status'] > 0:
            return True
        return False

    def worker_spawn(self, worker, unit_type):
        dir = ''

        #     if direction == 'LEFT':
        #         return (x-1, y)
        # if direction == 'RIGHT':
        #     return (x+1, y)
        # if direction == 'UP':
        #     return (x, y-1)
        # if direction == 'DOWN':
        #     return (x, y+1)

        if self.is_empty(worker.x, worker.y - 1):
            dir = 'UP'
        elif self.is_empty(worker.x, worker.y + 1):
            dir = 'DOWN'
        elif self.is_empty(worker.x + 1, worker.y):
            dir = 'RIGHT'
        elif self.is_empty(worker.x - 1, worker.y):
            dir = 'LEFT'
        self.moves.append(worker.duplicate(dir, unit_type))

    def is_empty(self, x, y):
        # print('tile', self.game_map.get_tile(x, y))
        filled_pos = []
        filled_pos += [(unit.x, unit.y) for unit in
                       self.your_units.get_all_unit_of_type('melee')]
        filled_pos += [(unit.x, unit.y) for unit in
                       self.your_units.get_all_unit_of_type('worker')]
        filled_pos += [(unit.x, unit.y) for unit in
                       self.enemy_units.get_all_unit_of_type('melee')]
        filled_pos += [(unit.x, unit.y) for unit in
                       self.enemy_units.get_all_unit_of_type('worker')]
        if self.game_map.get_tile(x, y) == ' ' or self.game_map.get_tile(x, y) == 'R':
            if (x, y) not in filled_pos:
                return True
        return False

    def better_bfs(self, map, start: (int, int), dest: (int, int), blocks) -> [
        (int, int)]:
        """(Map, (int, int), (int, int)) -> [(int, int)]
        Finds the shortest path from <start> to <dest>.
        Returns a path with a list of coordinates starting with
        <start> to <dest>.
        """
        graph = map.grid
        queue = [[start]]
        vis = set(start)
        if start == dest or graph[start[1]][start[0]] == 'X' or \
                not (0 < start[0] < len(graph[0]) - 1
                     and 0 < start[1] < len(graph) - 1):
            return None

        while queue:
            path = queue.pop(0)
            node = path[-1]
            r = node[1]
            c = node[0]

            if node == dest:
                return path
            for adj in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                # print(adj[1], adj[0])
                # print('ocu', ((adj[0], adj[1]) in blocks))
                if ((graph[adj[1]][adj[0]] == ' ' or
                     graph[adj[1]][adj[0]] == 'R') and
                    ((adj[0], adj[1]) not in blocks)) and adj not in vis:
                    # print('if')
                    queue.append(path + [adj])
                    vis.add(adj)
