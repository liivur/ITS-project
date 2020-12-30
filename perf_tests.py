import time
import nearest_neighbour as nn
import brute_force as bf
import back.backend as ba

def test_nn(locations):
    print("test nn")
    start = time.time()
    path, distance = nn.nearest_neighbour_dependencies(locations)
    duration = time.time() - start
    print("nearest neighbour path: ", path)
    print("nearest neighbour distance: ", distance)
    print("nearest neighbour time taken: ", duration)

    verify_locations_to_path(locations, path)


def test_bf(flattened_locations, locations):
    print("test bf")
    start = time.time()
    path, distance = bf.brute_force_axe(flattened_locations, locations)
    duration = time.time() - start
    print("brute force path: ", path)
    print("brute force distance: ", distance)
    print("brute force time taken: ", duration)

    verify_locations_to_path(locations, path)

def test_bb(locations):
    start = time.time()
    result, path = ba.get_path_from_pairs(locations)
    duration = time.time() - start
    pathlist = list(path)
    print("branch and bound path: ", pathlist)
    print("branch and bound distance: ", result)
    print("branch and bound time taken: ", duration)

    verify_locations_to_path(locations, pathlist)


def verify_locations_to_path(locations, path):
    assert 2 * len(locations) == len(path), "length of path is not twice the length of locations"
    for (start, end) in locations:
        path.index(start)
        path.index(end)

    for point in path:
        found = False
        for (start, end) in locations:
            if point == start or point == end:
                found = True
                break
        if not found:
            print("path point ", point, " was not found in locations")
            raise Exception()


if __name__ == "__main__":
    number_of_executions = 5
    persisted_locations = [((58.364129, 26.698139), (58.398912, 26.713159)),
                           ((58.378937, 26.676511), (58.368451, 26.708868)),
                           ((58.355686, 26.722171), (58.368923, 26.736934))
                           # ((58.425186, 26.622571), (58.388913, 26.716914)),
                           # ((58.349309, 26.748329), (58.302939, 26.700287)),
                           # ((58.399309, 26.793293), (58.312939, 26.710287)),
                           # ((58.320931, 26.729309), (58.339482, 26.739239)),
                           # ((58.390211, 26.790032), (58.403823, 26.801293)),
                           # ((58.369291, 26.749233), (58.358932, 26.759483)),
                           # ((58.299121, 26.772372), (58.238472, 26.7438993))
                           ]
    # persisted_locations = [((58.364129, 26.698139), (58.398912, 26.713159)),
    #                        ((58.378937, 26.676510), (58.368450, 26.708868)),
    #                        ((58.355686, 26.722171), (58.368923, 26.736934)),
    #                        ((58.425186, 26.622571), (58.388913, 26.716914)),
    #                        ((58.349309, 26.748329), (58.302939, 26.700287)),
    #                        ((58.399309, 26.793293), (58.312939, 26.710287)),
    #                        ((58.320930, 26.729309), (58.339482, 26.739239)),
    #                        ((58.390211, 26.790032), (58.403823, 26.801293)),
    #                        ((58.369290, 26.749233), (58.358932, 26.759483)),
    #                        ((58.299120, 26.772372), (58.238472, 26.7438993))
    #                        ]

    print("locations: ", persisted_locations)
    # test_nn(persisted_locations)
    #
    # flattened = nn.flatten(persisted_locations)
    #
    # test_bf(flattened, persisted_locations)

    test_bb(persisted_locations)