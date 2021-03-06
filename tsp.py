import numpy as np
import math
import random
import matplotlib.pyplot
import time

# TODO: Make some visualizations
# TODO: Add sum of distances comparision (instead of minimum criterium)
# TODO: Make more real data generator (distance between town A and B should be
#  lower than between town A and C + C and A)
# TODO: Make report
# TODO: Make documentation
# TODO: Develop Genetic algorithm, new crossing methods (ranking, roulette)


def make_random_matrix(number_of_towns: int = 16, min_distance: int = 10, max_distance: int = 100) -> int:
    """
    Function to make random matrix of distances between towns
    :param number_of_towns : number of towns in matrix
    :type number_of_towns: int
    :param min_distance: minimal distance between towns
    :type min_distance: int
    :param max_distance: maximum distance between towns
    :type max_distance: int
    :return: distance matrix
    :rtype: int
    """
    mat = np.random.randint(low=min_distance, high=max_distance, size=(number_of_towns, number_of_towns), dtype='int32')
    for i in range(len(mat)):
        mat[i][i] = 0
    return mat


def generate_random_route(data: np.array, number_of_drivers: int = 1, start_town: int = 0) -> tuple:
    """
    :param data: distance matrix
    :type data: np.array
    :param number_of_drivers: number of travelers/drivers
    :type number_of_drivers: int
    :param start_town: index of starting town
    :type start_town: int
    :return: tuple of distances and routes of each travelers
    :rtype: tuple
    """
    assert start_town < len(data[0])  # Town must be at matrix!
    route = [x for x in range(len(data[0])) if x != start_town]
    for i in range(number_of_drivers-1):
        route.append(start_town)
    random.shuffle(route)
    route = [start_town] + route
    route.append(start_town)
    distances = np.zeros(number_of_drivers, dtype='float')
    j = -1
    for i in range((len(route)-1)):
        if route[i] == start_town:
            j = j+1
        distances[j] = distances[j] + data[route[i], route[i+1]]
    return distances, route


def distance_comparision(first_dist: np.array, second_dist: np.array, kind='min') -> bool:
    """
    Distance comparision function
    :param first_dist: first distance to compare
    :type first_dist: np.array
    :param second_dist: second distance to compare
    :type second_dist: np.array
    :param kind: type of comparision
    :type kind: str
    :return: True or False depends of which of dinstaces are "better"
    :rtype: bool
    """
    to_return = False
    if kind == 'min':
        to_return = max(first_dist) < max(second_dist)
    return to_return


def random_search(data: np.array, test_time: float = 1, number_of_drivers: int = 1,
                  dist_comp: str = 'min', start_town: int = 0) -> tuple:
    """
    Random search implementation
    :param data: distances matrix
    :type data: np.array
    :param test_time: time of testing
    :type test_time: float
    :param number_of_drivers: number of travelers
    :type number_of_drivers: int
    :param dist_comp: type of distance comparision
    :type dist_comp: str
    :param start_town: starting_town
    :type start_town: int
    :return: tuple of best distances and routes of each travelers
    :rtype: tuple
    """
    iterations = 0
    best_dist, best_route = generate_random_route(data=data, number_of_drivers=number_of_drivers, start_town=start_town)
    y = [max(best_dist)]
    act_time = time.time()
    while time.time() < act_time + test_time:
        current_dist, current_route = generate_random_route(data, number_of_drivers, start_town=start_town)
        iterations = iterations + 1
        if distance_comparision(current_dist, best_dist, kind=dist_comp):
            best_dist, best_route = current_dist, current_route
        y.append(max(best_dist))
    prop = (test_time * 60) / len(y)
    x_data = []
    for i in range(len(y)):
        x_data.append(i * prop)
    matplotlib.pyplot.plot(x_data, y, label="random_search")
    matplotlib.pyplot.ylabel('distance')
    matplotlib.pyplot.xlabel('time[ms]')
    print("Random Search")
    print("Best distance: " + str(best_dist))
    print("Best Route " + str(best_route))
    print("Iterations " + str(iterations))
    return best_dist, best_route


def simulated_annealing(data: np.array, test_time: float = 1, number_of_drivers: int = 1, start_town: int = 0,
                        initial_temperature: float = 400000, temp_decrease_ratio: float = 0.99,
                        use_swap: bool = True) -> tuple:
    """
    Simulated Annealing implementation
    :param data: distances matrix
    :type data: np.array
    :param test_time: time of testing
    :type test_time: float
    :param number_of_drivers: number of travelers
    :type number_of_drivers: int
    :param start_town: starting_town
    :type start_town: int
    :param initial_temperature: hyperparameter of SA
    :type initial_temperature: float
    :param temp_decrease_ratio: hyperparameter of SA
    :type temp_decrease_ratio: float
    :param use_swap: Swap two elements of route list instead of generate new random route
    :type use_swap: bool
    :return: tuple of best distances and routes of each travelers
    :rtype: tuple
    """
    
    def swap(route: list, num_of_drivers: int) -> tuple:
        """
        Function for swaping two elements in route list
        :param route: list of next town destination
        :type route: list
        :param num_of_drivers: number of travelers
        :type num_of_drivers: int
        :return: new route and distance of it
        :rtype: tuple
        """
        new_route = []
        new_route = new_route + route
        first_index, second_index = random.sample(population=list(range(1, len(route) - 2)), k=2)
        new_route[first_index] = route[second_index]
        new_route[second_index] = route[first_index]
        new_distance = np.zeros(num_of_drivers, dtype='float')
        j = -1
        st_town = max(set(route), key=route.count)  # get the most frequent element
        for k in range((len(route) - 1)):
            if route[k] == st_town:
                j = j + 1
            new_distance[j] = new_distance[j] + data[route[k], route[k + 1]]
        return new_distance, new_route

    iterations = 0
    actual_dist, actual_route = generate_random_route(data, number_of_drivers, start_town=start_town)
    best_dist, best_route = actual_dist, actual_route
    y = [max(actual_dist)]
    temperature = initial_temperature
    temp_decrease_ratio = temp_decrease_ratio
    act_time = time.time()
    while time.time() < act_time + test_time:
        iterations = iterations + 1
        if use_swap:
            current_dist, current_route = swap(actual_route, number_of_drivers)
        else:
            current_dist, current_route = generate_random_route(data, number_of_drivers, start_town=start_town)
        dist_diff = max(current_dist)-max(actual_dist)
        if dist_diff <= 0:
            actual_dist, actual_route = current_dist, current_route
        else:
            if temperature > 0.1:
                x = (random.randrange(0, 1000))/1000
                if x < math.exp(-dist_diff/temperature):
                    actual_dist, actual_route = current_dist, current_route
        if max(best_dist) > max(actual_dist):
            best_dist, best_route = actual_dist, actual_route
        y.append(max(best_dist))
        temperature = temp_decrease_ratio*temperature
    prop = (test_time * 60) / len(y)
    x_data = []
    for i in range(len(y)):
        x_data.append(i * prop)
    matplotlib.pyplot.plot(x_data, y, label='simulated_annealing, swap: '+str(use_swap))
    matplotlib.pyplot.ylabel('distance')
    matplotlib.pyplot.xlabel('time[ms]')
    print("Simulated Annealing")
    print("Using swap: " + str(use_swap))
    print("Best distance: " + str(best_dist))
    print("Best Route " + str(best_route))
    print("Iterations " + str(iterations))
    return best_dist, best_route


def genetic_algorithm(data: np.array, test_time: float = 1, number_of_drivers: int = 1, population_quantity: int = 10,
                      start_town: int = 0) -> tuple:
    """
    Genetic algorithm implementation
    :param data: distances matrix
    :type data: np.array
    :param test_time: time of testing
    :type test_time: float
    :param number_of_drivers: number of travelers
    :type number_of_drivers: int
    :param population_quantity: number of instances in population
    :type population_quantity: int
    :param start_town: starting_town
    :type start_town: int
    :return: tuple of best distances and routes of each travelers
    :rtype: tuple
    """
    # help functions
    def start_population(num_drivers: int, st_town: int, population_number: int) -> tuple:
        """
        Function to begin genetic algorithm work, initalize first population
        :param num_drivers: number of travelers
        :type num_drivers: int
        :param st_town: starting_town
        :type st_town: int
        :param population_number: number of instances in population
        :type population_number: int
        :return: start population
        :rtype: tuple
        """
        route_population = []
        dist_population = []
        for k in range(population_number):
            new_dist, new_route = generate_random_route(data=data, number_of_drivers=num_drivers, start_town=st_town)
            route_population.append(new_route)
            dist_population.append(new_dist)
        return route_population, dist_population

    def crossing(first_route: list, second_route: list, num_drivers: int) -> tuple:
        """
        Function to crossing two routes to create new one
        :param first_route: first route
        :type first_route: list
        :param second_route: second route
        :type second_route: list
        :param num_drivers: number of travelers
        :type num_drivers: int
        :return: tuple of new route and it's distance
        :rtype: tuple
        """
        start_crossing_index = random.randrange(len(first_route) - 2) + 1
        decision_maker = random.randrange(10)
        if decision_maker > 5:
            new_route = first_route[:start_crossing_index]
            k = 0
            while len(second_route)-1 != k:
                if second_route[k] not in new_route:
                    new_route.append(second_route[k])
                k = k+1
            new_route.append(second_route[-1])
        else:
            k = 0
            new_route = first_route[start_crossing_index:]
            while len(second_route) - 1 != k:
                if second_route[k] not in new_route:
                    new_route = [second_route[k]] + new_route
                k = k + 1
            new_route = [second_route[-1]] + new_route

        new_distance = np.zeros(num_drivers, dtype='float')
        j = -1
        st_town = max(set(new_route), key=new_route.count)  # get the most frequent element
        for k in range((len(new_route) - 1)):
            if new_route[k] == st_town:
                j = j + 1
            new_distance[j] = new_distance[j] + data[new_route[k], new_route[k + 1]]
        return new_distance, new_route

    def new_pop(population_number: int, num_drivers: int, st_town: int,
                elite_rate: float = 0.2, mutation_rate: float = 0.2) -> tuple:
        """
        Function to generate new population
        :param population_number: number of instances in population
        :type population_number: int
        :param num_drivers: number of travelers
        :type num_drivers: int
        :param st_town: starting_town
        :type st_town: int
        :param elite_rate: rate of elite members in population, they must be in new population
        :type elite_rate: float
        :param mutation_rate: rate of mutated members in population
        :type mutation_rate: float
        :return: new population
        :rtype: tuple
        """

        elite_quantity = int(elite_rate * population_number)
        mutation_quantity = int(mutation_rate * population_number)

        # Elite
        new_pop_dist = population_dist[0:elite_quantity]
        new_pop_route = population_route[0:elite_quantity]

        # Mutation
        for _ in range(mutation_quantity):
            new_dist, new_route = generate_random_route(data=data, number_of_drivers=num_drivers, start_town=st_town)
            new_pop_dist.append(new_dist)
            new_pop_route.append(new_route)

        # Random cross for others
        while not (len(new_pop_dist) == len(population_dist)):
            c = random.randrange(len(population_route))
            d = random.randrange(len(population_route))
            new_dist, new_route = crossing(population_route[c], population_route[d], num_drivers=num_drivers)
            new_pop_dist.append(new_dist)
            new_pop_route.append(new_route)
        new_pop_dist, new_pop_route = zip(*sorted(zip(new_pop_dist, new_pop_route), key=lambda x: max(x[0])))
        new_pop_dist = list(new_pop_dist)
        new_pop_route = list(new_pop_route)
        return new_pop_dist, new_pop_route

    # Set start parameters
    iterations = 0
    population_route, population_dist = start_population(num_drivers=number_of_drivers, st_town=start_town,
                                                         population_number=population_quantity)
    iterations = iterations + population_quantity
    # Sortowanie
    population_dist, population_route = zip(*sorted(zip(population_dist, population_route), key=lambda x: max(x[0])))
    population_dist = list(population_dist)
    population_route = list(population_route)
    y = [max(population_dist[0])]
    act_time = time.time()
    while time.time() < act_time + test_time:
        iterations = iterations + population_quantity
        population_dist, population_route = new_pop(population_number=population_quantity,
                                                    num_drivers=number_of_drivers, st_town=start_town)
        y.append(max(population_dist[0]))
    prop = (test_time * 60) / len(y)
    x_data = []
    for i in range(len(y)):
        x_data.append(i * prop)
    matplotlib.pyplot.plot(x_data, y, label='genetic algorithm')
    print("Genetic Algorithm")
    print("Best distance:" + str(population_dist[0]))
    print("Best Route" + str(population_route[0]))
    print("Iterations " + str(iterations))
    return population_dist[0], population_route[0]


def main():
    # To make every time the same result
    np.random.seed(1)
    random.seed(1)

    dt = make_random_matrix(number_of_towns=100)
    drivers = 2
    t_time = 1
    town = 1
    _, _ = random_search(dt, number_of_drivers=drivers, test_time=t_time, start_town=town)
    _, _ = simulated_annealing(dt, number_of_drivers=drivers, test_time=t_time, start_town=town)
    _, _ = simulated_annealing(dt, number_of_drivers=drivers, use_swap=False, test_time=t_time, start_town=town)
    _, _ = genetic_algorithm(dt, number_of_drivers=drivers, test_time=t_time, start_town=town)

    matplotlib.pyplot.legend(loc='upper right', ncol=1)
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
