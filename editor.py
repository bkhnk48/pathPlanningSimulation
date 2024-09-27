import random

def random_allocation_with_bounds(total, regions, lower_bound=1, upper_bound=None):
  """
  Randomly allocates a total value among a given number of regions, ensuring values within specified bounds.

  Args:
    total: The total value to be allocated.
    regions: The number of regions.
    lower_bound: The minimum value each region must receive.
    upper_bound: The maximum value each region can receive.

  Returns:
    A list of tuples, where each tuple contains a region number and its allocated value.
  """

  # Ensure the total is feasible within the bounds
  if total < lower_bound * regions or (upper_bound and total > upper_bound * regions):
    raise ValueError("Total value must be within the specified bounds.")

  allocation = []
  remaining = total

  for i in range(1, regions + 1):
    # Determine the maximum possible value for this region
    max_value = min(remaining, upper_bound) if upper_bound else remaining

    # Ensure the value is within the bounds
    value = random.randint(lower_bound, max_value)
    remaining -= value

    allocation.append(("Region_" + str(i), value))

  return allocation


# Example usage:
region_per_list = random_allocation_with_bounds(100, 24, lower_bound=2, upper_bound=5)

# read file Redundant3x3Wards.txt, for each line compare that line to the line in preset list
preset_list = [(3,2,"Region_1"), (10,11,"Region_1"), (5,4,"Region_2"), (12,13,"Region_2"), (7,6,"Region_3"), (14,15,"Region_3"),
               (18,10,"Region_4"), (9,17,"Region_4"), (20,12,"Region_5"), (11,19,"Region_5"), (22,14,"Region_6"), (13,21,"Region_6"), (24,16,"Region_7"), (15,23,"Region_7"),
               (19,18,"Region_16"), (26,27,"Region_16"), (21,20,"Region_17"), (28,29,"Region_17"), (23,22,"Region_18"), (30,31,"Region_18"),
               (34,26,"Region_8"), (25,33,"Region_8"), (36,28,"Region_9"), (27,35,"Region_9"), (38,30,"Region_10"), (29,37,"Region_10"), (40,32,"Region_11"), (31,39,"Region_11"),
               (35,34,"Region_19"), (42,43,"Region_19"), (37,36,"Region_20"), (44,45,"Region_20"), (39,38,"Region_21"), (46,47,"Region_21"),
               (50,42,"Region_12"), (41,49,"Region_12"), (52,44,"Region_13"), (43,51,"Region_13"), (54,46,"Region_14"), (45,53,"Region_14"), (56,48,"Region_15"), (47,55,"Region_15"),
               (51,50,"Region_22"), (58,59,"Region_22"), (53,52,"Region_23"), (60,61,"Region_23"), (55,54,"Region_24"), (62,63,"Region_24")
               ]





with open('Redundant3x3Wards.txt') as f:
    lines = f.readlines()
    new_lines = []
    new_lines_with_region = set()
    for line in lines:
        
        line = line.strip()
        line = line.split(" ") # a(0) <int(1)> <int(2)> <int(3)> <int(4)> <int(5)>
        if line[0] == "a":    
            for item in preset_list:
                if item[0] == int(line[1]) and item[1] == int(line[2]):
                    #print(f"Found {item[2]} in file")
                    line.append(item[2])
                    #print(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]} {line[6]}")
                    #new_lines.add(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]} {line[6]}")
                    new_lines.append(line)
                    break
                else:
                    #new_lines.add(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]}")
                    if line not in new_lines:
                        new_lines.append(line)

    # remove duplicates line which has the same line[1] and line[2] because there are line that has the same line[1] and line[2 but don't have the line[6]
    new_lines = [list(x) for x in set(tuple(x) for x in new_lines)]

    for line in new_lines:
       for region in region_per_list:
            # if line.size() == 7
            if len(line) == 7:
                if line[6] == region[0]:
                    line.append(region[1])
                    #print(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]} {line[6]} {line[7]}")
                    new_lines_with_region.add(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]} {line[6]} {line[7]}")
                    break
            else:
                if f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]}" not in new_lines_with_region:
                    new_lines_with_region.add(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]}")

    for line in new_lines_with_region:
        print(line)
    
    





