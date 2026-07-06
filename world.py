import random
from maps import hospital, warehouse, office, maze, factory
from config import *
from astar import astar


class GridWorld:

    def __init__(self):

        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT

        self.grid = []

        self.dynamic_obstacles = set()

        # fixed start/goal (used if no preset map)
        self.start = (1, 1)
        self.goal = (self.width - 2, self.height - 2)

        self.generate_random_map()

    # -----------------------------
    # INIT GRID
    # -----------------------------
    def _init_grid(self):

        self.grid = [
            [0 for _ in range(self.width)]
            for _ in range(self.height)
        ]

    # -----------------------------
    # WALLS
    # -----------------------------
    def _build_walls(self):

        for x in range(self.width):
            self.grid[0][x] = 1
            self.grid[self.height - 1][x] = 1

        for y in range(self.height):
            self.grid[y][0] = 1
            self.grid[y][self.width - 1] = 1

    # -----------------------------
    # RANDOM POINT
    # -----------------------------
    def _random_point(self):

        return (
            random.randint(1, self.width - 2),
            random.randint(1, self.height - 2)
        )

    # -----------------------------
    # DISTANCE CHECK
    # -----------------------------
    def _valid_distance(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1]) >= 15

    # -----------------------------
    # START / GOAL GENERATION
    # -----------------------------
    def _set_start_goal(self):

        while True:

            self.start = self._random_point()
            self.goal = self._random_point()

            if self._valid_distance(self.start, self.goal):
                break

    # -----------------------------
    # RANDOM OBSTACLES
    # -----------------------------
    def _add_obstacles(self, count=120):

        for _ in range(count):

            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            if (x, y) == self.start or (x, y) == self.goal:
                continue

            self.grid[y][x] = 1

    # -----------------------------
    # GENERATE RANDOM MAP
    # -----------------------------
    def generate_random_map(self):

        while True:

            self._init_grid()
            self.dynamic_obstacles.clear()

            self._build_walls()
            self._set_start_goal()
            self._add_obstacles()

            path, _ = astar(self, self.start, self.goal)

            if len(path) > 0:
                break

    # -----------------------------
    # CHECK BLOCK
    # -----------------------------
    def is_blocked(self, x, y):

        return self.grid[y][x] == 1

    # -----------------------------
    # TOGGLE OBSTACLE
    # -----------------------------
    def toggle_obstacle(self, x, y):

        if (x, y) == self.start or (x, y) == self.goal:
            return

        self.grid[y][x] ^= 1

        if self.grid[y][x] == 1:
            self.dynamic_obstacles.add((x, y))
        else:
            self.dynamic_obstacles.discard((x, y))

    # -----------------------------
    # CLEAR DYNAMIC OBSTACLES
    # -----------------------------
    def clear_dynamic(self):

        for x, y in list(self.dynamic_obstacles):
            self.grid[y][x] = 0

        self.dynamic_obstacles.clear()

    # -----------------------------
    # LOAD PRESET MAP (FIXED SAFE VERSION)
    # -----------------------------
    def load_map(self, map_name):

        map_dict = {
            "hospital": hospital,
            "warehouse": warehouse,
            "office": office,
            "maze": maze,
            "factory": factory
        }

        if map_name not in map_dict:
            print("Invalid map:", map_name)
            return

        try:
            data = map_dict[map_name]()
        except Exception as e:
            print("Map function failed:", map_name, e)
            return

        self.start = data["start"]
        self.goal = data["goal"]

        self.grid = [
            [0 for _ in range(self.width)]
            for _ in range(self.height)
        ]

        self.dynamic_obstacles.clear()

        self._build_walls()

        for x, y in data["obstacles"]:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = 1








