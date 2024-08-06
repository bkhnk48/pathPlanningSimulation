import random
import numpy as np
import math
class Lobby:
    def __init__(self, N, speeds=None, distribution=None):
        self.speeds = speeds if speeds is not None else [1] * N
        self.distribution = distribution if distribution is not None else [1/len(self.speeds)] * len(self.speeds)
        self.agv_ids = []
        self.entry_times = []
        self.exit_times = []
        self.people = []
        self.itineraries = []

    def generate_people(self, L, N):
        # Normalize distribution to sum to 1
        distribution = np.array(self.distribution)
        distribution = distribution / distribution.sum()

        # Generate N = N/2 people with random x coordinates in the range from 0 to L
        # and assign each person a speed from the speeds list according to the distribution
        self.people = []
        total_people = 0
        num_people = [0]*len(self.speeds)
        for i in range(len(self.speeds)):
            if i != len(self.speeds) - 1:
                num_people[i] = int(N * distribution[i] / 2)
                total_people += num_people[i]
            else:
                # Assign the remaining people to the last group
                num_people[i] = N // 2 - total_people
            for _ in range(num_people[i]):
                # Randomly select a distribution type
                dist_type = np.random.choice(["poisson", "student", "uniform"])

                if dist_type == "poisson":
                    lam = L/2
                    random_number = np.random.poisson(lam=lam)
                    x_cord = min(random_number, L)
                elif dist_type == "student":
                    df = 6  # degrees of freedom
                    random_number = np.random.standard_t(df=df)
                    x_cord = L * (random_number - np.floor(random_number))  # map to [0, L]
                else:  # uniform distribution
                    x_cord = np.random.uniform(0, L)

                self.people.append(Person(x_cord, 0, self.speeds[i], 1))

    def calculate_time(self, L, D, robot, N, enter_time, printOut = True):
        self.generate_people(L, N)
        if(printOut):
            print(self.distribution)
            print(f"{num_people} {np.sum(num_people)} while N = {N/2}")
            print(f"Toa do x: {[person.x for person in people]}")
            print(f"Van toc v: {[person.speed for person in people]}")
            
        time = 0
        v = robot.speed
        x0 = robot.x
        for person in self.people:
            # Calculate the time for the person to cross the robot's path
            t = abs(robot.y - person.y) / person.speed
            # Calculate the robot's position at that time
            robot_x = x0 + robot.speed * (t + time)
            # Check if the robot is in the person's safe zone
            if person.x - person.safe_zone/2 < robot_x < person.x + person.safe_zone/2:
                # If so, the robot has to stop until the person has passed
                time += t
                robot.speed = 0
            else:
                # If not, the robot continues to move
                robot.speed = v
        robot.speed = v
        # Add the remaining time for the robot to move the rest of the way
        time += (L + robot.length - robot.x) / v
        exit_time = time + enter_time
        #self.itineraries.append([robot.id, enter_time, exit_time])
        self.merge_itinerary(robot.id, enter_time, exit_time)
        return exit_time
    def merge_itinerary(self, new_id, new_enter_time, independent_exit_time):
        new_itineraries = []
        for itinerary in self.itineraries:
            id, enter_time, exit_time = itinerary
            if exit_time < new_enter_time:
                continue
            if enter_time < new_enter_time and id != new_id:
                delta = exit_time - self.shortest_time
                independent_exit_time += delta
            new_itineraries.append(itinerary)
        self.itineraries = new_itineraries
        self.itineraries.append([new_id, new_enter_time, independent_exit_time])
        return independent_exit_time