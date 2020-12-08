import coordinate_based as cb


def nearest_neighbour_coordinates(locations):
    """Constructs path according to nearest neighbor. Expects flat list
    of coordinates. Does not take into account dependencies."""
    coord_distances = cb.calc_coord_distances(locations)

    print("coord distances: ", coord_distances)
    path_indices, distance = nearest_neighbor(0, coord_distances)

    path = []
    for i in path_indices:
        path.append((locations[i][0], locations[i][1]))
    return path, distance


def nearest_neighbor(start, adj_matrix):
    """Nearest neighbor algorithm, start is starting point as integer(row number in adj_matrix))"""
    current_point = start
    unvisited = [x for x in range(len(adj_matrix)) if x != start]
    distance = 0
    path = list()
    path.append(current_point)

    while len(unvisited) > 0:
        min_dist = float('inf')
        closest_point = -1
        for i in unvisited:
            if adj_matrix[current_point][i] < min_dist:
                min_dist = adj_matrix[current_point][i]
                closest_point = i
        unvisited.remove(closest_point)
        current_point = closest_point
        distance += min_dist
        path.append(current_point)

    # close cycle by adding path from last point to start
    last_dist = adj_matrix[current_point][start]
    path.append(start)
    distance += last_dist

    return path, distance


def flatten(locations, start_end=None):
    flattened_locations = []
    if start_end is not None:
        flattened_locations.append(start_end)

    for start, end in locations:
        flattened_locations.append(start)
        flattened_locations.append(end)

    return flattened_locations


def nearest_neighbor_dep_coord_based(locations, start_end_point=None):
    """Coordinate based nearest neighbor with dependencies, uses coordinate based adj matrix.
    Could also just pass the distance function forward"""
    # flatten locations and add start_end(as first)
    flattened = flatten(locations, start_end_point)
    # calc adj matrix for distance func
    adj_matrix = cb.calc_coord_distances(flattened)

    def adj_based_coord_distance(point1, point2):
        return adj_matrix[point1][point2]

    return nearest_neighbour_dependencies(locations, distance_func=adj_based_coord_distance,
                                          start_point=start_end_point)


# honours also from -> to dependencies
def nearest_neighbour_dependencies(locations, distance_func=cb.coordinates_distance, start_point=None):
    """Nearest neighbour path search. Takes into account dependencies between starting and ending points.
    Select first element's start point and add to path. Now find minimal distances between the lastly added point and
    all starting points plus ending points that are already in path. If start is given then add this point to the
    start and end of path."""
    path = []
    overall_distance = 0
    if start_point is not None:
        path.append(start_point)

    if len(locations) > 0:
        locs = locations.copy()
        # path = locs[0][0] # start of first tuple
        while len(locs) > 0:

            # if start point is not given then add first point(from first tuple) of locations and start with that
            if start_point is None:
                path.append(locs[0][0])
                current_point = locs[0][0]
                locs[0] = (None, locs[0][1])
            else:
                current_point = start_point

            min_distance = float('inf')
            closest_point_index = -1
            for i, (start, end) in enumerate(locs):
                point = None
                if start is None:
                    point = end
                else:
                    point = start

                # calc distance
                distance = distance_func(current_point, point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point_index = i

            new_point_tuple = locs[closest_point_index]
            new_point = new_point_tuple[0]
            if new_point is None:
                new_point = new_point_tuple[1]
                locs.pop(closest_point_index)
            else:
                locs[closest_point_index] = (None, new_point_tuple[1])

            path.append(new_point)
            overall_distance += min_distance

        # add starting point to the end also
        distance = distance_func(path[-1], start_point)
        path.append(start_point)
        overall_distance += distance

    return path, overall_distance


def nearest_neighbour_multiple(locations, distance_func=cb.coordinates_distance, start_point=None, number_of_buses=1):
    if number_of_buses > 1:




        sorted_centroids = sorted(centroids, key=lambda x: x[0])

