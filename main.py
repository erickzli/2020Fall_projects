import random
import configfile
import pandas as pd
import plotly.express as px

SCENARIO_CODE = configfile.scenario_code


class Person:
    def __init__(self, pid, infection, masked, city, max_x, max_y):
        """Initialize the Person object.
        :param infection: Whether the Person is infected in the first place.
        :param masked: Whether the Person is masked.
        """
        self.pid = pid
        self.infected = infection
        self.virus_active = infection
        self.infected_by = -1
        self.detected = False
        self.masked = masked
        self.curr_city = city
        self.under_quarantine = False
        self.will_show_symptom = False
        self.infected_timestamp = -1
        self.detected_timestamp = -1
        self.quarantine_timestamp = -1
        self.recovered = False
        self.max_x = max_x
        self.max_y = max_y
        self.curr_x = random.random() * max_x
        self.curr_y = random.random() * max_y
        self.moving_distance = 6

        if infection:
            self.infected_timestamp = 0

        if random.random() < configfile.show_symptom_possibility:
            self.will_show_symptom = True

    def __repr__(self):
        return self.pid

    def is_infected(self):
        return self.infected

    def is_virus_active(self):
        return self.virus_active

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
        self.virus_active = True
        self.infected_timestamp = curr_time
        self.infected_by = s_pid
        if configfile.verbose:
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
        self.population = init_population
        self.curr_population = init_population
        self.infection_rate = init_infection_rate
        self.real_infection_rate = 0
        self.detected_infection_rate = 0
        self.virus_active_rate = 0
        self.local_real_infection_rate = 0
        self.local_detected_infection_rate = 0
        self.local_virus_active_rate = 0
        self.max_x = max_x
        self.max_y = max_y
        self.train_x = train_x
        self.train_y = train_y
        self.people_list = []

        if cid == 0:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                self.people_list.append(Person(i, infected, masked, self.cid, max_x, max_y))
        else:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                self.people_list.append(Person(10000 + i, infected, masked, self.cid, max_x, max_y))
        if configfile.verbose:
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

        if len(onboard) > 0:
            if configfile.verbose:
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

    def get_curr_virus_active_rate(self):
        self.virus_active_rate = sum(p.virus_active for p in self.people_list) / self.get_curr_population()
        return self.virus_active_rate

    def get_local_curr_real_infection_rate(self):
        self.local_real_infection_rate = sum((p.infected and p.curr_city == self.cid) for p in self.people_list) / \
                                         self.population
        return self.local_real_infection_rate

    def get_local_curr_detected_infection_rate(self):
        self.local_detected_infection_rate = sum((p.detected and p.curr_city == self.cid) for p in self.people_list) / \
                                       self.population
        return self.local_detected_infection_rate

    def get_local_curr_virus_active_rate(self):
        self.local_virus_active_rate = sum((p.virus_active and p.curr_city == self.cid) for p in self.people_list) / \
                                 self.population
        return self.local_virus_active_rate

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
                    if p1.is_virus_active() and not p2.is_virus_active() and not p2.is_infected():
                        if simulate_infection(p1, p2):
                            if p2.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p2.pid)
                                newly_spread_pid_list.append(p1.pid)
                    elif not p1.is_virus_active() and p2.is_virus_active() and not p1.is_infected():
                        if simulate_infection(p2, p1):
                            if p1.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p1.pid)
                                newly_spread_pid_list.append(p2.pid)

        for idx, p in enumerate(self.people_list):
            if p.pid in newly_infected_pid_list:
                spreader_pid = newly_spread_pid_list[newly_infected_pid_list.index(p.pid)]
                self.people_list[idx].get_infected(spreader_pid, curr_loop)

    def update_symptons(self, curr_ts):
        for idx, p in enumerate(self.people_list):
            if p.will_show_symptom and p.infected and curr_ts - p.infected_timestamp == configfile.show_symptom_period:
                self.people_list[idx].detected = True
                self.people_list[idx].detected_timestamp = curr_ts

    def update_infection_status(self, curr_ts):
        for idx, p in enumerate(self.people_list):
            if p.infected and curr_ts - p.infected_timestamp == configfile.virus_active_period:
                self.people_list[idx].virus_active = False

    def update_quarantine_status(self, curr_ts):
        for idx, p in enumerate(self.people_list):
            if p.under_quarantine and curr_ts - p.quarantine_timestamp == configfile.quarantine_period:
                self.people_list[idx].under_quarantine = False

    def put_into_quarantine(self, curr_ts):
        for idx, p in enumerate(self.people_list):
            if p.detected:
                self.people_list[idx].under_quarantine = True
                self.people_list[idx].quarantine_timestamp = curr_ts

    def put_into_quarantine_by_pid(self, curr_ts, pid_list):
        for idx, p in enumerate(self.people_list):
            if p.get_id() in pid_list:
                self.people_list[idx].under_quarantine = True
                self.people_list[idx].quarantine_timestamp = curr_ts


def simulate_infection(infected_p, target_p):
    if infected_p.under_quarantine or target_p.under_quarantine:
        if random.random() < configfile.quarantine_p:
            return True
    elif infected_p.is_masked() and target_p.is_masked():
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


def get_pid_from_list(li):
    return_list = []
    for idx, i in enumerate(li):
        return_list.append(i.get_id())
    return return_list


def one_round(loop_num, dta):
    city0 = City(0, configfile.city0_population, 0.05, 0.5, configfile.city_limit_x, configfile.city_limit_y,
                 configfile.station_limit_x, configfile.station_limit_y)
    city1 = City(1, configfile.city1_population, 0, 0, configfile.city_limit_x, configfile.city_limit_y,
                 configfile.station_limit_x, configfile.station_limit_y)

    if configfile.verbose:
        print(city0.get_curr_population())
        print(city1.get_curr_population())

        print(city0.get_curr_real_infection_rate())
        print(city1.get_curr_real_infection_rate())

    small_counter = 0

    # the big loop: each loop indicates one time unit.
    for loop_idx in range(configfile.max_time):
        if loop_idx % configfile.trains_departure_timestamp == 0:
            trainlist = []
            if SCENARIO_CODE != 4:
                trainlist = city0.departure()
                city1.arrival(trainlist)
            if SCENARIO_CODE == 3:
                trainpid = get_pid_from_list(trainlist)
                city1.put_into_quarantine_by_pid(loop_idx, trainpid)

            real_rate = city1.get_local_curr_real_infection_rate()
            detected_rate = city1.get_local_curr_detected_infection_rate()
            virus_rate = city1.get_local_curr_virus_active_rate()
            if loop_num == 0:
                dta = dta.append({'ts': loop_idx, 'local_real_infection_rate': real_rate,
                                  'local_detected_infection_rate': detected_rate,
                                  'local_virus_active_rate': virus_rate},
                                 ignore_index=True)
            else:
                dta.at[small_counter, 'local_real_infection_rate'] += real_rate
                dta.at[small_counter, 'local_detected_infection_rate'] += detected_rate
                dta.at[small_counter, 'local_virus_active_rate'] += virus_rate
            small_counter += 1

        if configfile.verbose:
            print_loop_number(loop_idx, configfile.loop_print_level)
        city0.people_move()
        city1.people_move()
        city0.intracity_infection(loop_idx)
        city1.intracity_infection(loop_idx)
        city0.update_symptons(loop_idx)
        city1.update_symptons(loop_idx)
        city0.update_infection_status(loop_idx)
        city1.update_infection_status(loop_idx)
        if SCENARIO_CODE == 2 or SCENARIO_CODE == 3:
            city1.put_into_quarantine(loop_idx)
            city1.update_quarantine_status(loop_idx)

    if configfile.verbose:
        print(city0.get_curr_real_infection_rate())
        print(city1.get_curr_real_infection_rate())
        print(city0.get_curr_detected_infection_rate())
        print(city1.get_curr_detected_infection_rate())
        city0.get_infected_pid()
        city1.get_infected_pid()

        print(city0.get_curr_population())
        print(city1.get_curr_population())
        print(dta)

    return dta


if __name__ == '__main__':
    colnames = ['ts', 'local_real_infection_rate', 'local_detected_infection_rate', 'local_virus_active_rate']
    df = pd.DataFrame(columns=colnames)

    for roundn in range(configfile.iteration_num):
        print('Loop at:', roundn)
        df = one_round(roundn, df)

    df = df / [1, configfile.iteration_num, configfile.iteration_num, configfile.iteration_num]
    print(df)
    fig = px.line(df, x='ts', y='local_detected_infection_rate', title='City B Detected Infection Rate')
    fig.show()
