from collections import defaultdict
from player_win_loss import *

#global data structures
pos_to_list_players = defaultdict(set)
identity_to_cost = dict()
identity_to_team = dict()




### file processing from dk ###
pos = ["TOP", "JNG", "MID", "ADC", "SUP", "TEAM"]

def process_dk_lol(filename="DKSalaries.csv"):
	identity_to_cost = dict()
	identity_to_team = dict()
	pos_to_list_players = defaultdict(set)
	
	total_salary = 50000

	with open(filename) as f:
		first_line = True
		for line in f:
			if not first_line:
				split = line.split(",")
				role, identity, cost, team = split[0].strip(), split[2].strip(), int(split[5].strip()), split[-2].strip()
				pos_to_list_players[role].add(identity)

				if identity not in identity_to_cost:
					identity_to_cost[identity] = cost
				
				identity_to_cost[identity] = min(identity_to_cost[identity], cost)
				identity_to_team[identity] = team

			first_line = False

	return identity_to_cost, identity_to_team, pos_to_list_players 



identity_to_cost, identity_to_team, pos_to_list_players = process_dk_lol()


### roster generation

def generate_permutations(list1, list2):
	#list1 and list2 are both lists of lists
	new_list = []
	for i in list1:
		for j in list2:
			item_list = i + j 
			new_list.append(item_list)
	return new_list


def get_all_options():
	options = []
	for key, value in pos_to_list_players.items():
		options += value
	return options


def generate_legitimate_rosters():
	#returns all rosters without taking into consideration salary, team
	#all rosters have captain as last player
	initial = [[]]
	for position in pos:
		new_options = [[i] for i in pos_to_list_players[position]]
		initial = generate_permutations(initial, new_options)

	captain_options = get_all_options()
	new_initial = []

	for temp_solution in initial:
		temp_set = set(temp_solution)
		for j in captain_options:
			if j not in temp_set:
				new_item = temp_solution + [j]
				new_initial.append(new_item)

	return new_initial


def filter_rosters(answers, identity_to_cost, identity_to_team):
	#filter rosters by salary and max 4 per team per roster
	filtered_rosters = []
	for roster in answers:
		salary = [identity_to_cost[i] for i in roster]
		total = 0
		for i in range(len(salary)):
			if i != len(salary) - 1:
				total += salary[i]
			else:
				total += salary[i] * 1.5
		if total < 50000:
			filtered_rosters.append(roster)

	filtered_rosters_2 = []
	for roster in filtered_rosters:
		team_count = dict()
		for i in roster:
			team = identity_to_team[i]
			if team in team_count:
				team_count[team] += 1
			else:
				team_count[team] = 1

		valid = True
		for j in team_count:
			if team_count[j] > 4:
				valid = False
				break

		if valid:
			filtered_rosters_2.append(roster)


	return filtered_rosters_2


def get_team_count_from_roster(roster, identity_to_team):
	#get count per team
	team_count = dict()
	for i in roster:
		team = identity_to_team[i]
		if team not in team_count:
			team_count[team] = 0
		team_count[team] += 1
	return team_count


answers = generate_legitimate_rosters()
legit_rosters = filter_rosters(answers, identity_to_cost, identity_to_team)
print(f"Length of all possible rosters w/o restrictions: {len(answers)}")
print(f"Length of all possible rosters w/ restrictions: {len(legit_rosters)}")
print()


#tournament analysis 

winning_score = 129.62

#make this scrapable, so far for 5/5 MSI playins
results = {
	"BOSS": 13.56,
	"AHaHaCiK": 24.39,
	"Nomanz": 23.31,
	"Gadget": 15.2,
	"SaNTaS": 12.8,
	"Rockky": 5.86,
	"Jjun": 13.42,
	"G4": 15.3,
	"Lloyd": 16.94,
	"PoP": 9.82,
	"Evi": 18.72,
	"Steal": 21.94,
	"Ceros": 39.15,
	"Yutapon": 27.6,
	"Gaeng": 26.58,
	"Tay": 16.92,
	"Shini": 8.06,
	"Envy": 8.34, 
	"Mills": 8.64,
	"RedBert": 2.28,
	"Vega Squadron": 24,
	"INTZ e-Sports": 5,
	"MEGA Esports": 5,
	"DetonatioN FocusMe": 19,
}

def get_winning_rosters_and_scores(results, winning_score):
	winning_rosters = []
	winning_scores = []

	for roster in legit_rosters:
		total = 0
		for i in range(len(roster)):
			if roster[i] in results:
				if i != len(roster) - 1:
					total += results[roster[i]]
				else:
					total += results[roster[i]] * 1.5

		if total > winning_score:
			winning_rosters.append(roster)
			winning_scores.append(total)

	return winning_rosters, winning_scores

winning_rosters, winning_scores = get_winning_rosters_and_scores(results, winning_score)

print(f"Number of winning rosters: {len(winning_rosters)}")
print(f"Average score of winning rosters: {sum(winning_scores)/len(winning_scores)}")
print(f"Percentage of rosters that win: {len(winning_rosters)/len(legit_rosters)}")
print()


### analyzing strategy of drafting winning team

def analyze_top_scores(winning_rosters, winning_scores, top_n=10):
	combo = sorted(list(zip(winning_rosters, winning_scores)), key=lambda x: x[1], reverse=True)
	top_ten = combo[:top_n]
	average_team_comp_top_ten = dict()
	average_player_comp_top_ten = dict()

	for roster, score in top_ten:
		team_count = get_team_count_from_roster(roster, identity_to_team)
		for i in team_count:
			if i not in average_team_comp_top_ten:
				average_team_comp_top_ten[i] = 0
			average_team_comp_top_ten[i] += team_count[i]/len(top_ten)

		for i in roster:
			if i not in average_player_comp_top_ten:
				average_player_comp_top_ten[i] = 0
			average_player_comp_top_ten[i] += 1/len(top_ten)

	return average_team_comp_top_ten, average_player_comp_top_ten


top_n_teams = 50
average_team_comp_top_ten, average_player_comp_top_ten = analyze_top_scores(winning_rosters, winning_scores, top_n_teams)
print(f"Average team comp for top {top_n_teams}: {average_team_comp_top_ten}")
print(f"Average player comp for top {top_n_teams}: {average_player_comp_top_ten}")

list_of_top_players_tuples = sorted([(key, value) for key, value in average_player_comp_top_ten.items()], key=lambda x: x[1], reverse = True)
list_of_top_players = [i[0] for i in list_of_top_players_tuples]

print(list_of_top_players)




def find_best_roster():
	current_max = 0
	current_best_roster = None
	for i in range(len(winning_scores)):
		if winning_scores[i] > current_max:
			current_max = winning_scores[i]
			current_best_roster = winning_rosters[i]

	return current_max, current_best_roster

current_max, current_best_roster = find_best_roster()

team_count = get_team_count_from_roster(current_best_roster, identity_to_team)

print(f"Max score achievable tonight: {current_max}")
#print(f"Best roster possible tonight: {current_best_roster}")
#print(f"Best roster team compositions: {team_count}")


only_two_teams = []
other = []
average_team_comp = {}
average_player_comp = {}

for roster in winning_rosters:
	team_count = get_team_count_from_roster(roster, identity_to_team)

	for i in team_count:
		if i not in average_team_comp:
			average_team_comp[i] = 0
		average_team_comp[i] += team_count[i]

	for i in roster:
		if i not in average_player_comp:
			average_player_comp[i] = 0
		average_player_comp[i] += 1

	if len(team_count) == 2 and "DFM" in team_count and "VEG" in team_count:
		only_two_teams.append(roster)
	else:
		other.append(roster)

for i in average_team_comp:
	average_team_comp[i] = average_team_comp[i] / len(winning_rosters)

for i in average_player_comp:
	average_player_comp[i] = average_player_comp[i] / len(winning_rosters)

only_two_average = 0
for roster in only_two_teams:
	total = 0
	for i in range(len(roster)):
		if roster[i] in results:
			if i != len(roster) - 1:
				total += results[roster[i]]
			else:
				total += results[roster[i]] * 1.5
	only_two_average += total
only_two_average = only_two_average/len(only_two_teams)

other_average = 0
for roster in other:
	total = 0
	for i in range(len(roster)):
		if roster[i] in results:
			if i != len(roster) - 1:
				total += results[roster[i]]
			else:
				total += results[roster[i]] * 1.5
	other_average += total
other_average = other_average/len(other)

print(f"Average of all winning teams rosters: {only_two_average}")
print(f"Average of other rosters average: {other_average}")
print()




print(f"Number of winning rosters that is only winning teams: {len(only_two_teams)}")
print(f"Number of winning rosters that is not just winning teams: {len(other)}")
print(f"Percentage of winning rosters that is only winning teams: {len(only_two_teams)/len(winning_rosters)}")
print(f"Average team composition of winning roster: {average_team_comp}")
print()


roster_pool = []

for roster in legit_rosters:
	team_count = get_team_count_from_roster(roster, identity_to_team)
	if len(team_count) == 2 and "DFM" in team_count and "VEG" in team_count:
		roster_pool.append(roster)

print(f"Number of rosters with winning teams: {len(roster_pool)}")
print(f"Percentage chance of winning from only best teams: {len(only_two_teams)/len(roster_pool)}")


do_not_lookup = {"Vega Squadron", "INTZ e-Sports", "MEGA Esports", "DetonatioN FocusMe"}

predicted = dict()

for player in results:
	if player not in do_not_lookup:
		print(player)
		temp_result = find_win_loss_averages(player)
		team = identity_to_team[player]
		if team == "DFM" or team == "VEG":
			predicted[player] = temp_result[2]
		else:
			predicted[player] = temp_result[-1]

list_of_predicted_top_players_tuples = sorted([(key, value) for key, value in predicted.items()], key=lambda x: x[1], reverse = True)
list_of_predicted_top_players = [i[0] for i in list_of_predicted_top_players_tuples]

print(list_of_predicted_top_players)



