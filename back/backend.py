from flask import Flask, escape, jsonify, request, render_template
import googlemaps
from flask_cors import CORS, cross_origin
import time
import nearest_neighbour as nn
import brute_force as bf
from branch_and_bound import get_path, get_path_constrained
import api_model
import clustering
import math
import coordinate_based as cb


def convert_to_list(pairs):
    return_list = []
    for p in pairs:
        return_list.append(p)
    return return_list


def get_points_with_constraints(point_pairs):
    points = []
    for pair in point_pairs:
        points.append(pair[0])
        points.append(pair[1])

    indexes = {}
    points = list(set(points))
    for i in range(len(points)):
        indexes[points[i]] = i

    constraints = [(indexes[pair[0]], indexes[pair[1]]) for pair in point_pairs]

    return points, constraints


def get_path_from_addresses(addresses):
    if len(addresses) < 2:
        return 0, []

    distance_matrix = gmaps.distance_matrix(origins=addresses, destinations=addresses)
    adj = [list(map(lambda x: x['duration']['value'], row['elements'])) for row in distance_matrix['rows']]
    return get_path(adj)


def get_path_from_pairs(pairs):
    if len(pairs) < 1:
        return 0, []

    points, constraints = get_points_with_constraints(pairs)

    distance_matrix = gmaps.distance_matrix(origins=points, destinations=points)
    adj = [list(map(lambda x: x['distance']['value'], row['elements'])) for row in distance_matrix['rows']]
    result, path = get_path_constrained(adj, constraints)

    return result, map(lambda i: points[i], path)


def get_coords(address):
    geocode = gmaps.geocode(address)
    return geocode[0]['geometry']['location']['lat'], geocode[0]['geometry']['location']['lng']


def get_flat_addresses(addresses):
    flat = []
    for address in addresses:
        flat.append(address[0])
        flat.append(address[1])

    return flat


def add_start_and_end(locations):
    locations.insert(0, start_end_location)
    locations.append(start_end_location)


# duplicate with one in nearest_neighbor
def flatten(locations, start_end=None):
    flattened_locations = []
    if start_end is not None:
        flattened_locations.append(start_end)

    for start, end in locations:
        flattened_locations.append(start)
        flattened_locations.append(end)

    return flattened_locations


def get_google_based_distance_func(locations, start_end_point):
    flattened_points = flatten(locations, start_end_point)
    # calc adj matrix for distance func
    distance_matrix = gmaps.distance_matrix(origins=flattened_points, destinations=flattened_points)
    adj_matrix = [list(map(lambda x: x['distance']['value'], row['elements'])) for row in distance_matrix['rows']]

    def adj_based_road_distance(point1, point2):
        point1_index = flattened_points.index(point1)
        point2_index = flattened_points.index(point2)
        return adj_matrix[point1_index][point2_index]

    return adj_based_road_distance


gmaps = googlemaps.Client(key='AIzaSyCg2zb5Hlx6LNU0zaJw9vg98WvUv7JoZCw')

app = Flask(__name__)

timeslots = ['10:00', '10:30', '11:00', '11:30']
saved_pairs = {}
for slot in timeslots:
    saved_pairs[slot] = set()

# saved_pairs['10:00'].add(((58.364129, 26.698139), (58.365129, 26.698239)))
saved_pairs['10:00'].add(((58.364129, 26.698139), (58.367533, 26.693740)))


# list holds locations as latitude longitude pairs/tuples that will be used for path operations
persisted_locations = []
start_end_location = (58.364129, 26.698139)

google_road_based_distance = True  # otherwise coordinate based distance


@app.route('/')
def index():
    return render_template('index.html')


# =========== ROUTE APIS ===========

@app.route('/path', methods=['GET'])
@cross_origin()
def api_get_path():
    start = request.args.get('from', '')
    end = request.args.get('to', '')
    slot = request.args.get('slot', timeslots[0])
    if not slot:
        slot = timeslots[0]

    pairs = list(saved_pairs[slot])
    if start and end:
        start = tuple(map(lambda x: float(x), start.split(',')))
        end = tuple(map(lambda x: float(x), end.split(',')))
        pairs.append((start, end))

    start_time = time.time()
    result, path = get_path_from_pairs(pairs)
    time_taken = time.time() - start_time

    path_model = api_model.Path(api_model.convert_simple_paths([path]), result, time_taken, pairs)
    return jsonify(path_model.get_api_dict())


@app.route('/path', methods=['POST'])
@cross_origin()
def api_save_path():
    # addresses = request.args.getlist('addresses')
    start = request.form.get('from', '')
    end = request.form.get('to', '')
    slot = request.form.get('slot', timeslots[0])
    if not slot:
        slot = timeslots[0]

    if not (start and end):
        return "Error: No path field provided. Please specify an path."

    start = tuple(map(lambda x: float(x), start.split(',')))
    end = tuple(map(lambda x: float(x), end.split(',')))

    saved_pairs[slot].add((start, end))

    return jsonify(list(saved_pairs[slot]))


@app.route('/path_google', methods=['GET'])
@cross_origin()
def api_get_path_google():
    slot = request.args.get('slot', timeslots[0])
    pairs = convert_to_list(saved_pairs[slot])
    flattened = flatten(locations=pairs)
    # locations = get_flat_addresses(persisted_locations)
    # add_start_and_end(locations)

    start_time = time.time()
    direction = gmaps.directions(origin=start_end_location, destination=start_end_location, waypoints=flattened,
                                 optimize_waypoints=True, mode="driving", alternatives=False)
    time_taken = time.time() - start_time

    path, path_distance = api_model.convert_google_directions_to_path(direction)

    api_path = api_model.Path([path], path_distance, time_taken, pairs)

    return jsonify(api_path.get_api_dict())


@app.route('/path_coord_nn')
@cross_origin()
def api_get_path_coord_nn():
    print("nn for: ", persisted_locations)
    # flatten
    locations = list()
    for start, end in persisted_locations:
        locations.append(start)
        locations.append(end)

    start_time = time.time()
    path, distance = nn.nearest_neighbour_coordinates(locations)
    # coord_distances = nn.calc_coord_distances(locations)
    time_taken = time.time() - start_time

    print("returning distance=", distance)

    api_path = api_model.Path(api_model.convert_simple_paths([path]), distance, time_taken, persisted_locations)

    return jsonify(api_path.get_api_dict())


@app.route('/path_coord_nn_dep')
@cross_origin()
def api_get_path_coord_nn_dep():
    # google_road_based_distance = False

    slot = request.args.get('slot', timeslots[0])
    pairs = convert_to_list(saved_pairs[slot])
    # max 4 pairs in a cluster for google distance matrix
    number_of_clusters = math.ceil(len(pairs) / 4.0)
    # number_of_clusters = 1
    print("number of clusters: ", number_of_clusters)
    clusters = clustering.create_clusters(pairs, number_of_clusters)

    paths = []
    distances = 0
    total_time = 0
    for cluster in clusters:
        if google_road_based_distance:
            road_distance_func = get_google_based_distance_func(cluster, start_end_location)
            start_time = time.time()
            path, distance = nn.nearest_neighbour_dependencies(cluster, road_distance_func, start_end_location)
            time_taken = time.time() - start_time
        else:
            start_time = time.time()
            # path, distance = nn.nearest_neighbor_dep_coord_based(cluster, start_end_location)
            path, distance = nn.nearest_neighbour_dependencies(cluster, cb.coordinates_distance, start_end_location)
            time_taken = time.time() - start_time
        paths.append(path)
        distances += distance
        total_time += time_taken

    print("time taken: ", total_time)
    print("paths: ", paths)
    print("distance: ", distances)

    api_path = api_model.Path(api_model.convert_simple_paths([path]), distances, total_time, pairs)

    return jsonify(api_path.get_api_dict())


@app.route('/path_brute_axe')
@cross_origin()
def brute_axe_method():
    slot = request.args.get('slot', timeslots[0])
    pairs = convert_to_list(saved_pairs[slot])
    # flatten
    flattened = flatten(pairs) # do not add start_end to flattened list
    # , otherwise will be used for permutations

    if google_road_based_distance:
        road_distance_func = get_google_based_distance_func(pairs, start_end_location)
        start_time = time.time()
        path, distance = bf.brute_force_axe(flattened, pairs, start_end_location, road_distance_func)
        time_taken = time.time() - start_time
    else:
        start_time = time.time()
        path, distance = bf.brute_force_axe(flattened, pairs, start_end_location)
        time_taken = time.time() - start_time

    print("returning distance=", distance)
    print("returning path: ", path)

    api_path = api_model.Path(api_model.convert_simple_paths([path]), distance, time_taken, pairs)

    return jsonify(api_path.get_api_dict())


# =========== LOCATIONS APIS ===========

@app.route('/locations/add')
@cross_origin()
def add_start_end():
    print("adding location: ", request)
    start = request.args.get('from', '')
    end = request.args.get('to', '')
    start_coordinates = start.split(',')
    end_coordinates = end.split(',')
    print('values %s, %s' % (start_coordinates, end_coordinates))
    start_lat = float(start_coordinates[0])
    start_lng = float(start_coordinates[1])
    end_lat = float(end_coordinates[0])
    end_lng = float(end_coordinates[1])

    persisted_locations.append(((start_lat, start_lng), (end_lat, end_lng)))
    return "ok"


@app.route('/locations/add_multiple', methods=['POST'])
@cross_origin()
def add_locations():
    locs = request.get_json()
    for loc in locs['locations']:
        print("loc: %s" % (loc))
        persisted_locations.append((
            (float(loc['from']['lat']), float(loc['from']['lng'])),
            (float(loc['to']['lat']), float(loc['to']['lng']))
        ))

    return "ok"


@app.route('/locations')
@cross_origin()
def get_locations():
    print("get locations: ", request)
    print("locations:", persisted_locations)
    return jsonify(persisted_locations)


@app.route('/locations/reset')
def reset():
    print("reset locations")
    persisted_locations.clear()
    return "ok"


@app.route('/slots', methods=['GET'])
@cross_origin()
def api_get_slots():
    return jsonify(timeslots)


@app.route('/algorithms', methods=['GET'])
@cross_origin()
def api_get_algorithms():
    return jsonify([
        {
            'name': 'Branch and bound',
            'path': 'path',
        },
        {
            'name': 'Nearest neighbour',
            'path': 'path_coord_nn_dep',
        },
    ])


app.run(debug=True)
