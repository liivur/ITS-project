from flask import Flask, escape, jsonify, request, render_template
import googlemaps
from flask_cors import CORS, cross_origin
import time
import nearest_neighbour as nn
import brute_force as bf
from branch_and_bound import get_path, get_path_constrained


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
    if len(addresses) < 3:
        return 0, []

    distance_matrix = gmaps.distance_matrix(origins=addresses, destinations=addresses)
    adj = [list(map(lambda x: x['duration']['value'], row['elements'])) for row in distance_matrix['rows']]
    return get_path(adj)


def get_path_from_pairs(pairs):
    if len(pairs) < 2:
        return 0, []

    points, constraints = get_points_with_constraints(pairs)

    distance_matrix = gmaps.distance_matrix(origins=points, destinations=points)
    adj = [list(map(lambda x: x['duration']['value'], row['elements'])) for row in distance_matrix['rows']]
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


gmaps = googlemaps.Client(key='AIzaSyCg2zb5Hlx6LNU0zaJw9vg98WvUv7JoZCw')

app = Flask(__name__)
saved_pairs = {
    ((58.364129, 26.698139), (58.365129, 26.698239)),
}
saved_addresses = {
    ('Mõisavahe 2, Tartu, Estonia', 'Kastani 15, Tartu, Estonia'),
    ('Näituse 15, Tartu, Estonia', 'Kastani 15, Tartu, Estonia'),
}

# list holds locations as latitude longitude pairs/tuples that will be used for path operations
persisted_locations = []
start_end_location = (58.364129, 26.698139)


@app.route('/')
def index():
    return render_template('index.html')


# =========== ROUTE APIS ===========

@app.route('/path', methods=['GET'])
@cross_origin()
def api_get_path():
    start = request.args.get('from', '')
    end = request.args.get('to', '')

    pairs = list(saved_pairs)
    if start and end:
        start = tuple(map(lambda x: float(x), start.split(',')))
        end = tuple(map(lambda x: float(x), end.split(',')))
        pairs.append((start, end))

    start_time = time.time()
    result, path = get_path_from_pairs(pairs)
    time_taken = time.time() - start_time

    mapped_path = []
    for p in path:
        mapped_path.append({"location": {"lat": p[0], "lng": p[1]}})

    return jsonify({
        'path': mapped_path,
        'distance': result,
        'time': time_taken,
    })


@app.route('/path', methods=['POST'])
@cross_origin()
def api_save_path():
    # addresses = request.args.getlist('addresses')
    start = request.form.get('from', '')
    end = request.form.get('to', '')

    if not (start and end):
        return "Error: No path field provided. Please specify an path."

    start = tuple(map(lambda x: float(x), start.split(',')))
    end = tuple(map(lambda x: float(x), end.split(',')))

    saved_pairs.add((start, end))

    return jsonify(list(saved_pairs))


@app.route('/path_google', methods=['GET'])
@cross_origin()
def api_get_path_google():
    locations = get_flat_addresses(persisted_locations)
    # add_start_and_end(locations)

    start_time = time.time()
    direction = gmaps.directions(origin=locations[0], destination=locations[0], waypoints=locations[1:],
                                 optimize_waypoints=True, mode="driving", alternatives=False)
    time_taken = time.time() - start_time
    print('received direction in ', time_taken, ' s:', direction)
    print("path distance: ", direction[0]['legs'][0]['distance']['value'])

    path_distance = 0

    path = []
    first = True
    for leg in direction[0]['legs']:
        path_distance += leg['distance']['value']
        if first:
            path.append({"location": {"lat": leg['start_location']['lat'], "lng": leg['start_location']['lng']}})
            first = False
        path.append({"location": {"lat": leg['end_location']['lat'], "lng": leg['end_location']['lng']}})
    print("constructed path: ", path)
    responseDict = {"path": path, "distance": path_distance, "time": time_taken}

    print("overall distance=", path_distance)
    return jsonify(responseDict)


@app.route('/path_coord_nn')
@cross_origin()
def api_get_path_coord_nn():
    print("nn for: ", persisted_locations)
    # flatten
    locations = list()
    for start, end in persisted_locations:
        locations.append(start)
        locations.append(end)
    # add_start_and_end(locations)

    start_time = time.time()
    path, distance = nn.nearest_neighbour_coordinates(locations)
    # coord_distances = nn.calc_coord_distances(locations)
    time_taken = time.time() - start_time

    # print("coord distances: ", coord_distances)
    # path_indices, distance = nn.nearest_neighbor(0, coord_distances)

    print("returning distance=", distance)

    returning_path = []

    for p in path:
        returning_path.append({"location": {"lat": p[0], "lng": p[1]}})
    print("returning path: ", returning_path)
    responseDict = {"path": returning_path, "distance": distance, "time": time_taken}

    return jsonify(responseDict)


@app.route('/path_coord_nn_dep')
@cross_origin()
def api_get_path_coord_nn_dep():
    start_time = time.time()
    path, distance = nn.nearest_neighbour_dependencies_start(persisted_locations, start_end_location)
    time_taken = time.time() - start_time
    print("time taken: ", time_taken)
    print("path: ", path)
    print("distance: ", distance)

    returning_path = []

    for p in path:
        returning_path.append({"location": {"lat": p[0], "lng": p[1]}})
    print("returning path: ", returning_path)
    responseDict = {"path": returning_path, "distance": distance, "time": time_taken}

    return jsonify(responseDict)


@app.route('/path_brute_axe')
@cross_origin()
def brute_axe_method():
    # flatten
    locations = list()
    for start, end in persisted_locations:
        locations.append(start)
        locations.append(end)
    # add_start_and_end(locations)

    start_time = time.time()
    path, distance = bf.brute_force_axe(locations)
    time_taken = time.time() - start_time

    print("returning distance=", distance)
    print("returning path: ", path)

    returning_path = []

    for p in path:
        returning_path.append({"location": {"lat": p[0], "lng": p[1]}})

    responseDict = {"path": returning_path, "distance": distance, "time": time_taken}

    return jsonify(responseDict)


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
    print("adding locations: ", request)
    print("is_json:", request.is_json)
    locs = request.get_json()
    print("json: ", locs)
    print(dir(locs))
    print(locs['locations'])
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


app.run(debug=True)
