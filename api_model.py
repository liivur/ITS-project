def convert_simple_path(path):
    """Converts path given as list of tuples of 2 elements into list of point dictionaries"""
    mapped_path = []
    for p in path:
        mapped_path.append({"location": {"lat": p[0], "lng": p[1]}})
    return mapped_path


def convert_simple_paths(paths):
    mapped_paths = []
    for a_path in paths:
        mapped_paths.append(convert_simple_path(a_path))
    return mapped_paths


def convert_google_directions_to_path(directions):
    path_distance = 0
    path = []
    first = True
    for leg in directions[0]['legs']:
        path_distance += leg['distance']['value']
        if first:
            path.append({"location": {"lat": leg['start_location']['lat'], "lng": leg['start_location']['lng']}})
            first = False
        path.append({"location": {"lat": leg['end_location']['lat'], "lng": leg['end_location']['lng']}})
    return path, path_distance


class Path:
    _paths = []
    _distance = 0
    _time = 0
    _pairs = []

    def __init__(self, paths, distance, time, pairs):
        self._paths = paths
        self._distance = distance
        self._time = time
        self._pairs = pairs

    def get_api_dict(self):
        return {
            'paths': self._paths,
            'distance': self._distance,
            'time': self._time,
            'pairs': self._pairs,
        }
