import random
import configfile


class Person:
    def __init__(self, pid, infection, masked, city, max_x, max_y):
        """Initialize the Person object.
        :param infection: Whether the Person is infected in the first place.
        :param masked: Whether the Person is masked.
        """
        self.pid = pid
        self.infected = infection
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

    def is_infected(self):
        return self.infected

    def is_masked(self):
        return self.masked

    def get_id(self):
        return self.pid

    def get_current_location(self):
        return [self.curr_x, self.curr_y]

    def set_city(self, new_city):
        self.curr_city = new_city

    def get_infected(self, s_pid, curr_time):
        self.infected = True
        self.infected_timestamp = curr_time
        print('Person', s_pid, 'infected Person', self.get_id())

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
    def __init__(self, cid, init_population, init_infection_rate, init_masked_rate, max_x, max_y, train_x, train_y):
        self.cid = cid
        self.curr_population = init_population
        self.infection_rate = init_infection_rate
        self.real_infection_rate = -1
        self.detected_infection_rate = -1
        self.max_x = max_x
        self.max_y = max_y
        self.train_x = train_x
        self.train_y = train_y
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
                self.people_list.append(Person(10000 + i, infected, masked, 0, max_x, max_y))
        print('Initialized City', self.cid)
        self.get_infected_pid()

    def __repr__(self):
        return self.cid

    def arrival(self, train_list):
        for idx in range(len(train_list)):
            train_list[idx].set_city = 1
        self.people_list += train_list

    def departure(self):
        onboard = []
        for idx, p in enumerate(self.people_list):
            if p.curr_x <= self.train_x and p.curr_y <= self.train_y:
                onboard.append(p)
        self.people_list = [p for p in self.people_list
                            if p.curr_x > self.train_x or p.curr_y > self.train_y]

        print('Train passengers: ', end='')
        print_pid_from_list(onboard)
        return onboard

    def get_curr_population(self):
        self.curr_population = len(self.people_list)
        return self.curr_population

    def get_curr_real_infection_rate(self):
        self.real_infection_rate = sum(p.infected for p in self.people_list) / self.get_curr_population()
        return self.real_infection_rate

    def get_curr_detected_infection_rate(self):
        self.detected_infection_rate = sum(p.detected for p in self.people_list) / self.get_curr_population()
        return self.detected_infection_rate

    def get_infected_pid(self):
        print('Infected people: ', end='')
        for idx, p in enumerate(self.people_list):
            if p.is_infected():
                print(p.pid, end=' ')
        print()

    def people_move(self):
        """
        Update people's location in the city.
        :return:
        """
        for idx, p in enumerate(self.people_list):
            self.people_list[idx].set_new_location()

    def intracity_infection(self, curr_loop):
        newly_infected_pid_list = []
        newly_spread_pid_list = []
        for idx1, p1 in enumerate(self.people_list[:-1]):
            for idx2, p2 in enumerate(self.people_list[idx1+1:]):
                location1 = p1.get_current_location()
                location2 = p2.get_current_location()
                distance = calculate_distance(location1, location2)

                if distance < 6:
                    if p1.is_infected() and not p2.is_infected():
                        if simulate_infection(p1, p2):
                            if p2.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p2.pid)
                                newly_spread_pid_list.append(p1.pid)
                    elif not p1.is_infected() and p2.is_infected():
                        if simulate_infection(p2, p1):
                            if p1.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p1.pid)
                                newly_spread_pid_list.append(p2.pid)

        for idx, p in enumerate(self.people_list):
            if p.pid in newly_infected_pid_list:
                spreader_pid = newly_spread_pid_list[newly_infected_pid_list.index(p.pid)]
                self.people_list[idx].get_infected(spreader_pid, curr_loop)


def simulate_infection(infected_p, target_p):
    if infected_p.is_masked() and target_p.is_masked():
        if random.random() < configfile.infection_rate['masked_masked']:
            return True
    elif infected_p.is_masked() and not target_p.is_masked():
        if random.random() < configfile.infection_rate['masked_unmasked']:
            return True
    elif not infected_p.is_masked() and target_p.is_masked():
        if random.random() < configfile.infection_rate['unmasked_masked']:
            return True
    else:
        if random.random() < configfile.infection_rate['unmasked_unmasked']:
            return True
    return False


def calculate_distance(loc1, loc2):
    return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5


def print_loop_number(loop_num, print_level):
    if loop_num % print_level == 0:
        print('Loop at: ', loop_num)


def print_pid_from_list(li):
    for idx, i in enumerate(li):
        print(i.get_id(), end=' ')
    print()


if __name__ == '__main__':
    city0 = City(0, configfile.city0_population, 0.05, 0.8, configfile.city_limit_x, configfile.city_limit_y,
                 configfile.station_limit_x, configfile.station_limit_y)
    city1 = City(1, configfile.city1_population, 0, 0, configfile.city_limit_x, configfile.city_limit_y,
                 configfile.station_limit_x, configfile.station_limit_y)

    print(city0.get_curr_population())
    print(city1.get_curr_population())

    print(city0.get_curr_real_infection_rate())
    print(city1.get_curr_real_infection_rate())

    # the big loop: each loop indicates one time unit.
    for loop_idx in range(configfile.max_time):
        if (loop_idx + 1) % configfile.trains_departure_timestamp == 0:
            print('Train departs')
            trainlist = city0.departure()
            city1.arrival(trainlist)

        print_loop_number(loop_idx, configfile.loop_print_level)
        city0.people_move()
        city1.people_move()
        city0.intracity_infection(loop_idx)
        city1.intracity_infection(loop_idx)

    print(city0.get_curr_real_infection_rate())
    print(city1.get_curr_real_infection_rate())
    city0.get_infected_pid()
    city1.get_infected_pid()
