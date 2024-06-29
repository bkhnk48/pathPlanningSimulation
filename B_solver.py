from pyscipopt import Model, quicksum

# Additional function to track running time
import time
import datetime
import os
import sys
time_start = time.time()

# Function to read DIMACS file
def read_dimacs_file(file_name):
    # DIMACS format: p <problem_type> <num_nodes> <num_arcs>
    problem_info = {} # Create a dictionary to store problem information

    # DIMACS format: n <node_id> <flow>
    node_descriptors = [] # Create a list to store node descriptors

    # DIMACS format: a <src> <dst> <low> <cap> <cost>
    arc_descriptors = [] # Create a list to store arc descriptors

    # Store comment for earliness-tardiness problem
    comment_lines = []

    with open(file_name, 'r') as file:
        for line in file:
            # split with delimiter ' '
            line = line.strip().split(' ')
            if line[0] == 'c':
                # store comment line
                comment_lines.append(line)
            elif line[0] == 'p':
                # Parse problem line
                _, problem_type, num_nodes, num_arcs = line
                problem_info['type'] = problem_type
                problem_info['num_nodes'] = int(num_nodes)
                problem_info['num_arcs'] = int(num_arcs)
            elif line[0] == 'n':
                # Parse node descriptor line
                _, node_id, flow = line
                node_descriptors.append((int(node_id), int(flow)))
            elif line[0] == 'a':
                # Parse arc descriptor line
                _, src, dst, low, cap, cost = line
                arc_descriptors.append((int(src), int(dst), int(low), int(cap), int(cost)))
            else:
                # Ignore other lines
                continue
    return problem_info, node_descriptors, arc_descriptors, comment_lines

def read_custom_dimacs(filename): # call the previous function with additional parameter
    # Custom line for earliness-tardiness problem
    #  format: c tw <demand_node> <earliness> <tardiness>
    earliness_tardiness_dict = {}
    problem_info, node_descriptors, arc_descriptors, comment_lines = read_dimacs_file(filename)

    for line in comment_lines: # line is a list eg, ['c', 'tw', '1', '0', '0']
        if line[1] == 'tw':
            _, _, node_id, earliness, tardiness = line
            earliness_tardiness_dict[int(node_id)] = (int(earliness), int(tardiness))

    # sort the node_descriptors and arc_descriptors to dictionary
    node_descriptors_dict = {}
    for i in node_descriptors:
        node_id = i[0]
        flow = i[1]
        node_descriptors_dict[node_id] = flow

    arc_descriptors_dict = {}
    for i in arc_descriptors:
        src = i[0]
        dst = i[1]
        low = i[2]
        cap = i[3]
        cost = i[4]
        arc_descriptors_dict[(src, dst)] = (low, cap, cost)
    return problem_info, node_descriptors_dict, arc_descriptors_dict, earliness_tardiness_dict



# function to divide the node into supply and demand
def divide_node(node_descriptors_dict, arc_descriptors_dict):
    supply_nodes = {}
    demand_nodes = {}
    zero_nodes = {}
    for node, flow in node_descriptors_dict.items():
        if flow > 0:
            supply_nodes[node] = flow
        elif flow < 0:
            demand_nodes[node] = flow

    for node in arc_descriptors_dict:
        if node[0] not in supply_nodes and node[0] not in demand_nodes and node[0] not in zero_nodes:
            zero_nodes[node[0]] = 0
        if node[1] not in supply_nodes and node[1] not in demand_nodes and node[1] not in zero_nodes:
            zero_nodes[node[1]] = 0

    return supply_nodes, demand_nodes, zero_nodes



# function to sort all dictionary
def sort_all_dicts(supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict):
    # sort supply_nodes_dict by node_id from smallest to largest
    supply_nodes_dict = dict(sorted(supply_nodes_dict.items(), key=lambda item: item[0]))

    # sort demand_nodes_dict by node_id from smallest to largest
    demand_nodes_dict = dict(sorted(demand_nodes_dict.items(), key=lambda item: item[0]))

    # sort zero_nodes_dict by node_id from smallest to largest
    zero_nodes_dict = dict(sorted(zero_nodes_dict.items(), key=lambda item: item[0]))

    # sort arc_descriptors_dict by src from smallest to largest, then by dst from smallest to largest
    arc_descriptors_dict = dict(sorted(arc_descriptors_dict.items(), key=lambda item: (item[0][0], item[0][1])))

    return supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict



# model class
class MinimumCostFlowModel:
    def __init__(self, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict):
        self.model = Model("Minimum Cost Flow Problem")
        self.supply_nodes_dict = supply_nodes_dict # {node_id(int): supply(int)}
        self.demand_nodes_dict = demand_nodes_dict # {node_id(int): demand(int)}
        self.zero_nodes_dict = zero_nodes_dict # {node_id(int): 0}
        self.arc_descriptors_dict = arc_descriptors_dict # {(src(int), dst(int)): (low(int), cap(int), cost(int))}
        self.earliness_tardiness_dict = earliness_tardiness_dict # {node_id(int): (earliness(int), tardiness(int))}
        self.z_vars = None
        self.solve_time = None
        self.create_model()
        self.add_constraints()

    def create_model(self):

        # Create indexed dictionaries for variables
        self.vars_dict_index_i = {}
        self.vars_dict_index_j = {}

        # sort the arc_descriptors_dict by src from smallest to largest, then by dst from smallest to largest
        """
        for each arc((i, j), (low, cap, cost))
        create a variable x{supply_node}_{i}_{j}
        sorted by i from smallest to largest, then by j from smallest to largest
        """
        for supply_node in self.supply_nodes_dict:
            for (i, j), _ in self.arc_descriptors_dict.items():
                var_name = f"x{supply_node}_{i}_{j}"
                self.vars_dict_index_i.setdefault(i, []).append(var_name)
                self.vars_dict_index_j.setdefault(j, []).append(var_name)

                self.model.addVar(vtype="B", name=var_name)

        # create variable for earliness and tardiness
        if self.earliness_tardiness_dict != {}:
            self.z_vars = {} # {supply_node: z_var}
            self.z_vars_TW_E = {} # {(supply_node, demand_node): z_var}
            self.z_vars_TW_T = {} # {(supply_node, demand_node): z_var}

            for supply_node in self.supply_nodes_dict:
                z_var_name = f"z{supply_node}"
                self.z_vars[supply_node] = self.model.addVar(vtype="I", name=z_var_name)
                for demand_node, (earliness, tardiness) in self.earliness_tardiness_dict.items():
                    z_var_name_tw_e = f"z{supply_node}TW{demand_node}E"
                    z_var_name_tw_t = f"z{supply_node}TW{demand_node}T"
                    self.z_vars_TW_E[(supply_node, demand_node)] = self.model.addVar(vtype="C", name=z_var_name_tw_e)
                    self.z_vars_TW_T[(supply_node, demand_node)] = self.model.addVar(vtype="C", name=z_var_name_tw_t)

        self.all_vars = self.model.getVars()
        self.all_vars_dict = {var.name: var for var in self.all_vars}

    def add_constraints(self):
        # Constraint 1:
        """
        Theory of constraint 1:
        Limit the flow of each arc to its capacity
        """
        for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
            lst = []
            for supply_node in self.supply_nodes_dict:
                var_name = f"x{supply_node}_{i}_{j}"
                lst.append(self.all_vars_dict[var_name])
            self.model.addCons(quicksum(lst) <= cap)

        # Constraint 2:
        """
        Theory of constraint 2:
        For each supply node, the sum of all arcs out of the supply node must be equal to 1
        """
        for supply_node in self.supply_nodes_dict:
            arc_out = []
            for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                if i == supply_node:
                    #(f"x{supply_node}_{i}_{j}")
                    arc_out.append(f"x{supply_node}_{i}_{j}")
            self.model.addCons(quicksum(self.all_vars_dict[var] for var in arc_out) == 1)


        # Constraint 3:
        """
        Theory of constraint 3:
        For each demand node, the sum of all arcs into the demand node must be equal to 1
        """
        for demand_node in self.demand_nodes_dict:
            arc_in = []
            for supply_node in self.supply_nodes_dict:
                for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                    if j == demand_node:
                        #print(f"x{supply_node}_{i}_{j}")
                        arc_in.append(f"x{supply_node}_{i}_{j}")
            self.model.addCons(quicksum(self.all_vars_dict[var] for var in arc_in) == 1)

        # Constraint 4:
        """
        Theory of constraint 4:
        For each zero node, the sum of all arcs into the zero node must be equal to the sum of all arcs out of the zero node
        """
        for zero_node in self.zero_nodes_dict:
            for supply_node in self.supply_nodes_dict:
                arc_in = []
                arc_out = []
                for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                    if j == zero_node:
                        arc_in.append(f"x{supply_node}_{i}_{j}")
                    if i == zero_node:
                        arc_out.append(f"x{supply_node}_{i}_{j}")
                self.model.addCons(quicksum(self.all_vars_dict[var] for var in arc_in) == quicksum(self.all_vars_dict[var] for var in arc_out))

        # Constraint 5:
        if self.earliness_tardiness_dict != {}:

            # Additional constrain to support
            for supply_node in self.supply_nodes_dict:
                arc_in = []
                arc_out = []
                for (i, j), _ in self.arc_descriptors_dict.items():
                    var_name = f"x{supply_node}_{i}_{j}"
                    if j == supply_node:
                        arc_in.append(self.all_vars_dict[var_name])
                    if i == supply_node:
                        arc_out.append(self.all_vars_dict[var_name])
                self.model.addCons(1 + quicksum(arc_in) == quicksum(arc_out))

            for supply_node in self.supply_nodes_dict:
                arc_in = []
                arc_out = []
                for (i, j), _ in self.arc_descriptors_dict.items():
                    var_name = f"x{supply_node}_{i}_{j}"
                    if j in self.supply_nodes_dict and j != supply_node:
                        arc_in.append(self.all_vars_dict[var_name])
                    if i in self.supply_nodes_dict and i != supply_node:
                        arc_out.append(self.all_vars_dict[var_name])
                self.model.addCons(quicksum(arc_in) == quicksum(arc_out))

            for supply_node in self.supply_nodes_dict:
                z_var = self.z_vars[supply_node]
                total_sum = 0
                # constrain: z{supply_node} == sum of all arcs from supply_node with their cost
                for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                    var_name = f"x{supply_node}_{i}_{j}"
                    total_sum += cost * self.all_vars_dict[var_name]
                self.model.addCons(z_var == total_sum)

                arc_in_t = []
                arc_in_e = []
                for demand_node, (earliness, tardiness) in self.earliness_tardiness_dict.items():
                    z_var_tw_e = self.z_vars_TW_E[(supply_node, demand_node)]
                    z_var_tw_t = self.z_vars_TW_T[(supply_node, demand_node)]


                    # tardingess constraint
                    for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                        if j == demand_node:
                            var_name = f"x{supply_node}_{i}_{j}"
                            arc_in_t.append(self.all_vars_dict[var_name])
                    self.model.addCons(z_var_tw_t >= (z_var - tardiness) * quicksum(arc_in_t))
                    self.model.addCons(z_var_tw_t >= 0)

                    # earliness constraint
                    for (i, j), (low, cap, cost) in self.arc_descriptors_dict.items():
                        if j == demand_node:
                            var_name = f"x{supply_node}_{i}_{j}"
                            arc_in_e.append(self.all_vars_dict[var_name])
                    self.model.addCons(z_var_tw_e >= (earliness*quicksum(arc_in_e) - z_var))
                    self.model.addCons(z_var_tw_e >= 0)





    def solve(self):
        if self.z_vars is not None:
            alpha = 1
            beta = 1
            # quick sum z_vars and multiply with alpha
            z_vars_sum = alpha * quicksum(self.z_vars.values())

            # quick sum z_vars_TW_E and z_vars_TW_T and multiply with beta
            z_vars_TW_E_sum = beta * quicksum(self.z_vars_TW_E.values())
            z_vars_TW_T_sum = beta * quicksum(self.z_vars_TW_T.values())

            self.model.setObjective(z_vars_sum + z_vars_TW_E_sum + z_vars_TW_T_sum, "minimize")
        else:
            self.model.setObjective(quicksum(self.arc_descriptors_dict[(i, j)][2] * self.all_vars_dict[f"x{supply_node}_{i}_{j}"] for supply_node in self.supply_nodes_dict for (i, j) in self.arc_descriptors_dict), "minimize")

        self.model.optimize()
        self.solve_time = self.model.getSolvingTime()


    def output_solution(self):
        if self.model.getStatus() == "optimal":
            print("Run time:", time.time() - time_start, "SEC\n")
            print("Solver time:", self.solve_time)
            print("Optimal value:", self.model.getObjVal())
            print("Solution:")
            # Lấy tất cả các biến từ mô hình
            vars = self.model.getVars()
            # In giá trị của tất cả các biến
            for var in vars:
                if self.model.getVal(var) > 0:
                    print(f"{var.name} = {self.model.getVal(var)}")
        else:
            print("No solution found")


    def save_solution(self, filename):
        # check if output folder exists
        folder = "output_B_solver"
        if not os.path.exists(folder):
            os.makedirs(folder)

        # generate filename base on file input and current time(DD-MM-YYYY_HH-MM-SS)
        filename = filename.split(".")[0] + "_" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
        filename = os.path.join(folder, filename)
        with open(filename, 'w') as f:
            if self.model.getStatus() == "optimal":
                f.write("Run time: " + str(time.time() - time_start) + " SEC\n")
                f.write("Solver time: " + str(self.solve_time) + "\n")
                f.write("Optimal value: " + str(self.model.getObjVal()) + "\n")
                f.write("Solution:\n")
                # Lấy tất cả các biến từ mô hình
                vars = self.model.getVars()
                # In giá trị của tất cả các biến
                for var in vars:
                    if self.model.getVal(var) > 0:
                        f.write(f"{var.name} = {self.model.getVal(var)}\n")
            else:
                f.write("No solution found")


input_file = sys.argv[1]

problem_info, node_descriptors_dict, arc_descriptors_dict, earliness_tardiness_dict = read_custom_dimacs(input_file)

# # test the function
# # dictionary format: {'type': 'min', 'num_nodes': 4, 'num_arcs': 5}
# print(problem_info)
#
# # dictionary format: {node_id(int): demand/supply(int)}
# print(node_descriptors_dict)
#
# # dictionary format: {(src(int), dst(int)): (low(int), cap(int), cost(int))}
# print(arc_descriptors_dict)
#
# # dictionary format: {node_id(int): (earliness(int), tardiness(int))}
# print(earliness_tardiness_dict)


supply_nodes_dict, demand_nodes_dict, zero_nodes_dict = divide_node(node_descriptors_dict, arc_descriptors_dict)

# # test the function
# # dictionary format: {node_id(int): supply(int)}
# print(supply_nodes_dict)
#
# # dictionary format: {node_id(int): demand(int)}
# print(demand_nodes_dict)
#
# # dictionary format: {node_id(int): 0}
# print(zero_nodes_dict)


supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict = sort_all_dicts(supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict)

# print(supply_nodes_dict)
# print(demand_nodes_dict)
# print(zero_nodes_dict)
# print(arc_descriptors_dict)


# test the model
model = MinimumCostFlowModel(supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict)
model.solve()
model.output_solution()
model.save_solution(input_file)