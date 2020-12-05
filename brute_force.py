import nearest_neighbour as nn

path_counter = 0


def brute_force_axe(locations):
    return brute_force_rec(list(), locations)

# no dependencies yet
def brute_force_rec(path, locations):
    global path_counter
    # points = locations.copy()
    if len(locations) == 0:
        path_counter += 1
        return path, calculate_path_distance(path)
    min_path = None
    min_distance = float('inf')
    for i in range(len(locations)):
        points = locations.copy()
        p = points.pop(i)
        down_path = path.copy()
        down_path.append(p)
        found_path, distance = brute_force_rec(down_path, points)
        if distance < min_distance:
            min_distance = distance
            min_path = found_path
    return min_path, min_distance


def calculate_path_distance(path):
    distance = 0
    for i in range(1, len(path)):
        distance += nn.coordinates_distance(path[i-1], path[i])
    return distance


if __name__ == '__main__':
    import time
    import math
    locs = [(58.384292, 26.722858), (58.398912, 26.713159), (58.378937, 26.67651), (58.36845, 26.708868), (58.384292, 26.722858)]
    print("points: ", len(locs))
    print("n! = ", math.factorial(len(locs)))
    start_time = time.time()
    path, distance = brute_force_rec(list(), locs)
    print("time: ", time.time() - start_time)
    print("found min path=", path)
    print("found min distance=", distance)
    print("paths: ", path_counter)