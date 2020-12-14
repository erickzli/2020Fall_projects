#!/usr/bin/env python
"""
main.py: where you run the Twin City COVID Monte Carlo Simulation!
Course: IS 597PRO Fall 2020
Author: Erick Li
"""

import random
import configfile
import pandas as pd
import plotly.express as px

# the scenario code (check configfile.py)
SCENARIO_CODE = configfile.scenario_code


class Person:
    def __init__(self, pid, infection, masked, city, max_x, max_y):
        """Initialize the Person object.
        :param pid: person's ID.
        :param infection: whether the Person is infected in the first place.
        :param masked: whether the Person is masked.
        :param city: original city.
        :param max_x: maximal X that the person can get to (same as max X of the city limit)
        :param max_y: maximal Y that the person can get to (same as max Y of the city limit)
        """
        self.pid = pid
        self.infected = infection
        self.virus_active = infection
        self.infected_by = -1
        self.detected = False
        self.masked = masked
        self.curr_city = city
        self.original_city = city
        self.under_quarantine = False
        self.will_show_symptom = False
        self.infected_iter = -1
        self.detected_iter = -1
        self.quarantine_iter = -1
        self.recovered = False
        self.max_x = max_x  # city limit X
        self.max_y = max_y  # city limit Y
        self.curr_x = random.random() * max_x  # initial location X
        self.curr_y = random.random() * max_y  # initial location Y
        self.moving_distance = 6  # default movement distance per iteration

        if infection:
            self.infected_iter = 0

        if random.random() < configfile.show_symptom_possibility:
            self.will_show_symptom = True

    def __repr__(self):
        return self.pid

    def is_infected(self):
        """
        Whether the Person has been infected. Once it changes to True, it won't change back to False.
        :return: boolean value showing if the person has been infected.
        """
        return self.infected

    def is_virus_active(self):
        """
        Whether the Virus is still active.
        :return: boolean value showing if the virus is still active.
        """
        return self.virus_active

    def is_masked(self):
        """
        Whether the Person is masked.
        :return: boolean value showing if the person is masked.
        """
        return self.masked

    def get_id(self):
        """
        Get the Person ID (if the person is from City B, the ID contains 5 digits.
        :return: the person's id
        """
        return self.pid

    def get_current_location(self):
        """
        Get the current location of the Person.
        :return: a list containing the current location of the person.
        """
        return [self.curr_x, self.curr_y]

    def set_curr_city(self, new_city):
        """
        Set the city
        :param new_city: the new city id if the person travel to another city
        :return:
        """
        self.curr_city = new_city

    def get_infected(self, s_pid, curr_iter):
        """
        Indicate the Person is infected.
        :param s_pid: pid of the person who infected the current person.
        :param curr_iter: current iteration.
        :return:
        """
        self.infected = True
        self.virus_active = True
        self.infected_iter = curr_iter
        self.infected_by = s_pid
        if configfile.verbose:
            print('Person', s_pid, 'infected Person', self.get_id())

    def ask_for_quarantine(self, curr_iter):
        """
        The Person will go under quarantine.
        :param curr_iter: current iteration.
        :return:
        """
        self.under_quarantine = True
        self.quarantine_iter = curr_iter

    def set_new_location(self, additional_move=0):
        """
        Randomly set the new location of the Person for each iteration.
        :param additional_move: (optional, default: 0) additional distance per iteration
        :return:
        """
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
        """
        Defines a city
        :param cid: city ID (City A: 0; City B: 1)
        :param init_population: initial population of the city
        :param init_infection_rate: initial infection rate of the city
        :param init_masked_rate: initial mask wearing rate
        :param max_x: city limit (X axis)
        :param max_y: city limit (Y axis)
        :param train_x: station limit (X axis)
        :param train_y: station limit (Y axis)
        """
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
        self.max_x = max_x  # city limit X
        self.max_y = max_y  # city limit Y
        self.train_x = train_x  # train station limit X
        self.train_y = train_y  # train station limit Y
        self.people_list = []  # list of Person objects currently in the city

        # City A
        if cid == 0:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                self.people_list.append(Person(i, infected, masked, self.cid, max_x, max_y))
        # City B
        else:
            for i in range(init_population):
                infected = True if random.random() < init_infection_rate else False
                masked = True if random.random() < init_masked_rate else False
                # pids from City B contain 5 digits
                self.people_list.append(Person(10000 + i, infected, masked, self.cid, max_x, max_y))
        if configfile.verbose:
            print('Initialized City', self.cid)
            self.print_infected_pid()

    def __repr__(self):
        return self.cid

    def arrival(self, train_list):
        """
        When a train arrives, if there are people on the train, accept those people into the city.
        :param train_list: list of Person objects currently onboard.
        :return:
        """
        # Add Person objects from the train_list to the city
        for idx in range(len(train_list)):
            train_list[idx].set_curr_city = 1
        self.people_list += train_list

    def departure(self):
        """
        Remove those people from the city who left by taking the current train. People who are within the station limit
        are considered onboard.
        :return: list of Person objects currently onboard.
        """
        # Remove Person objects within the station limit to the onboard list
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
        """
        Get the current population of the city
        :return: the current population of the city
        """
        self.curr_population = len(self.people_list)
        return self.curr_population

    def get_curr_real_infection_rate(self):
        """
        Get the real infection rate (including those that are not detected but actually infected). Demoninator: current
        population including visitors.
        :return: the current real infection rate.
        """
        self.real_infection_rate = sum(p.infected for p in self.people_list) / self.get_curr_population()
        return self.real_infection_rate

    def get_curr_detected_infection_rate(self):
        """
        Get the detected infection rate. (only including the infected person that have been detected). Denominator:
        current population including visitors.
        :return: the current detected infection rate.
        """
        self.detected_infection_rate = sum(p.detected for p in self.people_list) / self.get_curr_population()
        return self.detected_infection_rate

    def get_curr_virus_active_rate(self):
        """
        Get the current active case rate. (Only including the people who have the virus active in their bodies).
        Denominator: current population including visitors.
        :return: the current virus active rate.
        """
        self.virus_active_rate = sum(p.virus_active for p in self.people_list) / self.get_curr_population()
        return self.virus_active_rate

    def get_local_curr_real_infection_rate(self):
        """
        Get the local real infection rate (including local citizens that are not detected but actually infected).
        Denominator: population of the citizens.
        :return: the current local real infection rate.
        """
        self.local_real_infection_rate = sum(
            (p.infected and p.original_city == self.cid) for p in self.people_list
        ) / self.population
        return self.local_real_infection_rate

    def get_local_curr_detected_infection_rate(self):
        """
        Get the local detected infection rate (including local citizens that are not detected but actually infected).
        Denominator: population of the citizens.
        :return: the current local detected infection rate.
        """
        self.local_detected_infection_rate = sum(
            (p.detected and p.original_city == self.cid) for p in self.people_list
        ) / self.population
        return self.local_detected_infection_rate

    def get_local_curr_virus_active_rate(self):
        """
        Get the local virus active rate (including local citizens that are not detected but actually infected).
        Denominator: population of the citizens.
        :return: the current local virus active rate.
        """
        self.local_virus_active_rate = sum(
            (p.virus_active and p.original_city == self.cid) for p in self.people_list
        ) / self.population
        return self.local_virus_active_rate

    def print_infected_pid(self):
        """
        Print the infected people's ID
        :return:
        """
        print('Infected people: ', end='')
        for idx, p in enumerate(self.people_list):
            if p.is_infected():
                print(p.pid, end=' ')
        print()

    def people_move(self):
        """
        Update the location of every person in the city.
        :return:
        """
        for idx, p in enumerate(self.people_list):
            self.people_list[idx].set_new_location()

    def intracity_infection(self, curr_iter):
        """
        Randomly determine whether a person is infected if they have close contact with someone who is virus-active.
        :param curr_iter: current iteration
        :return:
        """
        newly_infected_pid_list = []
        newly_spread_pid_list = []
        # Calculate the distance between each Person object one-by-one
        for idx1, p1 in enumerate(self.people_list[:-1]):
            for idx2, p2 in enumerate(self.people_list[idx1+1:]):
                location1 = p1.get_current_location()
                location2 = p2.get_current_location()
                distance = calculate_distance(location1, location2)

                # If the distance is smaller than 6 units.
                if distance < 6:
                    # If the virus is active in Person 1, but not active in perviously uninfected Person 2, it is
                    #  possible that Person 1 could infect Person 2.
                    if p1.is_virus_active() and not p2.is_virus_active() and not p2.is_infected():
                        if simulate_infection(p1, p2):
                            if p2.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p2.pid)
                                newly_spread_pid_list.append(p1.pid)
                    # If the virus is active in Person 2, but not active in perviously uninfected Person 1, it is
                    #  possible that Person 2 could infect Person 1.
                    elif not p1.is_virus_active() and p2.is_virus_active() and not p1.is_infected():
                        if simulate_infection(p2, p1):
                            if p1.pid not in newly_infected_pid_list:
                                newly_infected_pid_list.append(p1.pid)
                                newly_spread_pid_list.append(p2.pid)

        # Record all the infections in the current iteration
        for idx, p in enumerate(self.people_list):
            if p.pid in newly_infected_pid_list:
                spreader_pid = newly_spread_pid_list[newly_infected_pid_list.index(p.pid)]
                self.people_list[idx].get_infected(spreader_pid, curr_iter)

    def update_symptoms(self, curr_iter):
        """
        Update the infected people's symptoms based on the symptom period (defined in the configfile.py).
        :param curr_iter: current iteration
        :return:
        """
        for idx, p in enumerate(self.people_list):
            # If the Person could show symptoms, got infected, and it has been show_symptom_period iterations since the
            #  infection, the infected Person got detected.
            if p.will_show_symptom and p.infected and curr_iter - p.infected_iter == configfile.show_symptom_period:
                self.people_list[idx].detected = True
                self.people_list[idx].detected_iter = curr_iter

    def update_infection_status(self, curr_iter):
        """
        Change the virus active people's virus status to False after virus active period (defined in the configfile.py).
        :param curr_iter: current iteration
        :return:
        """
        for idx, p in enumerate(self.people_list):
            # If the Person has been infected, virus active, and it has been virus_active_period iterations since the
            #  infection, the virus becomes inactive.
            if p.infected and p.virus_active and curr_iter - p.infected_iter == configfile.virus_active_period:
                self.people_list[idx].virus_active = False

    def update_quarantine_status(self, curr_iter):
        """
        Change the quarantined people's quarantine status to False after the quarantine period (defined in the
        configfile.py)
        :param curr_iter: current iteration
        :return:
        """
        for idx, p in enumerate(self.people_list):
            # If the Person is under quarantine, and it has been quarantine_period iterations since the quarantine,
            #  change the quarantine status to False.
            if p.under_quarantine and curr_iter - p.quarantine_iter == configfile.quarantine_period:
                self.people_list[idx].under_quarantine = False

    def put_into_quarantine(self, curr_iter):
        """
        Put the detected people within the city to quarantine (change the quarantine status to True).
        :param curr_iter: current iteration
        :return:
        """
        for idx, p in enumerate(self.people_list):
            if p.detected:
                self.people_list[idx].under_quarantine = True
                self.people_list[idx].quarantine_iter = curr_iter

    def put_into_quarantine_by_pid(self, curr_iter, pid_list):
        """
        Put the listed people within the city to quarantine (change the quarantine status to True).
        :param curr_iter: current iteration
        :param pid_list: the list that contains the pid to be quarantined
        :return:
        """
        for idx, p in enumerate(self.people_list):
            if p.get_id() in pid_list:
                self.people_list[idx].under_quarantine = True
                self.people_list[idx].quarantine_iter = curr_iter


def simulate_infection(infected_p, target_p):
    """
    Randomly determine whether the targeted person is infected by the closely contacted virus-active person based on
    the infection probability defined in the configfile.py.
    :param infected_p: Infected Person object
    :param target_p: Targeted Person object
    :return: boolean value whether the person is infected.
    >>> random.seed(123)
    >>> infected = Person(pid=12, infection=True, masked=False, city=0, max_x=100, max_y=100)
    >>> targeted = Person(pid=24, infection=False, masked=False, city=0, max_x=100, max_y=100)
    >>> print(simulate_infection(infected, targeted))
    True
    >>> print(simulate_infection(infected, targeted))
    True
    >>> print(simulate_infection(infected, targeted))
    False
    """
    if infected_p.under_quarantine or target_p.under_quarantine:
        if random.random() < configfile.infection_prob['quarantined']:
            return True
    elif infected_p.is_masked() and target_p.is_masked():
        if random.random() < configfile.infection_prob['masked_masked']:
            return True
    elif infected_p.is_masked() and not target_p.is_masked():
        if random.random() < configfile.infection_prob['masked_unmasked']:
            return True
    elif not infected_p.is_masked() and target_p.is_masked():
        if random.random() < configfile.infection_prob['unmasked_masked']:
            return True
    else:
        if random.random() < configfile.infection_prob['unmasked_unmasked']:
            return True
    return False


def calculate_distance(loc1, loc2):
    """
    Calculate the distance between location 1 and location 2.
    :param loc1: list that contains X and Y coords of location 1.
    :param loc2: list that contains X and Y coords of location 2.
    :return: the distance
    >>> calculate_distance([0, 0], [0, 0])
    0.0
    >>> calculate_distance([2, 4], [5, 3.5])
    3.0413812651491097
    """
    # Calculate the euclidean distance between loc1 and loc2.
    return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5


def print_iter_number(curr_iter, print_level):
    """
    Print the current iteration number when the iteration reaches to the multiple of print_level. E.g., if print_level
    is 2000, the function will print at 0, 2000, 4000, 6000, ...)
    :param curr_iter: current iteration
    :param print_level: when should the print function be executed.
    :return:
    >>> print_iter_number(1000, 2000)
    >>> print_iter_number(4000, 2000)
    Iteration at: 4000
    >>> print_iter_number(3000, 2000.5)
    Traceback (most recent call last):
    ...
    TypeError: print_level must be an integer
    >>> print_iter_number(2000, -2000)
    Traceback (most recent call last):
    ...
    ValueError: print_level must be greater than 0
    """
    if not isinstance(print_level, int):
        raise TypeError('print_level must be an integer')
    if print_level <= 0:
        raise ValueError('print_level must be greater than 0')
    if curr_iter % print_level == 0:
        print('Iteration at:', curr_iter)


def print_pid_from_list(li):
    """
    Print the pid of the Person objects in the list.
    :param li: the list of Person objects.
    :return:
    >>> p1 = Person(pid=12, infection=True, masked=True, city=0, max_x=100, max_y=100)
    >>> p2 = Person(pid=156, infection=True, masked=True, city=0, max_x=100, max_y=100)
    >>> p3 = Person(pid=20003, infection=True, masked=False, city=1, max_x=100, max_y=100)
    >>> plist = [p1, p2, p3]
    >>> print_pid_from_list(plist)
    12 156 20003
    >>> plist_empty = []
    >>> print_pid_from_list(plist_empty)
    <BLANKLINE>
    """
    for idx, i in enumerate(li):
        print(i.get_id(), end=' ')
    print()


def get_pid_from_list(li):
    """
    Return the pid of the Person objects in the list.
    :param li: the list of Person objects.
    :return: a list of pid
    >>> p1 = Person(pid=12, infection=True, masked=True, city=0, max_x=100, max_y=100)
    >>> p2 = Person(pid=156, infection=True, masked=True, city=0, max_x=100, max_y=100)
    >>> p3 = Person(pid=20003, infection=True, masked=False, city=1, max_x=100, max_y=100)
    >>> plist = [p1, p2, p3]
    >>> print(get_pid_from_list(plist))
    [12, 156, 20003]
    """
    return_list = []
    for idx, i in enumerate(li):
        return_list.append(i.get_id())
    return return_list


def one_round(curr_iter, dta):
    """
    Execute one round of the simulation. Update information of the infection rates.
    :param curr_iter: current iteration
    :param dta: a pandas dataframe. Columns: iteration, local real infection rate, local detected infection rate, and
    local virus active rate.
    :return: the updated pandas dataframe.
    """
    city0 = City(0, configfile.city0_population, configfile.city0_init_infection_rate, configfile.city0_masked_rate,
                 configfile.city_limit_x, configfile.city_limit_y, configfile.station_limit_x,
                 configfile.station_limit_y)
    city1 = City(1, configfile.city1_population, configfile.city1_init_infection_rate, configfile.city1_masked_rate,
                 configfile.city_limit_x, configfile.city_limit_y, configfile.station_limit_x,
                 configfile.station_limit_y)

    if configfile.verbose:
        print(city0.get_curr_population())
        print(city1.get_curr_population())

        print(city0.get_curr_real_infection_rate())
        print(city1.get_curr_real_infection_rate())

    small_counter = 0

    # The big iteration: each iteration indicates one time unit.
    for iter_idx in range(configfile.max_iter):
        if iter_idx % configfile.trains_departure_iter == 0:
            trainlist = city0.departure()
            city1.arrival(trainlist)
            # Scenario 3: put everyone off the train into quarantine not matter whether they are infected.
            if SCENARIO_CODE == 3:
                trainpid = get_pid_from_list(trainlist)
                city1.put_into_quarantine_by_pid(iter_idx, trainpid)

            real_rate = city1.get_local_curr_real_infection_rate()
            detected_rate = city1.get_local_curr_detected_infection_rate()
            virus_rate = city1.get_local_curr_virus_active_rate()
            if curr_iter == 0:
                dta = dta.append({'iter': iter_idx, 'local_real_infection_rate': real_rate,
                                  'local_detected_infection_rate': detected_rate,
                                  'local_virus_active_rate': virus_rate},
                                 ignore_index=True)
            else:
                dta.at[small_counter, 'local_real_infection_rate'] += real_rate
                dta.at[small_counter, 'local_detected_infection_rate'] += detected_rate
                dta.at[small_counter, 'local_virus_active_rate'] += virus_rate
            small_counter += 1

        if configfile.verbose:
            print_iter_number(iter_idx, configfile.iter_print_level)
        city0.people_move()
        city1.people_move()
        city0.intracity_infection(iter_idx)
        city1.intracity_infection(iter_idx)
        city0.update_symptoms(iter_idx)
        city1.update_symptoms(iter_idx)
        city0.update_infection_status(iter_idx)
        city1.update_infection_status(iter_idx)
        # Scenarios 2 & 3: Put anyone who shows symptoms to quarantine.
        if SCENARIO_CODE == 2 or SCENARIO_CODE == 3:
            city1.put_into_quarantine(iter_idx)
            city1.update_quarantine_status(iter_idx)

    if configfile.verbose:
        print(city0.get_curr_real_infection_rate())
        print(city1.get_curr_real_infection_rate())
        print(city0.get_curr_detected_infection_rate())
        print(city1.get_curr_detected_infection_rate())
        city0.print_infected_pid()
        city1.print_infected_pid()

        print(city0.get_curr_population())
        print(city1.get_curr_population())
        print(dta)

    return dta


if __name__ == '__main__':
    colnames = ['iter', 'local_real_infection_rate', 'local_detected_infection_rate', 'local_virus_active_rate']
    df = pd.DataFrame(columns=colnames)

    for roundn in range(configfile.max_round):
        print('Iteration at:', roundn)
        df = one_round(roundn, df)

    df = df / [1, configfile.max_round, configfile.max_round, configfile.max_round]
    print(df)
    fig = px.line(df, x='iter', y='local_detected_infection_rate', title='City B Detected Infection Rate')
    fig.show()
