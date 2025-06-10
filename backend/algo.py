import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fitness_function(C, g, x, c):
    """Calculates the fitness (delay) for a given green time and congestion level."""
    try:
        a = (1 - (g / C)) ** 2
        p = 1 - ((g / C) * x)

        # Check for potential division by zero
        if abs(p) < 1e-6:  # Use a small tolerance
            logging.warning("Potential division by zero in fitness_function. Returning a large delay value.")
            return 1e9  # Return a very large value to penalize this solution

        d1i = (0.38 * C * a) / p

        a2 = 173 * (x ** 2)
        ri1 = np.sqrt((x - 1) + (x - 1) ** 2 + ((16 * x) / c))

        d2i = a2 * ri1

        return d1i + d2i

    except Exception as e:
        logging.exception("Error in fitness_function")
        return 1e9  # Penalize heavily on errors

def initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars, road_capacity):
    """Initializes the population with random green times."""
    population = []
    road_congestion = np.array(road_capacity) - np.array(cars)
    road_congestion = road_congestion / np.array(road_capacity)

    while len(population) < pop_size:
        green_times = np.random.randint(green_min, green_max + 1, num_lights)
        if np.sum(green_times) <= cycle_time:
            try:
                total_delay = np.sum([fitness_function(cycle_time, green_times[i], road_congestion[i], road_capacity[i]) for i in range(num_lights)])
                population.append((green_times, total_delay))
            except Exception as e:
                logging.exception("Error calculating total delay during initialization")
                continue  # Try a different set of green times

    return sorted(population, key=lambda x: x[1])

def roulette_wheel_selection(population, total_delays, beta):
    """Selects an individual based on roulette wheel selection."""
    try:
        worst_delay = max(total_delays)
        probabilities = np.exp(-beta * np.array(total_delays) / worst_delay)
        probabilities /= np.sum(probabilities)
        return np.random.choice(len(population), p=probabilities)
    except Exception as e:
        logging.exception("Error in roulette_wheel_selection")
        return np.random.randint(0, len(population))  # Fallback: random selection

def crossover(parent1, parent2, num_lights):
    """Performs crossover between two parents."""
    point = np.random.randint(1, num_lights)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2

def mutate(individual, mutation_rate, green_min, green_max):
    """Mutates an individual."""
    num_lights = len(individual)
    mutated = individual.copy()
    for _ in range(int(mutation_rate * num_lights)):
        idx = np.random.randint(0, num_lights)
        sigma = np.random.choice([-1, 1]) * 0.02 * (green_max - green_min)
        mutated[idx] = np.clip(individual[idx] + sigma, green_min, green_max) # Assign the clipped value back
    return mutated

def inversion(individual, num_lights):
    """Performs inversion on an individual."""
    idx1, idx2 = np.random.randint(0, num_lights, 2)
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
    individual[idx1:idx2+1] = individual[idx1:idx2+1][::-1]
    return individual

def genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars, road_capacity):
    """Runs the genetic algorithm to optimize traffic light timings."""
    population = initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars, road_capacity)
    if not population:
        logging.error("Initial population is empty. Check parameters and fitness function.")
        return None, []

    best_sol = population[0]
    best_delays = [best_sol[1]]

    road_congestion = np.array(road_capacity) - np.array(cars)
    road_congestion = road_congestion / np.array(road_capacity)

    for iteration in range(max_iter):
        total_delays = [ind[1] for ind in population]
        new_population = []

        while len(new_population) < pop_size:
            i1 = roulette_wheel_selection(population, total_delays, beta)
            i2 = roulette_wheel_selection(population, total_delays, beta)

            parent1, parent2 = population[i1][0], population[i2][0]
            child1, child2 = crossover(parent1, parent2, num_lights)

            if np.sum(child1) <= cycle_time:
                child1 = mutate(child1, mutation_rate, green_min, green_max)
                child1 = np.clip(child1, green_min, green_max)
                try:
                    total_delay = np.sum([fitness_function(cycle_time, child1[i], road_congestion[i], road_capacity[i]) for i in range(num_lights)])
                    new_population.append((child1, total_delay))
                except:
                    logging.exception("Error in calculating total delay in child1")

            if np.sum(child2) <= cycle_time:
                child2 = mutate(child2, mutation_rate, green_min, green_max)
                child2 = np.clip(child2, green_min, green_max)
                try:
                    total_delay = np.sum([fitness_function(cycle_time, child2[i], road_congestion[i], road_capacity[i]) for i in range(num_lights)])
                    new_population.append((child2, total_delay))
                except:
                    logging.exception("Error in calculating total delay in child2")

        # Apply inversion
        while len(new_population) < pop_size:
            i = np.random.randint(0, len(population))
            individual = inversion(population[i][0], num_lights)
            if np.sum(individual) <= cycle_time:
                individual = mutate(individual, mutation_rate, green_min, green_max)
                try:
                    total_delay = np.sum([fitness_function(cycle_time, individual[i], road_congestion[i], road_capacity[i]) for i in range(num_lights)])
                    new_population.append((individual, total_delay))
                except:
                    logging.exception("Error in calculating total delay after inversion")

        # Merge and select the best population
        population += new_population
        population = sorted(population, key=lambda x: x[1])[:pop_size]
        
        if population[0][1] < best_sol[1]:
            best_sol = population[0]
        
        best_delays.append(best_sol[1])
        logging.info(f"Iteration {iteration}: Best Total Delay = {best_sol[1]}")
        logging.info(f"Green Times: North = {best_sol[0][0]}, South = {best_sol[0][1]}, West = {best_sol[0][2]}, East = {best_sol[0][3]}")
    
    return best_sol, best_delays

def optimize_traffic(cars):
    """Optimizes traffic light timings using a genetic algorithm."""
    # Default parameters
    pop_size = 400
    num_lights = 4
    max_iter = 25
    green_min = 10
    green_max = 60
    cycle_time = 160 - 12
    mutation_rate = 0.02
    pinv = 0.2
    beta = 8
    road_capacity = [20] * num_lights  # Example road capacities

    try:
        # Run Genetic Algorithm with default parameters
        best_sol, best_delays = genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars, road_capacity)

        if best_sol is None:
            logging.error("Genetic algorithm failed to find a valid solution.")
            return None

        # Convert numpy types to standard Python types
        result = {
            'north': int(best_sol[0][0]),
            'south': int(best_sol[0][1]),
            'west': int(best_sol[0][2]),
            'east': int(best_sol[0][3])
        }

        logging.info('Optimal Solution:')
        logging.info(f'North Green Time = {result["north"]} seconds')
        logging.info(f'South Green Time = {result["south"]} seconds')
        logging.info(f'West Green Time = {result["west"]} seconds')
        logging.info(f'East Green Time = {result["east"]} seconds')

        return result
    
    except Exception as e:
        logging.exception("Error in optimize_traffic")
        return None
