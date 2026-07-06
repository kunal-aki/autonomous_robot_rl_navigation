from heapq import heappush, heappop


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(world, start, goal):

    open_set = []
    heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    visited = 0

    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    while open_set:

        _, current = heappop(open_set)
        visited += 1

        if current == goal:

            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            # ✅ ALWAYS RETURN SAME FORMAT
            return path, visited

        for dx, dy in directions:

            nx = current[0] + dx
            ny = current[1] + dy

            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue

            if world.is_blocked(nx, ny):
                continue

            neighbor = (nx, ny)

            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:

                g_score[neighbor] = tentative_g
                came_from[neighbor] = current

                f = tentative_g + heuristic(neighbor, goal)
                heappush(open_set, (f, neighbor))

    return [], visited


