# City limit
#   <--- X --->
# ----------------
# |              | ^
# |              | |
# |     City     | Y
# |              | |
# |              | v
# ----------------
city_limit_x = 500
city_limit_y = 500

# Station limit
# ----------------
# |              |
# |   X          |
# |--------      |
# |  Sta. | Y    |
# |       |      |
# ----------------
station_limit_x = 100
station_limit_y = 100

# City initial population
city0_population = 100
city1_population = 100

# Possibility that a person shows symptoms after being infected.
show_symptom_possibility = 0.7
# Number of iterations after being infected that starts showing symptoms (if the person will show symptoms at all).
show_symptom_period = 360
# Number of iterations after being infected that the virus disappear.
virus_active_period = 840
# Number of iterations for a standard quarantine.
quarantine_period = 1200

# Infection probabilities under different situations.
infection_prob = dict(
    # {infected object} _ {targeted object}
    masked_masked=0.02,
    masked_unmasked=0.05,
    unmasked_masked=0.2,
    unmasked_unmasked=0.6,
    quarantined=0.005
)

# Number of iteration for each simulation round
max_iter = 3000

# Number of rounds
max_round = 30

# Trains departure iter number (multiple of)
trains_departure_iter = 200

# Print iteration info (multiple of)
iter_print_level = 1000

# Scenario code
# 1: Without any restrictions
# 2: City B quarantines people who shows symptoms
# 3: City B quarantines all travelers from City A
scenario_code = 3

# whether print detail info.
verbose = True
