import coordinate_based as cb

path_counter = 0


def brute_force_axe(flat_locations, locations, start_end=None, distance_func=cb.coordinates_distance):
    """Single bus brute force method, calculates and measures distance of every permutation.
    Takes into account also dependencies."""
    if start_end is not None:
        path = [start_end]
    else:
        path = []
    return brute_force_rec(path, flat_locations, locations, start_end, distance_func=distance_func)


def brute_force_rec(path, flat_locations, locations, start_end=None, distance_func=cb.coordinates_distance):
    """Single bus brute force method(recursive), calculates and measures distance of every permutation.
        Takes into account dependencies also."""
    global path_counter
    if len(flat_locations) == 0:
        path_counter += 1
        if verify_dependencies(locations, path):
            if start_end is not None:
                path.append(start_end)
            return path, calculate_path_distance(path, distance_func=distance_func)
        else:
            return path, float('inf')
    min_path = None
    min_distance = float('inf')
    for i in range(len(flat_locations)):
        points = flat_locations.copy()
        p = points.pop(i)
        down_path = path.copy()
        down_path.append(p)
        found_path, distance = brute_force_rec(down_path, points, locations, start_end, distance_func)
        if distance < min_distance:
            min_distance = distance
            min_path = found_path
        if len(path) == 0:
            print(i, " iteration done")
    return min_path, min_distance


# attempt to do more efficient brute force
# def brute_force_dep(path, locations, start_end, distance_func=cb.coordinates_distance):
#     path = [start_end]
#     # locs = locations.copy()
#     brute_force_rec_dep(path, locations, distance_func)
#
# def brute_force_rec_dep(path, locations, distance_func=cb.coordinates_distance):
#     global path_counter
#     # points = locations.copy()
#     if len(locations) == 0:
#         path_counter += 1
#         return path, calculate_path_distance(path, distance_func)
#     min_path = None
#     min_distance = float('inf')
#     pair_counter = 0
#     point_counter = 0  # point counter in pair
#     while True:
#         current_pair = locations[pair_counter]
#         current_point = current_pair[point_counter]
#         if current_pair[0] == -1:  # start point already selected, end point can be selected
#             endpoint_selected = True
#             current_point = current_pair[1]
#
#         # end activities
#         if point_counter < 2:
#             point_counter += 1
#         else:
#             pair_counter += 1
#             point_counter = 0
#
#     #---
#     for i in range(len(locations)):
#         points = locations.copy()
#         p = points.pop(i)
#         down_path = path.copy()
#         down_path.append(p)
#         found_path, distance = brute_force_rec(down_path, points)
#         if distance < min_distance:
#             min_distance = distance
#             min_path = found_path
#     return min_path, min_distance

def calculate_path_distance(path, distance_func=cb.coordinates_distance):
    distance = 0
    for i in range(1, len(path)):
        distance += distance_func(path[i-1], path[i])
    return distance


def verify_dependencies(locations, path):
    for start, end in locations:
        start_index = path.index(start)
        try:
            path.index(end, start_index)  # raises error, if not found (endpoint after start)
        except ValueError:
            return False
    return True


if __name__ == '__main__':
    import time
    import math
    locs = [(58.384292, 26.722858), (58.398912, 26.713159), (58.378937, 26.67651), (58.36845, 26.708868), (58.384292, 26.722858)]
    print("points: ", len(locs))
    print("n! = ", math.factorial(len(locs)))
    start_time = time.time()
    path, distance = brute_force_rec(list(), locs, [])
    print("time: ", time.time() - start_time)
    print("found min path=", path)
    print("found min distance=", distance)
    print("paths: ", path_counter)

    # test verify_dependencies
    locs1 = [((2,3),(3,4)),((5,5),(6,6))]
    path1 = [(5,5), (2,3), (3,4), (6,6)]
    path2 = [(2,3), (6,6), (5,5), (3,4)]
    assert verify_dependencies(locs1, path1), "correct path according to dependencies"
    assert not verify_dependencies(locs1, path2), "incorrect path according to dependencies"
