from numpy import *
import random
from os.path import basename, splitext
import copy

EXCESS_PENALTY = 100

class CVRP():
    
    
    def get_problem_optimization_sense(self):
        MIN = -1
        MAX = 1
        
        return MIN
    
    
    def get_instances_dir(self):
        return '../cvrp_instances/'
    
    
    def get_problem_name(self):
        return 'CVRP'
    
    
    def read_instance_data(self, file):
        # Get num of vertices
        line = file.readline()

        # Parse number of trucks
        while not line.startswith('COMMENT'): line = file.readline()
        K_prefix_str = 'No of trucks:'
        K_begin = line.index(K_prefix_str) + len(K_prefix_str)
        K_end = line.index(',', K_begin)
        K = eval(line[K_begin:K_end])
        
        # Parse number of vertices
        while not line.startswith('DIMENSION'): line = file.readline()
        num_vertices = eval(line.split().pop())
        
        # Parse vehicles capacity
        while not line.startswith('CAPACITY'): line = file.readline()
        capacity = eval(line.split().pop())
        
        # Parse vertices coordinates
        coordinates = []
        while not line.startswith('NODE_COORD_SECTION'): line = file.readline()
        line = file.readline()
        while not line.startswith('DEMAND_SECTION'):
            [id, x, y] = line.split()
            coordinates.append((float(x), float(y)))
            line = file.readline()
        
        # Parse vertices demands
        demands = zeros(num_vertices, dtype=int)
        line = file.readline()
        while not line.startswith('DEPOT_SECTION'):
            [id, q] = line.split()
            id, q = eval(id), eval(q)
            id -= 1 # Input is 1-indexed while representation is 0-indexed
            demands[id] = float(q)
            line = file.readline()
        
        
        D = zeros((num_vertices, num_vertices), dtype=int)
        
        # Calculate distances between vertices
        for u in range(num_vertices):
            for v in range(num_vertices):
                (x_u, y_u) = coordinates[u]
                (x_v, y_v) = coordinates[v]
                D_uv = round(sqrt(((x_v - x_u)**2) + ((y_v - y_u)**2)))
                D[u,v] = D_uv
                D[v,u] = D_uv
        
        instance_data = (num_vertices, coordinates, D, capacity, demands, K)
        return instance_data
    
    
    def read_problem_set_file(self, file_path):
        (problem_set_name, ext) = splitext(basename(file_path))
        
        file = open(file_path, 'r')
        
        instance_name = problem_set_name
        instance_data = self.read_instance_data(file)
        (num_vertices, coordinates, D, capacity, demands, K) = instance_data
        
        instance = CVRPInstance(self, instance_name, num_vertices, coordinates,
                                D, capacity, demands, K)
        
        return [instance]
    
    
    def get_opt_value(self, instance_name):
        map = {'cvrp-1-1288' : 1288,
               'cvrp-2-1272' : 1272}
        
        if not instance_name in map:
            return None
        else:
            return map[instance_name]


class CVRPInstance():
    
    
    def __init__(self, problem, name, num_vertices, coordinates,
                 D, capacity, demands, K):
        self.problem = problem
        self.name = name
        self.num_vertices = num_vertices
        self.coordinates = coordinates
        self.D = D
        self.capacity = capacity
        self.demands = demands
        self.K = K
    
    
    def get_problem_size(self):
        return self.num_vertices
    

    def improve_route(self, route):
        """ Improve the route using a 2-opt heuristic. Changes the route
            in-place and returns the improvement in the length of the route.
        """
        improvement = 0
        
        size = len(route)

        improving = True
        while improving:
            improving = False
            
            # For each pair of non-contiguous edges (a, c), (b, d)
            for i in range(size - 2):
                a, c = route[i], route[i + 1]
                for j in range(i + 2, size - 1):
                    b, d = route[j], route[j + 1]

                    # Calculate improvement for removing those edges and
                    # substituting for the other edges that close the tour
                    delta = + self.D[a, b] + self.D[c, d] \
                            - self.D[a, c] - self.D[b, d]
                    
                    if delta < 0:
                        # Perform 2-opt move.
                        """
                        for k in range((j-i) / 2):
                            route[i + 1 + k], route[j - k] = route[j - k], route[i + 1 + k]
                        """
                        subroute = route[(i + 1):(j + 1)]
                        subroute.reverse()
                        route[(i + 1):(j + 1)] = subroute
                        #"""
                        improving = True
                        improvement += delta
                        break
                if improving: break

        return improvement
    
    
    def improve_to_opt_route(self, route):
        """ Solves the route to optimality using a dynamic programming
            algorithm. Changes the route in-place and returns the improvement
            in the length of the route.
        """ 
        if len(route) < 2:
            return 0
        
        # Calculate value of the route to be optimized
        value = 0
        for i in range(len(route) - 1):
            value += self.D[route[i], route[i + 1]]
        value += self.D[route[-1], route[0]]
        
        S = set(route)
        S.discard(0) # Discard the depot
        S = frozenset(S) # Use frozenset so that it can be hashable
        
        best_route, best_value = None, None
        
        self.opt_paths.clear()
        
        # Select argmin_i{OPT[S, i] + d_i0}
        for i in S:
            subpath, subpath_value = self.opt_subpath(S, i)
            route_value = subpath_value + self.D[i, 0]
            
            if best_value == None or route_value < best_value:
                best_value = route_value
                best_route = subpath
        
        # Update the route
        route[:] = best_route[:]
        
        improvement = best_value - value
        return improvement
    
    
    opt_paths = {} # Mapping for "memoizing" the optimal subpaths
    
    def opt_subpath(self, S, i):
        """ Calculates the value of the shortest path that starts at the depot,
            visits all customers in S - {i} and stops at customer i.
            Returns the path and its length. 
        """
        if (S, i) not in self.opt_paths:
            
            # Base of recursion is when S == {i}
            if len(S) == 1:
                self.opt_paths[(S, i)] = ([0, i], self.D[0, i])
            
            else:
                best_path, best_value = None, None
                S_minus_i = S - set([i])
                
                # Select argmin_j{OPT[S - {i}, j] + d_ji}
                for j in S_minus_i:
                    subpath, subpath_value = self.opt_subpath(S_minus_i, j)
                    path_value = subpath_value + self.D[j, i]
                    
                    if best_value == None or path_value < best_value:
                        best_path = subpath + [i]
                        best_value = path_value
            
                self.opt_paths[(S, i)] = (best_path, best_value)
        
        return self.opt_paths[(S, i)]
    
    
    def removal_cost(self, customer, route, remaining_capacity):
        """ Calculate cost of removing customer from a vehicle route """
        cost = 0
        
        # Calculate penalty difference of changing the used capacity
        if remaining_capacity < 0:
            excess_delta = max(-self.demands[customer],
                               remaining_capacity)
            cost += excess_delta * EXCESS_PENALTY
        
        tmp_route = list(route)
        
        # Removing this from the old route would cost
        # - c((v_(i-1), v_i)) - c((v_i, v_(i + 1))) + c((v_(i-1), v_(i + 1)))
        idx = tmp_route.index(customer)
        previous = tmp_route[idx - 1]
        next = tmp_route[(idx + 1) % len(tmp_route)]
        cost += self.D[previous, next] \
                - self.D[previous, customer] \
                - self.D[customer, next]
        
        # But the move cost can be improved with route optimization
        tmp_route.pop(idx)
        cost += self.improve_route(tmp_route)
        
        return cost
    
    
    def insertion_cost(self, customer, route, remaining_capacity):
        """ Calculate cost of inserting customer into a vehicle route """
        cost = 0
        
        # Calculate penalty difference of changing the used capacity
        remaining_capacity = (remaining_capacity
                              - self.demands[customer])
        if remaining_capacity < 0:
            excess_delta = min(self.demands[customer],
                               -remaining_capacity)
            cost += excess_delta * EXCESS_PENALTY
        
        tmp_route = list(route)

        # Inserting this customer at the end of the route would cost
        # - c((v_n, v_0)) + c((v_n, customer)) + c((customer, v_0))
        cost += self.D[tmp_route[-1], customer] \
                + self.D[customer, tmp_route[0]] \
                - self.D[tmp_route[-1], tmp_route[0]]
        
        # But the move cost can be improved with route optimization
        tmp_route.append(customer)
        cost += self.improve_route(tmp_route)

        return cost
    
    
    def generate_random_solution(self):
        customers = list(range(1, self.num_vertices))
        random.shuffle(customers)
        routes = [[] for vehicle in range(self.K)]
        remaining_capacity = ones(self.K, dtype=int) * self.capacity
        customer_allocation = zeros(self.num_vertices, dtype=int)
        customer_allocation[0] = -1
        
        for vehicle in range(self.K):
            remaining_capacity[vehicle] = self.capacity
            
            # Try to feasibly add customers to the vehicle
            for id in customers:
                q = self.demands[id]
                # If there is remaining capacity, or it is the last vehicle
                if q <= remaining_capacity[vehicle] or vehicle == (self.K - 1):
                    routes[vehicle].append(id)
                    customer_allocation[id] = vehicle
                    remaining_capacity[vehicle] -= q

            # Remove from the list the customers actually added
            for id in routes[vehicle]:
                customers.remove(id)
            
            # Add the depot to the start of the route
            routes[vehicle].insert(0, 0)
            
            # Optimize the route
            self.improve_route(routes[vehicle])

        solution = CVRPSolution(self, customer_allocation, routes,
                                remaining_capacity)
        return solution
    
    
    def generate_greedy_randomized_solution(self, k):
        return self.generate_random_solution()
    
    
    def generate_all_moves(self):
        return range(1, self.num_vertices)


class CVRPSolution():
    
    
    def __init__(self, instance, customer_allocation, routes,
                 remaining_capacity):
        self.customer_allocation = customer_allocation
        self.instance = instance
        self.routes = routes
        self.remaining_capacity = remaining_capacity
    
    
    def __copy__(self):
        return CVRPSolution(self.instance,
                            self.customer_allocation.copy(),
                            copy.deepcopy(self.routes),
                            self.remaining_capacity.copy())
    
    
    def __deepcopy__(self):
        return self.__copy__()
    
    
    def __str__(self):
        routes_str = ''
        for vehicle in range(len(self.routes)):
            routes_str += 'routes[' + str(vehicle) + ']='
            route = self.routes[vehicle]
            for i in range(len(route)):
                routes_str += str(route[i]) + ','
            routes_str += '\n'
        return routes_str
    
    
    def draw_solution(self):
        return
    
    
    def calculate_report_value(self):
        return self.calculate_value()
    
    
    def calculate_value(self):
        value = 0
        
        for vehicle in range(len(self.routes)):
            route = self.routes[vehicle]
            
            # Calculate penalty for exceeding the capacity
            if self.remaining_capacity[vehicle] < 0:
                value += (-self.remaining_capacity[vehicle]) * EXCESS_PENALTY
            
            # Add weights of edges linking consecutive vertices in the route
            for i in range(len(route) - 1):
                value += self.instance.D[route[i], route[i + 1]]
            
            # Add the weight of the returning edge
            value += self.instance.D[route[-1], route[0]]
        
        return value
    
    
    def best_vehicle_change(self, customer):
        """ Choose vehicle different from the current that has the lowest
            cost for insertion of this customer.
        """
        best_vehicle = None
        best_insertion_cost = None
        
        old_vehicle = self.customer_allocation[customer]
        
        for vehicle in range(self.instance.K):
            # Staying in the current vehicle means no change
            if vehicle == old_vehicle: continue
            
            insertion_cost = self.instance.insertion_cost(customer, \
                    self.routes[vehicle], self.remaining_capacity[vehicle])
            
            if best_insertion_cost == None \
                    or insertion_cost < best_insertion_cost:
                best_insertion_cost = insertion_cost
                best_vehicle = vehicle
        
        return (best_vehicle, best_insertion_cost)
        
    
    def calculate_move_delta(self, (customer)):
        # Calculate cost of removing customer from current vehicle
        old_vehicle = self.customer_allocation[customer]
        removal_cost = self.instance.removal_cost(customer, \
                self.routes[old_vehicle], self.remaining_capacity[old_vehicle])
        
        # Identify best different vehicle for inserting the customer
        (new_vehicle, insertion_cost) = self.best_vehicle_change(customer)
        
        move_delta = removal_cost + insertion_cost 
        return move_delta
    
    
    def generate_random_move(self):
        # Get random customer to move
        i = random.randint(1, (self.instance.num_vertices - 1))
        
        delta = self.calculate_move_delta(i)
        return (i, delta)
    
    
    def apply_move(self, (customer)):
        old_vehicle = self.customer_allocation[customer]
        
        # Identify best different vehicle for inserting the customer
        (new_vehicle, insertion_cost) = self.best_vehicle_change(customer)
        
        # Move customer from the old to the new route
        self.customer_allocation[customer] = new_vehicle
        
        # Update remaining capacities
        self.remaining_capacity[old_vehicle] += self.instance.demands[customer]
        self.remaining_capacity[new_vehicle] -= self.instance.demands[customer]
        
        # Update and optimize routes
        self.routes[old_vehicle].remove(customer)
        self.routes[new_vehicle].append(customer)
        self.instance.improve_route(self.routes[old_vehicle])
        self.instance.improve_route(self.routes[new_vehicle])
        
        
    def is_tabu(self, tabu_list, customer):
        return (customer in tabu_list)
    
    
    def append_tabu(self, tabu_list, customer):
        # Add the customer whose vehicle changed to the tabu list
        # to avoid moving it again too early
        tabu_list.append(customer)
