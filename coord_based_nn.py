import math
import numpy as np

def coordinates_distance(point1, point2):
    """haversine formula to calculate the great-circle distance between 2 points"""
    lat1, lng1 = point1
    lat2, lng2 = point2
    print("coordinates_distance: %f, %f, %f, %f" %(lat1, lng1, lat2, lng2))
    # lat1 = point1[0]
    # lat2 = point2[0]
    # lon1 = point1[1]
    # lon2 = point2[1]
    R = 6371000 # meters
    fii1 = lat1 * math.pi / 180
    fii2 = lat2 * math.pi / 180
    d_fii = (lat2 - lat1) * math.pi / 180
    d_lambda = (lng2 - lng1) * math.pi / 180

    a = math.sin(d_fii/2)**2 + math.cos(fii1) * math.cos(fii2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c  # in meters
    return d


def calc_coord_distances(locations):
    """Calculate distances of all locations(latitude longitude)"""
    n = len(locations)
    coord_distances = np.empty((n, n))
    for i in range(n - 1):
        coord_distances[i, i] = 0.0
        for j in range(i + 1, n):
            dist = coordinates_distance(locations[i], locations[j])
            coord_distances[i][j] = dist
            coord_distances[j][i] = dist
    return coord_distances


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
