import coordinate_based as cb

def create_clusters(locations, number_of_clusters=1):
    if number_of_clusters > 1:
        # each pair is 1 cluster
        clusters = []
        # clusters.append([(start_point, None)])
        for pair in locations:
            clusters.append([pair])

        while len(clusters) > number_of_clusters:
            # find closest clusters and merge
            min_cluster_distance = float('inf')
            min_cluster_index1 = -1
            min_cluster_index2 = -1
            for i in range(len(clusters) - 1):
                for j in range(i, len(clusters)):
                    dist = cb.calculate_distance(clusters[i], clusters[j])
                    if dist < min_cluster_distance:
                        min_cluster_distance = dist
                        min_cluster_index1 = i
                        min_cluster_index2 = j
            # merge clusters
            clusters[min_cluster_index1].extend(clusters.pop(min_cluster_index2))

        # points merged, clusters formed
        print("found clusters: ", clusters)
        return clusters
    else:
        return [locations]


if __name__ == '__main__':
    locs = [((58.384292, 26.722858), (58.398912, 26.713159)), ((58.378937, 26.67651), (58.36845, 26.708868)),
            ((58.384292, 26.722858), (58.394291, 26.712848))]
    result1 = create_clusters(locs, 1)
    result2 = create_clusters(locs, 2)
    result3 = create_clusters(locs, 3)