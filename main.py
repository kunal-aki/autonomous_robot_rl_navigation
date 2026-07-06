import pygame
import sys
import time
import random
from collections import deque

from config import *
from world import GridWorld
from robot import Robot
from astar import astar
from memory.qlearning import QLearningMemory


# -----------------------------
# MAP MEMORY
# -----------------------------
map_memory = {
    "hospital": {"best_time": float("inf"), "best_path": float("inf"), "runs": 0},
    "warehouse": {"best_time": float("inf"), "best_path": float("inf"), "runs": 0},
    "office": {"best_time": float("inf"), "best_path": float("inf"), "runs": 0},
    "maze": {"best_time": float("inf"), "best_path": float("inf"), "runs": 0},
    "factory": {"best_time": float("inf"), "best_path": float("inf"), "runs": 0},
}

current_map_name = "custom"


# -----------------------------
# PERSISTENT POLICY MEMORY
# -----------------------------
map_policy_memory = {}


def get_map_key(world):
    return str(world.grid)


def update_map_memory(name, runtime, path_length):
    if name in map_memory:
        m = map_memory[name]
        m["runs"] += 1
        m["best_time"] = min(m["best_time"], runtime)
        m["best_path"] = min(m["best_path"], path_length)


# -----------------------------
# VALIDATE STORED PATH
# -----------------------------
def path_is_valid(world, path):
    if path is None:
        return False

    for x, y in path:
        if world.is_blocked(x, y):
            return False

    return True


# -----------------------------
# DRAW FUNCTION
# -----------------------------
def draw(screen, world, robot, font,
         runtime, goal_reached,
         nodes, heatmap):

    screen.fill(WHITE)

    # ---------------------------------
    # DRAW GRID + HEATMAP
    # ---------------------------------
    for y in range(world.height):
        for x in range(world.width):

            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            heat = min(heatmap[y][x], 25)

            if heat > 0:
                intensity = int((heat / 25) * 255)
                color = (
                    255,
                    255 - intensity,
                    255 - intensity
                )

                pygame.draw.rect(
                    screen,
                    color,
                    rect
                )

            if world.grid[y][x] == 1:
                pygame.draw.rect(
                    screen,
                    BLACK,
                    rect
                )

            pygame.draw.rect(
                screen,
                GRAY,
                rect,
                1
            )

    # ---------------------------------
    # START / GOAL
    # ---------------------------------
    sx, sy = world.start
    gx, gy = world.goal

    pygame.draw.rect(
        screen,
        GREEN,
        (
            sx * CELL_SIZE,
            sy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

    pygame.draw.rect(
        screen,
        RED,
        (
            gx * CELL_SIZE,
            gy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

    # ---------------------------------
    # ROBOT
    # ---------------------------------
    pygame.draw.rect(
        screen,
        BLUE,
        (
            robot.x * CELL_SIZE,
            robot.y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

    # ---------------------------------
    # SIDEBAR
    # ---------------------------------
    sidebar_x = GRID_WIDTH * CELL_SIZE + 20

    pygame.draw.rect(
        screen,
        (240, 240, 240),
        (
            GRID_WIDTH * CELL_SIZE,
            0,
            SIDEBAR_WIDTH,
            HEIGHT
        )
    )

    y = 20

    lines = [
        "Persistent RL Robot",
        "",
        f"Runtime: {runtime:.2f}s",
        f"Nodes: {nodes}",
        f"Status: {'DONE' if goal_reached else 'RUNNING'}",
        "",
        "Controls:",
        "R = Reset",
        "N = New Random Map",
        "1 = Hospital",
        "2 = Warehouse",
        "3 = Office",
        "4 = Maze",
        "5 = Factory",
        "",
        "Explore first run",
        "Optimal path every",
        "future reset",
        "",
        "Heatmap resets",
        "on R and N"
    ]

    for line in lines:
        text = font.render(
            line,
            True,
            BLACK
        )

        screen.blit(
            text,
            (sidebar_x, y)
        )

        y += 22

    pygame.display.flip()


# -----------------------------
# MAIN
# -----------------------------
def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RL + Persistent Learning Robot")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # -----------------------------
    # WORLD + ROBOT
    # -----------------------------
    world = GridWorld()
    robot = Robot(world.start)

    goal_reached = False
    start_time = time.time()
    runtime = 0

    nodes = 0

    # -----------------------------
    # Q-LEARNING
    # -----------------------------
    memory = QLearningMemory(current_map_name)

    # -----------------------------
    # HEATMAP
    # -----------------------------
    heatmap = [
        [0 for _ in range(world.width)]
        for _ in range(world.height)
    ]

    def reset_heatmap():
        nonlocal heatmap
        heatmap = [
            [0 for _ in range(world.width)]
            for _ in range(world.height)
        ]

    # -----------------------------
    # PATH STORAGE
    # -----------------------------
    path = []
    path_index = 0

    def compute_path():
        nonlocal path
        nonlocal path_index
        nonlocal nodes

        path, nodes = astar(
            world,
            (robot.x, robot.y),
            world.goal
        )

        path_index = 0

    # -----------------------------
    # MAP POLICY
    # -----------------------------
    map_key = get_map_key(world)

    if map_key not in map_policy_memory:
        map_policy_memory[map_key] = {
            "trained": False,
            "optimal_path": None
        }

    policy = map_policy_memory[map_key]

    # -----------------------------
    # LOOP MEMORY
    # -----------------------------
    recent_states = deque(maxlen=20)
    exploration_rate = 0.30

    # -----------------------------
    # RESET
    # -----------------------------
    def reset():
        nonlocal robot
        nonlocal goal_reached
        nonlocal start_time
        nonlocal runtime
        nonlocal path
        nonlocal path_index
        nonlocal recent_states

        robot = Robot(world.start)
        goal_reached = False
        start_time = time.time()
        runtime = 0
        path = []
        path_index = 0
        recent_states = deque(maxlen=20)
        reset_heatmap()

    # -----------------------------
    # LOAD MAP
    # -----------------------------
    def load_map(name):
        nonlocal robot
        nonlocal goal_reached
        nonlocal start_time
        nonlocal runtime
        nonlocal path
        nonlocal path_index
        nonlocal map_key
        nonlocal policy

        global current_map_name

        world.load_map(name)
        current_map_name = name
        robot = Robot(world.start)
        goal_reached = False
        start_time = time.time()
        runtime = 0
        path = []
        path_index = 0
        recent_states.clear()
        reset_heatmap()

        map_key = get_map_key(world)

        if map_key not in map_policy_memory:
            map_policy_memory[map_key] = {
                "trained": False,
                "optimal_path": None
            }

        policy = map_policy_memory[map_key]

    running = True

    # -----------------------------
    # MAIN LOOP
    # -----------------------------
    while running:
        if not goal_reached:
            runtime = time.time() - start_time

        # -----------------------------
        # EVENTS
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # -------------------------
            # PLACE / REMOVE OBSTACLE
            # -------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x //= CELL_SIZE
                y //= CELL_SIZE

                if x < GRID_WIDTH:
                    world.toggle_obstacle(x, y)
                    # invalidate learned path
                    policy["optimal_path"] = None
                    path = []
                    path_index = 0

            # -------------------------
            # KEYBOARD
            # -------------------------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset()
                elif event.key == pygame.K_n:
                    world.generate_random_map()
                    load_map("custom")
                elif event.key == pygame.K_1:
                    load_map("hospital")
                elif event.key == pygame.K_2:
                    load_map("warehouse")
                elif event.key == pygame.K_3:
                    load_map("office")
                elif event.key == pygame.K_4:
                    load_map("maze")
                elif event.key == pygame.K_5:
                    load_map("factory")

        # -----------------------------
        # UPDATE HEATMAP (Fixed Indentation: Now inside loop)
        # -----------------------------
        heatmap[robot.y][robot.x] += 1

        # -----------------------------
        # FIRST RUN → BUILD OPTIMAL PATH
        # -----------------------------
        if policy["optimal_path"] is None:
            policy["optimal_path"], _ = astar(world, world.start, world.goal)

        # -----------------------------
        # GOAL CHECK
        # -----------------------------
        if (robot.x, robot.y) == world.goal and not goal_reached:
            goal_reached = True
            runtime = time.time() - start_time
            policy["trained"] = True

        # -----------------------------
        # MOVEMENT LOGIC
        # -----------------------------
        if not goal_reached:
            # -------------------------
            # AFTER TRAINING → SAFE OPTIMAL PATH FOLLOWING
            # -------------------------
            if policy["trained"] and policy["optimal_path"]:
                if (policy["optimal_path"] is None or
                        not path_is_valid(world, policy["optimal_path"])):

                    policy["optimal_path"], _ = astar(
                        world,
                        (robot.x, robot.y),
                        world.goal
                    )
                    path_index = 0

                if path_index < len(policy["optimal_path"]):
                    nx, ny = policy["optimal_path"][path_index]

                    # extra safety: never step into a newly added obstacle
                    if not world.is_blocked(nx, ny):
                        robot.x, robot.y = nx, ny
                        path_index += 1
                    else:
                        # recompute immediately if blocked
                        policy["optimal_path"], _ = astar(
                            world,
                            (robot.x, robot.y),
                            world.goal
                        )
                        path_index = 0

            # -------------------------
            # EXPLORATION MODE
            # -------------------------
            else:
                state = (robot.x, robot.y)

                # anti-loop logic
                if len(recent_states) < 10 or state in recent_states:
                    action = random.choice(["up", "down", "left", "right"])
                else:
                    action = memory.best_action(state)

                recent_states.append(state)

                moves = {
                    "up": (0, -1),
                    "down": (0, 1),
                    "left": (-1, 0),
                    "right": (1, 0)
                }

                dx, dy = moves[action]
                nx, ny = robot.x + dx, robot.y + dy

                reward = -0.01

                if not (0 <= nx < world.width and 0 <= ny < world.height):
                    nx, ny = robot.x, robot.y
                elif world.is_blocked(nx, ny):
                    reward = -1
                    nx, ny = robot.x, robot.y
                elif (nx, ny) in recent_states:
                    reward = -0.5
                    nx, ny = robot.x, robot.y

                memory.update(state, action, reward, (nx, ny))
                robot.x, robot.y = nx, ny

        # -----------------------------
        # DRAW
        # -----------------------------
        draw(screen, world, robot, font, runtime, goal_reached, 0, heatmap)
        clock.tick(60)

    # Clean shutdown after 'while running' breaks
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


