import math
import numpy as np


def coordinates_distance(point1, point2):
    """haversine formula to calculate the great-circle distance between 2 points"""
    lat1, lng1 = point1
    lat2, lng2 = point2
    R = 6371000  # meters
    fii1 = lat1 * math.pi / 180
    fii2 = lat2 * math.pi / 180
    d_fii = (lat2 - lat1) * math.pi / 180
    d_lambda = (lng2 - lng1) * math.pi / 180

    a = math.sin(d_fii / 2) ** 2 + math.cos(fii1) * math.cos(fii2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = R * c  # in meters
    return d


def calc_coord_distances(locations):
    """Calculate distances of all locations(latitude longitude).
    Expects flat list, not pairs of points"""
    n = len(locations)
    coord_distances = np.empty((n, n))
    for i in range(n - 1):
        coord_distances[i, i] = 0.0
        for j in range(i + 1, n):
            dist = coordinates_distance(locations[i], locations[j])
            coord_distances[i][j] = dist
            coord_distances[j][i] = dist
    return coord_distances


def calc_adj_dist_matrix(locations):
    """Expects flat locations list with tuples of lat long"""
    n = len(locations) * 2
    adj_matrix = []
    for point1 in locations:
        for point2 in locations:
            adj_matrix[point1][point2] = adj_matrix[point2][point1] = coordinates_distance(point1, point2)
    return adj_matrix
