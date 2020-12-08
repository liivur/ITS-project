import math
# solution based on https://www.geeksforgeeks.org/traveling-salesman-problem-using-branch-and-bound-2/


def is_path_allowed(i, path, constraints):
    for constraint in constraints[i]:
        if path[constraint] == -1:
            return False

    return True


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


def get_path_rec(weights, lower_bound, weight, level, path, visited, constraints, final_result=float('inf')):
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
        if weights[path[level - 1]][i] == 0 or visited[i] or not is_path_allowed(i, path, constraints):
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
            t_result, t_path = get_path_rec(weights, t_bound, current_weight, level + 1, path, visited, constraints, final_result)

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

    if n < 2:
        return 0, []
    if n == 2:
        return weights[0][1], [0, 1]

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


def get_path_constrained(weights, from_to=[]):
    n = len(weights)

    if n < 2:
        return 0, []
    if n == 2:
        return weights[from_to[0][0]][from_to[0][1]], [0, 1]

    # Set constraints - can only pick an edge if all the constraints are already in the path
    constraints = [[] for i in range(n)]
    for pair in from_to:
        constraints[pair[1]].append(pair[0])

    # Initialize the current_path and visited array
    path = [-1] * (n + 1)
    visited = [False] * n

    # We start at vertex 1 so the first vertex
    # in path[] is 0
    visited[0] = True
    path[0] = 0

    # Calculate initial lower bound for the root node
    # using the formula 1/2 * (sum of first min +
    # second min) for all edges.
    bound = 0
    for i in range(n):
        bound += first_min(weights, i) + second_min(weights, i)
    bound = math.ceil(bound / 2)

    # Call to get_path_rec for curr_weight
    # equal to 0 and level 1
    return get_path_rec(weights, bound, 0, 1, path, visited, constraints)

