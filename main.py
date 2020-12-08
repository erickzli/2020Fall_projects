import random
import configfile


class Person:
    def __init__(self, pid, infection, masked, city, max_x, max_y):
        """Initialize the Person object.
        :param infection: Whether the Person is infected in the first place.
        :param masked: Whether the Person is masked.
        """
        self.pid = pid
        self.infection = infection
        self.detected = False
        self.masked = masked
        self.curr_city = city
        self.under_quarantine = False
        self.infected_timestamp = -1
        self.quarantine_timestamp = -1
        self.max_x = max_x
        self.max_y = max_y
        self.curr_x = random.random() * max_x
        self.curr_y = random.random() * max_y
        self.moving_distance = 6

        if infection:
            self.infected_timestamp = 0

    def __repr__(self):
        return self.pid

    def get_infection(self):
        return self.infection

    def get_masked(self):
        return self.masked

    def get_current_location(self):
        return self.curr_x, self.curr_y

    def set_city(self, new_city):
        self.curr_city = new_city

    def get_infected(self, curr_time):
        self.infection = True
        self.infected_timestamp = curr_time

    def ask_for_quarantine(self, curr_time):
        self.under_quarantine = True
        self.quarantine_timestamp = curr_time

    def set_new_location(self, additional_move=0):
        move_goal = self.moving_distance + additional_move

        # When the position is too close to the left edge
        if self.curr_x < move_goal:
            move_x = random.random() * move_goal
        # When the position is too close to the right edge
        elif self.curr_x + move_goal > self.max_x:
            move_x = random.random() * move_goal * -1
        else:
            move_x = (random.random() * 2 - 1) * move_goal

        move_y = (move_goal ** 2 - move_x ** 2) ** 0.5
        # When the position is too close to the lower edge
        if self.curr_y < move_goal:
            pass
        # When the position is too close to the upper edge
        elif self.curr_y + move_goal > self.max_y:
            move_y *= -1
        else:
            move_y *= random.choice([-1, 1])

        self.curr_x += move_x
        self.curr_y += move_y


class City:
    def __init__(self, cid, init_population, init_infection_rate, init_masked_rate, max_x, max_y):
        self.cid = cid
        self.curr_population = init_population
        self.infection_rate = init_infection_rate
        self.real_infection_rate = -1
        self.detected_infection_rate = -1
        self.max_x = max_x
        self.max_y = max_y
        self.people_list = []

        if cid == 0:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                self.people_list.append(Person(i, infected, masked, 0, max_x, max_y))
        else:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                self.people_list.append(Person(10000 * i, infected, masked, 0, max_x, max_y))

    def __repr__(self):
        return self.cid

    def arrival(self, train_list):
        for idx in range(len(train_list)):
            train_list[idx].set_city = 1
        self.people_list.append(train_list)

    def departure(self):
        onboard = []
        for idx, p in enumerate(self.people_list):
            if p.curr_x <= configfile.portal_x and p.curr_y <= configfile.portal_y:
                onboard.append(p)
        self.people_list = [p for p in self.people_list
                            if p.curr_x > configfile.portal_x or p.curr_y > configfile.portal_y]
        return onboard

    def get_curr_population(self):
        self.curr_population = len(self.people_list)
        return self.curr_population

    def get_curr_real_infection_rate(self):
        self.real_infection_rate = sum(p.infection for p in self.people_list) / self.get_curr_population()
        return self.real_infection_rate

    def get_curr_detected_infection_rate(self):
        self.detected_infection_rate = sum(p.detected for p in self.people_list) / self.get_curr_population()
        return self.detected_infection_rate

    def people_move(self):
        for idx, p in enumerate(self.people_list):
            self.people_list[idx].set_new_location()


if __name__ == '__main__':
    city0 = City(0, configfile.city0_population, 0.05, 0.8, 1000, 1000)
    city1 = City(1, configfile.city1_population, 0, 0, 1000, 1000)

    print(city0.get_curr_population())
    print(city1.get_curr_population())

    print(city0.get_curr_real_infection_rate())
    print(city1.get_curr_real_infection_rate())

    for loop_idx in range(configfile.max_time):
        if loop_idx % 100 == 0:
            print(loop_idx)
        city0.people_move()
        city1.people_move()
