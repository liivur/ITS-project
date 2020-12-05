from flask import Flask, escape, jsonify, request, render_template
import googlemaps
import math
from flask_cors import CORS, cross_origin
import time
import nearest_neighbour as nn
import brute_force as bf


# solution based on https://www.geeksforgeeks.org/traveling-salesman-problem-using-branch-and-bound-2/
# Function to find the minimum edge cost
# having an end at the vertex i
def first_min(weights, i, maxsize=float('inf')):
    minimum = maxsize
    for k in range(len(weights)):
        if weights[i][k] < minimum and i != k:
            minimum = weights[i][k]

    return minimum


# function to find the second minimum edge
# cost having an end at the vertex i
def second_min(weights, i, maxsize=float('inf')):
    first, second = maxsize, maxsize
    for j in range(len(weights)):
        if i == j:
            continue
        if weights[i][j] <= first:
            second = first
            first = weights[i][j]
        elif weights[i][j] <= second and weights[i][j] != first:
            second = weights[i][j]

    return second


def get_path_rec(weights, lower_bound, weight, level, path, visited, final_result=float('inf')):
    n = len(weights)

    # base case is when we have reached level N
    # which means we have covered all the nodes once
    if level == n:
        # current_result has the total weight of the solution we got
        current_result = weight + weights[path[level - 1]][path[0]]
        final_path = path[:]
        final_path[n] = path[0]

        return current_result, final_path

    final_path = []
    # for any other level iterate for all vertices to build the search space tree recursively
    for i in range(n):
        if weights[path[level - 1]][i] == 0 or visited[i]:
            continue

        current_weight = weight + weights[path[level - 1]][i]

        # different computation of curr_bound
        # for level 2 from the other levels
        if level == 1:
            item_bound = (first_min(weights, path[level - 1]) + first_min(weights, i)) / 2
        else:
            item_bound = (second_min(weights, path[level - 1]) + first_min(weights, i)) / 2

        t_bound = lower_bound - item_bound
        # t_bound + current_weight is the actual lower bound for the node that we have arrived on.
        # If current lower bound < final_res, we need to explore the node further
        if t_bound + current_weight < final_result:
            path[level] = i
            visited[i] = True
            t_result, t_path = get_path_rec(weights, t_bound, current_weight, level + 1, path, visited, final_result)

            if t_result < final_result:
                final_result = t_result
                final_path = t_path

        visited = [False] * len(visited)
        for j in range(level):
            if path[j] != -1:
                visited[path[j]] = True

    return final_result, final_path


def get_path(weights):
    n = len(weights)

    # Calculate initial lower bound for the root node
    # using the formula 1/2 * (sum of first min +
    # second min) for all edges.
    bound = 0
    for i in range(n):
        bound += first_min(weights, i) + second_min(weights, i)
    bound = math.ceil(bound / 2)

    # Initialize the current_path and visited array
    path = [-1] * (n + 1)
    visited = [False] * n

    # We start at vertex 1 so the first vertex
    # in path[] is 0
    visited[0] = True
    path[0] = 0

    # Call to get_path_rec for curr_weight
    # equal to 0 and level 1
    return get_path_rec(weights, bound, 0, 1, path, visited)


def get_path_from_addresses(addresses):
    if len(addresses) < 3:
        return 0, []

    distance_matrix = gmaps.distance_matrix(origins=addresses, destinations=addresses)
    adj = [list(map(lambda x: x['duration']['value'], row['elements'])) for row in distance_matrix['rows']]
    return get_path(adj)


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

    print("path from %s to %s" % (start, end))

    # TODO: add proper handling for from and to
    addresses = get_flat_addresses(saved_addresses)
    if start and end:
        addresses.append(start)
        addresses.append(end)

    result, path = get_path_from_addresses(addresses)

    locations = []
    for i in path:
        locations.append({
            'address': addresses[i],
            'coords': get_coords(addresses[i]),
        })

    return jsonify({
        'path': locations,
        'result': result,
    })


@app.route('/path', methods=['POST'])
@cross_origin()
def api_save_path():
    # addresses = request.args.getlist('addresses')
    start = request.form.get('from', '')
    end = request.form.get('to', '')

    print("saving path from %s to %s" %(start, end))
    if not (start and end):
        return "Error: No path field provided. Please specify an path."

    saved_addresses.add((start, end))

    return jsonify(list(saved_addresses))


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
