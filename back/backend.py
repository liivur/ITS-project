from flask import Flask, escape, jsonify, request
import googlemaps
import math
from flask_cors import CORS, cross_origin
import numpy as np


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


gmaps = googlemaps.Client(key='AIzaSyCg2zb5Hlx6LNU0zaJw9vg98WvUv7JoZCw')

app = Flask(__name__)
saved_addresses = {
    ('Mõisavahe 2, Tartu, Estonia', 'Kastani 15, Tartu, Estonia'),
    ('Näituse 15, Tartu, Estonia', 'Kastani 15, Tartu, Estonia'),
}


@app.route('/path', methods=['GET'])
@cross_origin()
def api_get_path():
    start = request.args.get('from', '')
    end = request.args.get('to', '')

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

    if not (start and end):
        return "Error: No path field provided. Please specify an path."

    saved_addresses.add((start, end))

    return jsonify(list(saved_addresses))


app.run()
