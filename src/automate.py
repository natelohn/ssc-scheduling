import csv, os, random
from core import Stapher, Shift, Schedule, constants
from constraint import Problem, Variable, Domain
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Color, PatternFill, Font, Border, Side



def get_staph_from_csv_file(file):
	staph_file = open(file)
	csv_staph_file = csv.reader(staph_file)
	staph = {}
	staph['all-staph'] = []
	for staph_info in csv_staph_file:
		name = staph_info[0]
		summers = staph_info[1]
		class_year = staph_info[2]
		gender = staph_info[3]
		positions = staph_info[4:]
		stapher = Stapher(name,summers,class_year,gender,positions)
		staph['all-staph'].append(stapher)
		for position in positions:
			if position in staph:
				staph[position].append(stapher)
			else:
				staph[position] = [stapher]
	staph_file.close()
	return staph


def get_shifts_from_csv_file(filename, is_programming):
	shifts_in_file = []
	shifts_file = open(filename)
	csv_shifts_file = csv.reader(shifts_file)
	for shift_info in csv_shifts_file:
		day = int(shift_info[0])
		title = shift_info[1]
		start = float(shift_info[2])
		end = float(shift_info[3])
		ammount = int(shift_info[4])
		for i in range(0,ammount):
			shift = Shift(day, title, start, end, is_programming)
			shifts_in_file.append(shift)
	shifts_file.close()
	return shifts_in_file

def get_shifts(directory):
	shifts = {}
	for category in os.listdir(directory):
		category_dir = directory + '/' + category
		if 'DS' not in category_dir: # need to remove this after putting git magic in
			shifts[category] = {}
			shifts['all-' + category + '-shifts'] = []
			for worker_group in os.listdir(category_dir):
				worker_dir =  category_dir + '/' + worker_group
				if 'DS' not in worker_dir:
					types_for_worker_group = []
					shifts[category][worker_group] = []
					shifts['all-' + worker_group + '-shifts'] = []
					for shift_file in os.listdir(worker_dir):
						if 'DS' not in shift_file:
							file = worker_dir + '/' + shift_file
							shift_type = shift_file[5:-4]
							if category == 'programming':
								shifts_of_type = get_shifts_from_csv_file(file, True)
							else:
								shifts_of_type = get_shifts_from_csv_file(file, False)
							shifts[category][worker_group] += [shift_type]
							shifts['all-' + category + '-shifts'] += shifts_of_type
							shifts['all-' + worker_group + '-shifts'] += shifts_of_type
							shifts[shift_type] = shifts_of_type
							types_for_worker_group.append(shift_type)
					if worker_group in shifts:
						shifts[worker_group] += types_for_worker_group
					else:
						shifts[worker_group] = types_for_worker_group

	return shifts

def get_pairs_to_avoid(file):
	pair_file = open(file)
	csv_pair_file = csv.reader(pair_file)
	pairs = {}
	for pair_info in csv_pair_file:
		name = pair_info[0]
		people_to_avoid_on_off_day = pair_info[1:]
		pairs[name] = people_to_avoid_on_off_day
	pair_file.close()
	return pairs

def get_has_car(file):
	car_file = open(file)
	names = []
	for name in car_file:
		name = name[:-1]
		names.append(name)
	car_file.close()
	return names


# This is a method to see which days position groups can not take off. (i.e. Ski Dock can't be TueWay)
def get_off_day_restrictions(staph, shifts):
	restricted_off_days = {}
	for position in shifts['programming']:
		if position in staph:
			programming = 'all-' + position + '-shifts'
			ammount_of_shifts_at_a_given_time = {}
			for shift in shifts[programming]:
				time_key = str(shift.day) + ' ' + str(shift.start) + '-' +  str(shift.end) # Does not account for overlapping times
				if time_key in ammount_of_shifts_at_a_given_time:
					ammount_of_shifts_at_a_given_time[time_key] += 1
				else:
					ammount_of_shifts_at_a_given_time[time_key] = 1
				if len(staph[position]) - ammount_of_shifts_at_a_given_time[time_key] == 0:
					if position in restricted_off_days:
						restricted_off_days[position].add(shift.day)
					else:
						restricted_off_days[position] = set([shift.day])
					if shift.start >= 16:
						restricted_off_days[position].add(shift.day + 1)
	# off_day_names = ['SatSu','SuMo','MoTue','TueWay','WeThur','StirFry','FriSat','SatSu']
	# for position in restricted_off_days:
	# 	print position, 'can not be...'
	# 	for day in restricted_off_days[position]:
	# 		print '	', off_day_names[day]
	return restricted_off_days

def passes_off_day_restrictions(stapher, off_day, off_day_groups, off_day_restrictions):
	for position in stapher.positions:
		if position in off_day_restrictions:
			if off_day in off_day_restrictions[position]:
				return False
	return True

def get_off_days_score(off_day_groups,pairs_to_avoid):
	scores = {}
	total_score = 0
	for group in off_day_groups:
		count_of_positions = {}
		count_of_gender = {}
		count_of_class_years = {}
		position_overlap = 0
		returner_count = 0
		bad_pair_count = 0
		bad_pairs = []
		for stapher in off_day_groups[group]:
			for other_stapher in off_day_groups[group]:
				if other_stapher.name in pairs_to_avoid[stapher.name]:
					string_one = stapher.name + ',' + other_stapher.name
					string_two = other_stapher.name + ',' + stapher.name
					if string_one not in bad_pairs and string_two not in bad_pairs:
						bad_pair_count += 1
						bad_pairs.append(stapher.name + ',' + other_stapher.name)
			if stapher.is_returner():
				returner_count += 1
			if stapher.class_year in count_of_class_years:
				count_of_class_years[stapher.class_year] += 1
			else:
				count_of_class_years[stapher.class_year] = 1
			if stapher.gender in count_of_gender:
				count_of_gender[stapher.gender] += 1
			else:
				count_of_gender[stapher.gender] = 1
			for position in stapher.positions:
				if position in count_of_positions:
					count_of_positions[position] += 1
					position_overlap += count_of_positions[position]
				else:
					count_of_positions[position] = 1
		majority_class_year = 0
		for class_year in count_of_class_years:
			if count_of_class_years[class_year] >= majority_class_year:
				majority_class_year = count_of_class_years[class_year]
		if (len(off_day_groups[group]) - returner_count) < 0:
			returner_new_balence_score = returner_count - (len(off_day_groups[group]) - returner_count)
		else:
			returner_new_balence_score = (len(off_day_groups[group]) - returner_count) - returner_count
		if 'male' not in count_of_gender or 'female' not in count_of_gender:
			print 'NOT THIS ONE!'
			return 10000000
		if count_of_gender['female'] > count_of_gender['male']:
			majority_gender = 'female'
		else:
			majority_gender = 'male'
		gender_balence = count_of_gender[majority_gender] - (len(off_day_groups[group]) - count_of_gender[majority_gender])
		position_weight = position_overlap *2
		bad_pair_weight = bad_pair_count
		gender_weight = 3
		returner_new_weigt = 5
		class_year_weight = 1
		group_score = (position_overlap * position_weight) + (bad_pair_count * bad_pair_weight) + (gender_balence * gender_weight) + (returner_new_balence_score * returner_new_weigt) + (majority_class_year * class_year_weight)
		total_score += group_score
	return total_score

def make_off_day_master(off_day_group):
	directory = '../output/2017/masters'
	if not os.path.exists(directory):
		os.makedirs(directory)
	filename = directory + '/off_days.csv'
	new_file = open(filename, 'w')
	off_day_names = ['SatSu','SuMo','MoTue','TueWay','WeThur','StirFry','FriSat']
	txt = ''
	for day in off_day_group:
		txt += off_day_names[day]
		for stapher in off_day_group[day]:
			txt += ',' + stapher.name
		txt += '\n'
	new_file.write(txt)
	new_file.close()			

def generate_random_off_day_groups(staph, off_day_restrictions):
	staph_to_be_chosen = list(staph['all-staph'])
	off_day_groups = {}
	tries = 0	
	possible_off_days = [1,2,3,4,5]
	while len(staph_to_be_chosen) > 0:
		stapher = staph_to_be_chosen[random.randint(0, len(staph_to_be_chosen) - 1)]
		shortest_off_day = possible_off_days[0]
		if tries > 1000:
			staph_to_be_chosen = list(staph['all-staph'])
			off_day_groups = {}
			tries = 0
		if passes_off_day_restrictions(stapher, shortest_off_day, off_day_groups, off_day_restrictions):
			if shortest_off_day in off_day_groups:
				off_day_groups[shortest_off_day].append(stapher)
			else:
				off_day_groups[shortest_off_day] = [stapher]
			staph_to_be_chosen.remove(stapher)
			possible_off_days.pop(0) #Removes the shortest off day from the front
			possible_off_days.append(shortest_off_day)#Place the shortest off day at the back
		tries += 1
	return off_day_groups

def schedule_off_days(best_group):
	for day in best_group:
		for stapher in best_group[day]:
			half_off_day = Shift(day - 1,'Off Day',16,23.5,False)
			off_day = Shift(day,'Off Day',6,23.5,False)
			stapher.add_shift(half_off_day)
			stapher.add_shift(off_day)

def make_off_day_statistics(best_group,pairs_to_avoid,off_day_restrictions):
	has_car = get_has_car('../input/past-csv-files/' + year + '/has_car.csv')
	score = get_off_days_score(best_group,pairs_to_avoid)
	statistics = 'GROUPS SCORE: ' + str(score)
	errors = ''
	off_day_names = ['SatSu','SuMo','MoTue','TueWay','WeThur','StirFry','FriSat']
	for day in best_group:
		genders = {}
		summers = {}
		positions = {}
		class_years = {}
		bad_pairs = []
		has_car_on_off_day = []
		for stapher in best_group[day]:
			for position in stapher.positions:
				if position in off_day_restrictions:
					if day in off_day_restrictions[position]:
						errors  += '\n' + stapher.name + ' CAN NOT BE ' + off_day_names[day] + ' BECAUSE THEY ARE ' + position + '\n'
			if stapher.name in has_car:
				has_car_on_off_day.append(stapher.name)
			if stapher.gender in genders:
				genders[stapher.gender].append(stapher)
			else:
				genders[stapher.gender] = [stapher]
			if stapher.summers in summers:
				summers[stapher.summers].append(stapher)
			else:
				summers[stapher.summers] = [stapher]
			if stapher.class_year in class_years:
				class_years[stapher.class_year].append(stapher)
			else:
				class_years[stapher.class_year] = [stapher]
			for position in stapher.positions:
				if position in positions:
					positions[position].append(stapher)
				else:
					positions[position] = [stapher]
			for other_stapher in best_group[day]:
				if other_stapher.name in pairs_to_avoid[stapher.name]:
					string_one = stapher.name + ',' + other_stapher.name
					string_two = other_stapher.name + ',' + stapher.name
					if string_one not in bad_pairs and string_two not in bad_pairs:
						bad_pairs.append(stapher.name + ',' + other_stapher.name)
		statistics += '\n=========== ' + off_day_names[day] + ' ===========\n'
		stapher_count = len(best_group[day])
		statistics += '	' + str(stapher_count) + ' staphers\n'
		statistics += '	Gender Balence: '
		for gender in genders:
			statistics += str(len(genders[gender])) + ' ' +  gender + ', '
		returners = 0
		returner_males = 0
		new_males = 0
		for summer in summers:
			if summer > 0:
				returners += len(summers[summer])
			for stapher in summers[summer]:
				if stapher.gender == 'male':
					if summer > 0:
						returner_males += 1
					else:
						new_males += 1
		new = stapher_count - returners
		returner_females = returners - returner_males
		new_females = new - new_males
		statistics += '\n 	Returner/New Balence: ' + str(new) + ' new & ' + str(returners) + ' returning.'
		statistics += '\n 		' + str(new_females) + ' new females & ' + str(returner_females) + ' returning females.'
		statistics += '\n 		' + str(new_males) + ' new males & ' + str(returner_males) + ' returning males.'
		statistics += '\n 	Class Year:\n'
		for class_year in class_years:
			males_in_class = 0
			for stapher in class_years[class_year]:
				if stapher.gender == 'male':
					males_in_class += 1
			females_in_class = len(class_years[class_year]) - males_in_class
			statistics += '		' + str(len(class_years[class_year])) + ' in ' + str(class_year) + ': ' + str(males_in_class) + ' males, ' + str(females_in_class) + ' females.\n'
		statistics += '\n 	' + str(len(has_car_on_off_day)) + ' people have cars: '
		for name in has_car_on_off_day:
			statistics += name + ','
		statistics += '\n 	' + str(len(bad_pairs)) + ' bad pair(s): '
		for pair in bad_pairs:
			statistics += pair + ', '
		statistics += '\n 	Positions:'
		for position in positions:
			statistics += '\n 		' + str(len(positions[position])) + ' ' + position
	print 'STATS!!!!!!'
	statistics = errors + statistics
	print statistics
	directory = '../output/2017/masters'
	if not os.path.exists(directory):
		os.makedirs(directory)
	filename = directory + '/off_day_stats.txt'
	new_file = open(filename, 'w')
	new_file.write(statistics)
	new_file.close()

def generate_best_groups(staph, off_day_restrictions,pairs_to_avoid):
	lowest_score = 1000
	best_scoring_groups = []
	while lowest_score > 200:
		off_day_groups = generate_random_off_day_groups(staph, off_day_restrictions)
		off_days_score = get_off_days_score(off_day_groups,pairs_to_avoid)
		if off_days_score <= lowest_score:
			print off_days_score
			lowest_score = off_days_score
			best_scoring_groups.append(off_day_groups)
	best_groups = best_scoring_groups[-1]
	return best_groups

def get_groups_from_master(staph):
	off_day_master = open('../output/2017/masters/off_days.csv')
	csv_off_day_file = csv.reader(off_day_master)
	off_day_names = ['SatSu','SuMo','MoTue','TueWay','WeThur','StirFry','FriSat']
	off_day_groups = {}
	for line in csv_off_day_file:
		off_day = off_day_names.index(line[0])
		names = line[1:]
		for stapher in staph['all-staph']:
			if stapher.name in names:
				if off_day in off_day_groups:
					off_day_groups[off_day].append(stapher)
				else:
					off_day_groups[off_day] = [stapher]
	off_day_master.close()
	return off_day_groups

def off_days(staph,off_day_restrictions,pairs_to_avoid):
	# off_day_groups = generate_best_groups(staph, off_day_restrictions,pairs_to_avoid)
	# make_off_day_master(off_day_groups)
	off_day_groups = get_groups_from_master(staph)
	# make_off_day_statistics(off_day_groups,pairs_to_avoid,off_day_restrictions)
	# Must be done before any other shifts scheduled!
	schedule_off_days(off_day_groups)


def get_programming_score(staph_group):
	score = 0
	for stapher in staph_group:
		score += stapher.meal_break_violations()
		if 'ski-dock' in stapher.positions:
			for length in stapher.get_lengths_without_break():
				if length > 3:
					score += 1
	return score

def find_improved_swap(staph_group,shift,score):
	stapher = shift.stapher
	for other_stapher in staph_group:
		if other_stapher.free_during_shift(shift):
			stapher.remove_shift(shift)
			other_stapher.add_shift(shift)
			new_score = get_programming_score(staph_group)
			if new_score < score:
				return new_score
			else:
				other_stapher.remove_shift(shift)
				stapher.add_shift(shift)
	return score

			
def improve_programming(staph_group,programming_shifts):
	for i in range(0,10):
		score = get_programming_score(staph_group)
		for shift in programming_shifts:
			score = find_improved_swap(staph_group,shift,score)
	# for stapher in staph_group:
	# 	if 'ski-dock' in stapher.positions:
	# 		print stapher.name
	# 		for day in stapher.work_times_by_day():
	# 			print '	',day
	# 			for time in stapher.work_times_by_day()[day]:
	# 				print '		',time

			

def automate_programming(staphers, shifts_to_fill):
	shift_tries = 0
	staph_tries = 0
	while len(shifts_to_fill) > 0:
		shift = shifts_to_fill[0]
		stapher = staphers[0]
		if stapher.free_during_shift(shift):
			stapher.add_shift(shift)
			shifts_to_fill.remove(shift)
			staphers.remove(stapher)
			staphers.append(stapher)
			shift_tries = 0
		else:
			shifts_to_fill.remove(shift)
			shifts_to_fill.append(shift)
			shift_tries += 1
		if shift_tries > len(shifts_to_fill):
			staphers.remove(stapher)
			staphers.append(stapher)
			shift_tries = 0
			staph_tries += 1
		if staph_tries > len(staphers):
			print len(shifts_to_fill),'programming shift(s) could not get filled...'
			for shift in shifts_to_fill:
				print '	',shift
			break

def programming(staph,shifts):
	# Stpah D doesn't have programming
	for position in staph:
		if position in shifts:
			staphers = staph[position]
			for shift_type in shifts[position]:
				shifts_to_fill = shifts[shift_type]
				automate_programming(staphers, list(shifts_to_fill))
			all_programming_shifts = shifts['all-' + position + '-shifts']
			improve_programming(staphers,all_programming_shifts)
			# print position + '\'s programming score is', get_programming_score(staphers)
		else:
			print '	------->',position, 'doesn\'t have programming...'
		

def schedule_special_shifts(staph, shifts, constraint_info):
	max_prefference = constraint_info['number_special_shift_types']
	special_shift_types = shifts['special']['all-staph']
	for shift_type in special_shift_types:
		unassigned_shifts = [] + shifts[shift_type]
		current_prefference = 0
		while current_prefference < max_prefference and unassigned_shifts != []:
			for stapher in staph['all-staph']:
				if stapher.special_shift_preferences[current_prefference] == shift_type:
					for shift in unassigned_shifts:
						if passes_all_constraints(shift, stapher, constraint_info):
							stapher.add_shift(shift)
							unassigned_shifts.remove(shift)
							break
			current_prefference += 1

def schedule_programming_shifts(staph, shifts, constraint_info):
	"""
	Here we need to order the shifts to assure that those groups with the smallest number of people in them
	get their required shifts placed first. This is to assure that smaller person groups get all the shifts they 
	have to cover before staphers that hold multiple positions are placed in the automator w/ bigger groups.
	"""
	programming_groups = shifts['programming']
	ordered_groups = []
	max_group_size = constraint_info['number_of_staphers']
	for i in range(0,max_group_size):
		for group in programming_groups:
			if len(staph[group]) < i and group not in ordered_groups:
				ordered_groups.append(group)
	# """
	# Now we build the schedules step by step...
	# """
	success = 0
	total = 0
	for group in ordered_groups:
		staphers = staph[group]
		print '\n\nGROUP:', group, ',',len(staphers),'stapher(s).'
		for shift_type in shifts[group]:
			programming_shifts = shifts[shift_type]
			print '	TYPE:',shift_type, '-', len(programming_shifts),'shifts.'
			total += 1
			print '	Starting search...'
			if bfs_schedules(staphers,programming_shifts,constraint_info):
				print '	... SUCCESS!!\n'
				success += 1
			else:
				print '	... FAILURE :(\n'
			print '=============================='
			print 'Placed', success, '/', total, 'shift types.'	

# Takes in an array of shifts and an array of workers
# and places them given they pass all constraints
def dfs_schedules(staph, unassigned_shifts, constraint_info):
	if unassigned_shifts == []:
		return True
	shift = unassigned_shifts[0]
	for stapher in staph:
		if passes_all_constraints(shift, stapher, constraint_info):
			stapher.add_shift(shift)
			unassigned_shifts.remove(shift)
			if not bfs_schedules(staph, unassigned_shifts, constraint_info):
				stapher.remove_shift(shift)
				unassigned_shifts.append(shift)
			else:
				return True
	if not shift.covered:
		return False

def bfs_schedules(staph, unassigned_shifts, constraint_info):
	if unassigned_shifts == []:
		return True
	shift = unassigned_shifts[len(unassigned_shifts) - 1]
	for stapher in staph:
		if passes_all_constraints(shift, stapher, constraint_info):
			stapher.add_shift(shift)
			unassigned_shifts.remove(shift)
			if not dfs_schedules(staph, unassigned_shifts, constraint_info):
				stapher.remove_shift(shift)
				unassigned_shifts.append(shift)
			else:
				return True
	if not shift.covered:
		return False

def passes_all_constraints(shift, stapher, constraint_info):
	"""Add all of the constraints we want to the CSP."""
	if shift == None or stapher == None:
		return False
	if fails_special_shift_constraints(shift, stapher, constraint_info):
		return False
	if fails_off_shift_constraints(shift, stapher, constraint_info):
		return False
	if fails_programming_shift_constraints(shift, stapher, constraint_info):
		return False
	return stapher.free_during_shift(shift) and not shift.covered
	# TODO: Add more constraints!

def fails_kids_shift_constraints(shift, stapher, constraint_info):
	if not shift.is_kids_programming():
		return False
	# TODO: Add a must have male/female on the shift constraint. How? Idk...
	# OH! I think I got it! Just add a gender requirement to each shift
	# and make sure that stapher.gender = shift.requirement!
	return False

def fails_ski_dock_constraints(shift, stapher, constraint_info):
	if not shift.is_ski_dock():
		return False
	return False

def fails_programming_shift_constraints(shift, stapher, constraint_info):
	if not shift.is_programming():
		return False
	if shift.eligible_workers not in stapher.positions:
		return True
	# Max programming hours
	# if stapher.reached_programming_limit_type(shift, constraint_info):
	# 	return True
	# if stapher.reached_programming_limit_week(shift, constraint_info):
	# 	return True
	# if fails_ski_dock_constraints(shift, stapher, constraint_info):
	# 	return True
	return False

def fails_special_shift_constraints(shift, stapher, constraint_info):
	return False
	if not shift.is_special():
		return False
	# No one can get more the the even number of shifts
	if stapher.schedule.total_special_shifts >= constraint_info['max_special_shifts']:
		return True
	# No one can have 2 of the same type of shift
	elif shift.type in stapher.schedule.special_shift_types:
		return True
	return False

def fails_off_shift_constraints(shift, stapher, constraint_info):
	if not shift.is_off_day():
		return False
	if stapher.off_day_scheduled():
		return True
	if not stapher.same_off_day(shift):
		return True
	if shift.length != 24:
		return not stapher.free_during_time(shift.day + 1 , 0, 24)
	else:
		return not stapher.free_during_time(shift.day - 1 , 16, 24)

def avg_weekly_programming_hours_by_group(staph, shifts, constraint_info):
	programming_groups = shifts['programming']
	average_weekly_programming_hours = {}
	variance = constraint_info['programing_limit_varience']
	for group in programming_groups:
		total_programming_hours = 0
		for shift_type in shifts[group]:
			for shift in shifts[shift_type]:
				total_programming_hours += shift.length
		average_weekly_programming_hours[group] = (total_programming_hours / len(staph[group])) + variance
	return average_weekly_programming_hours

def limits_by_type_and_day(staph, shifts):
	limits = {}
	programming_groups = shifts['programming']
	for group in programming_groups:
		for shift_type in shifts[group]:
			total_shifts_of_type_by_day = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
			longest_shift_of_type_by_day = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
			shortest_shift_of_type_by_day = {0:24, 1:24, 2:24, 3:24, 4:24, 5:24, 6:24}
			total_shift_hours_by_day = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
			for shift in shifts[shift_type]:
				total_shifts_of_type_by_day[shift.day] += 1
				total_shift_hours_by_day[shift.day] += shift.length
				if shift.length > longest_shift_of_type_by_day[shift.day]:
					longest_shift_of_type_by_day[shift.day] = shift.length
				if shift.length < shortest_shift_of_type_by_day[shift.day]:
					shortest_shift_of_type_by_day[shift.day] = shift.length
			limit_of_type_by_day = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
			for day in limit_of_type_by_day:
				if  total_shifts_of_type_by_day[day]:
					average_shift_length = total_shift_hours_by_day[day] / total_shifts_of_type_by_day[day]
				if total_shifts_of_type_by_day[day] < len(staph[group]):
					limit = average_shift_length
				else:
					limit = (total_shifts_of_type_by_day[day] / len(staph[group])) * shortest_shift_of_type_by_day[day]
				limit_of_type_by_day[day] = limit
			limits[shift_type] = limit_of_type_by_day
	return limits
			
def get_readable_time(time):
	hour = int(time)
	minute = str(time - hour)
	if minute == '0.0' or minute == '0':
		minute = ':00'
	elif minute == '0.25':
		minute = ':15'
	elif minute == '0.33':
		minute = ':20'
	elif minute == '0.5':
		minute = ':30'
	elif minute == '0.66':
		minute = ':40'
	elif minute == '0.75':
		minute = ':45'
	if hour < 12 or hour == 24:
		suffix = 'am'
	else:
		suffix = 'pm'
	if hour > 12:
		hour = hour - 12
	if hour == 0:
		hour = 12
	return str(hour) + minute + suffix

def make_schedule_txt_files(staph):
	days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday']
	for stapher in staph['all-staph']:
		schedule_txt = ''
		schedule = stapher.schedule.all_shifts
		for day in schedule:
			schedule_txt += str(days[day]) + ','
			for shift in schedule[day]:
				if shift.is_programming:
					programming_tag = 'p'
				else:
					programming_tag = ''
				start = get_readable_time(shift.start)
				end = get_readable_time(shift.end)
				schedule_txt +=  shift.title + '(' + start + '-' + end + ')' + programming_tag + ','
			schedule_txt = schedule_txt[:-1] + '\n'
			directory = '../output/2017/schedules/txt_files'
		schedule_txt = schedule_txt[:-1]
		if not os.path.exists(directory):
			os.makedirs(directory)
		filename = directory + '/' + stapher.name + '.txt'
		new_file = open(filename, 'w')
		new_file.write(schedule_txt)
		new_file.close()

def get_time_from_txt(time_txt):
	split = time_txt.index(':')
	hour = int(time_txt[:split])
	minute_txt = time_txt[split:-2]
	is_am = time_txt[-2:] == 'am'
	if minute_txt == ':00':
		minute = 0
	elif minute_txt == ':15':
		minute = 0.25
	elif minute_txt == ':20':
		minute = 0.33
	elif minute_txt == ':30':
		minute = 0.5
	elif minute_txt == ':40':
		minute = 0.66
	elif minute_txt == ':45':
		minute = 0.75
	if not is_am or (is_am and hour == 12):
		hour += 12
	return hour + minute

def get_shift_from_txt(day,shift_txt,shifts):
	time_index = shift_txt.index('(')
	start_index = shift_txt.index('-')
	shift_title = shift_txt[:time_index]
	start_time_txt = shift_txt[time_index + 1:start_index]
	end_time_txt = shift_txt[start_index + 1:-1]
	start_time = get_time_from_txt(start_time_txt)
	end_time = get_time_from_txt(end_time_txt)
	shift = Shift(day, shift_title, start_time, start_time)
	return shift

def get_schedules_from_txt_files(staph,shifts):
	days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday']
	for stapher in staph['all-staph']:
		schedule_txt_file = open('../output/2017/schedules/' + stapher.name + '.txt')
		csv_schedule_txt_file = csv.reader(schedule_txt_file)
		for line in csv_schedule_txt_file:
			day = days.index(line[0]) # remove colon from the day
			for shift_txt in line[1:]:
				shift = get_shift_from_txt(day,shift_txt,shifts)
				stapher.add_shift(shift)
		schedule_txt_file.close()
	# for stapher in staph['all-staph']:
	# 	print stapher.name
	#  	stapher.schedule.print_info()

# For testing...
def print_staph_by_position(staph_by_positions):
	for position in staph_by_positions:
		print position
		for stapher in staph_by_positions[position]:
			print '	',stapher
			stapher.schedule.print_info()

def print_staph(staph, constraint_info):
	for stapher in staph:
		print stapher
		# w = stapher.special_shift_preferences
		# print stapher.name, 'wanted: 1.', w[0], '2.',w[1],'3.',w[2],'4.',w[3],'5.',w[4]
		max_programming_hours = 0
		for pos in stapher.positions:
			max_programming_hours += constraint_info['max_programming_hours'][pos]
		print 'MAX PROGRAMMING HOURS:', max_programming_hours
		print stapher.total_shifts(),'shifts,',stapher.programming_hours(),'programming hours.'
		stapher.schedule.print_info()

def print_uncovered_shifts(shifts):
	print '============UNCOVERED=SHIFTS================'
	uncovered = []
	for shift in shifts:
		if not shift.covered:
			uncovered.append(shift)
	if len(uncovered) > 0:
		for shift in uncovered:
			print shift
	print len(uncovered) ,'SHIFTS LEFT UNCOVERED'

def generate_rand_preferences(staph, shifts):
	all_staph = staph['all-staph']
	special_shift_types = shifts['special']['staph']
	for stapher in all_staph:
		type_prefferences = []
		while len(type_prefferences) < len(special_shift_types): # only looks at top 4 choices
			r = random.randint(0,len(special_shift_types) - 1)
			if special_shift_types[r] not in type_prefferences:
				type_prefferences.append(special_shift_types[r])
		stapher.special_shift_preferences = type_prefferences

def find_special_shift_sucess_rate(staph, shifts, constraint_info):
	all_staph = staph['all-staph']
	special_shifts = shifts['all-special-shifts']
	in_top_three = 0
	in_top_five = 0
	in_top_ten = 0
	in_top_fifteen = 0
	placed_not_top_choice = 0
	uncovered_shifts = 0
	trials = 1000
	total_shifts = len(special_shifts) * trials
	for i in range(0,trials):
		for stapher in all_staph:
			stapher.clear_shifts_of_category('special')
		generate_rand_preferences(staph, shifts)
		schedule_special_shifts(staph, shifts, constraint_info)
		for stapher in all_staph:
			for day in stapher.schedule.all_shifts.keys():
				for shift in stapher.schedule.all_shifts[day]:
					if shift.type in stapher.special_shift_preferences[:3]:
						in_top_three += 1
					if shift.type in stapher.special_shift_preferences[:5]:
						in_top_five += 1
					if shift.type in stapher.special_shift_preferences[:10]:
						in_top_ten += 1
					if shift.type in stapher.special_shift_preferences[:15]:
						in_top_fifteen += 1
					else:
						placed_not_top_choice += 1
		not_covered = False
		for shift in special_shifts:
			if not shift.covered:
				not_covered = True
		if not_covered:
			uncovered_shifts += 1
	percent_top_three = (float(in_top_three)/total_shifts) * 100
	percent_top_five = (float(in_top_five)/total_shifts) * 100
	percent_top_ten = (float(in_top_ten)/total_shifts) * 100
	percent_top_fifteen = (float(in_top_fifteen)/total_shifts) * 100
	percent_not_in_top = (float(placed_not_top_choice)/total_shifts) * 100
	print percent_top_three, '% of shifts placed were ranked in top 3'
	print percent_top_five, '% of shifts placed were ranked in top 5'
	print percent_top_ten, '% of shifts placed were ranked in top 10'
	print percent_top_fifteen, '% of shifts placed were ranked in top 15'
	print percent_not_in_top, '% of shifts placed were ranked above 15'
	print uncovered_shifts,'/', trials,' trials, has special shifts not scheduled'

def arr_from_dict(dictionary):
	array = []
	for key in dictionary:
		for value in dictionary[key]:
			array.append(value)
	return array

def reset_xl_files(ws):
    merged_cells = ws.merged_cell_ranges
    for day in range(0,7):
		row = 9 + (day * 4)
		time = 6
		while time < 23.5:
			hour = int(time)
			minute = time - hour
			col = 3 + ((hour - 6) * 4) + (minute * 4)
			time_cell = ws.cell(row=row - 2,column=col)
			programming_cell = ws.cell(row=row - 1,column=col)
			cell = ws.cell(row=row,column=col)
			cell.value = ''
			programming_cell.value = ''
			time_cell.value = ''
			cell.fill = PatternFill(patternType='solid',fill_type='solid',fgColor=Color('ffffff'))
			cell.border = Border(left=Side(style='thin'),right=Side(style='thin'),top=Side(style='thin'),bottom=Side(style='thin'))
			cell_coordinance = cell.column + str(cell.row)
			for m_cell in merged_cells:
				m_start = m_cell[:m_cell.index(':')]
				if cell_coordinance == m_start:
					end_coordinance = m_cell[m_cell.index(':') + 1:]
					cell_to_unmerge = cell_coordinance + ':' + end_coordinance
					ws.unmerge_cells(cell_to_unmerge)
			time += 0.25

def get_time_from_txt(time_txt):
	split = time_txt.index(':')
	hour = int(time_txt[:split])
	minute_txt = time_txt[split:-2]
	is_am = time_txt[-2:] == 'am'
	if minute_txt == ':00':
		minute = 0
	elif minute_txt == ':15':
		minute = 0.25
	elif minute_txt == ':20':
		minute = 0.25
	elif minute_txt == ':30':
		minute = 0.5
	elif minute_txt == ':40':
		minute = 0.75
	elif minute_txt == ':45':
		minute = 0.75
	if not is_am and hour != 12: 
		hour += 12
	return hour + minute

def get_start_time(shift_txt):
	time_txt = shift_txt[shift_txt.index('('):]
	start_index = time_txt.index('-')
	start_time_txt = time_txt[1:start_index]
	start_time = get_time_from_txt(start_time_txt)
	return start_time

def get_end_time(shift_txt):
	time_txt = shift_txt[shift_txt.index('('):]
	start_index = time_txt.index('-')
	end_time_txt = time_txt[start_index + 1: -1]
	end_time = get_time_from_txt(end_time_txt)
	return end_time

def update_xlsx(src, ws):
	days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday']
	schedule_file = open(src)
	csv_schedule_file = csv.reader(schedule_file)
	for line in csv_schedule_file:
		day = days.index(line[0])
		row = 9 + (day * 4)
		for shift_txt in line[1:]:
			is_programming = shift_txt[len(shift_txt) - 1] == 'p'
			if is_programming:
				shift_txt = shift_txt[:-1]
			start_time = get_start_time(shift_txt)
			start_hour = int(start_time)
			start_minute = start_time - start_hour
			end_time = get_end_time(shift_txt)
			end_hour = int(end_time)
			end_minute = end_time - end_hour
			start_col = 3 + ((start_hour - 6) * 4) + (start_minute * 4)
			end_col = 3 + ((end_hour - 6) * 4) + (end_minute * 4) - 1
			cell = ws.cell(row=row,column=start_col)
			shift_title =  shift_txt[:shift_txt.index('(')]
			if ':20' in shift_txt or ':40' in shift_txt:
				cell.value = shift_txt
			else:
				cell.value = shift_title
			# print shift_txt,row,start_col,end_col
			if shift_title == 'Off Day':
				cell.fill = PatternFill(patternType='solid',fill_type='solid',fgColor=Color('C4C4C4'))
			else:
				curr_col = start_col
				while curr_col <= end_col:
					time_cell = ws.cell(row=row - 2,column=curr_col)
					programming_cell = ws.cell(row=row - 1,column=curr_col)
					if is_programming:
						programming_cell.value = '1'
					else:
						time_cell.value = '1'
					curr_col += 1
					programming_cell.border = Border(left=Side(style='thin'),right=Side(style='thin'),top=Side(style='thin'),bottom=Side(style='thin'))
			cell.alignment = Alignment(shrinkToFit=True, wrapText=True, horizontal='center',vertical='center')
			cell.border = Border(left=Side(style='thin'),right=Side(style='thin'),top=Side(style='thin'),bottom=Side(style='thin'))
			ws.merge_cells(start_row=row,start_column=start_col,end_row=row,end_column=end_col)
	schedule_file.close()

def fill_xl_with_schedules(staph):
	# print 'Loading workbook...'
	# filename = '../output/2017/schedules/test.xlsx'
	# wb = load_workbook(filename)
	# ws = wb.get_sheet_by_name('TEMPLATE')
	# reset_xl_files(ws)
	# txt_file = '../output/2017/schedules/txt_files/Ariel Bong.txt'
	# update_xlsx(txt_file,ws)
	# print 'Saving workbook...'
	# wb.save(filename)
	print 'Loading workbook...'
	filename = '../output/2017/schedules/schedules.xlsx'
	wb = load_workbook(filename)
	print 'Getting all worksheets...'
	for stapher in staph['all-staph']:
		name = stapher.name
		print '	Resetting', stapher.name + '\'s schedule...'
		ws = wb.get_sheet_by_name(name)
		reset_xl_files(ws)
		txt_file = '../output/2017/schedules/txt_files/'+ name + '.txt'
		print '	Updating', stapher.name + '\'s XL file...'
		update_xlsx(txt_file,ws)
	print 'Saving workbook...'
	wb.save(filename)


def duplicate_xl_temp(file,name):
	print file, name
	wb = load_workbook(file)
	template = wb.get_sheet_by_name('TEMPLATE')
	new = wb.copy_worksheet(template)
	new.title = name
	title_cell = new['B2']
	title_cell.value = name
	wb.save(file)


def group_masters(shifts,staph):
	masters = ['ski-dock','manager','athletics','arts','nature']
	no_individual_masters = ['icom','boat-dock-coordinator','sdh','ski-dock','iic','kgc','yoga','climbing','volleyball','tennis','sailing','arts','crafts','music','theater','hiking','naturalist','kids-naturalist']
	for position in staph:
		if position in shifts:
			if position not in no_individual_masters:
				shifts[ position + '-master'] = shifts['all-' + position + '-shifts']
				masters.append(position)
			if position in ['sdh','ski-dock']:
				if 'ski-dock-master' in shifts:
					shifts['ski-dock-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['ski-dock-master'] = shifts['all-' + position + '-shifts']
			if position in ['iic','kgc']:
				if 'manager-master' in shifts:
					shifts['manager-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['manager-master'] = shifts['all-' + position + '-shifts']
			if position in ['yoga','climbing','volleyball','tennis','sailing']:
				if 'athletics-master' in shifts:
					shifts['athletics-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['athletics-master'] = shifts['all-' + position + '-shifts']
			if position in ['arts','crafts','music','theater']:
				if 'arts-master' in shifts:
					shifts['arts-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['arts-master'] = shifts['all-' + position + '-shifts']
			if position in ['hiking','naturalist','kids-naturalist']:
				if 'nature-master' in shifts:
					shifts['nature-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['nature-master'] = shifts['all-' + position + '-shifts']
			if position in ['boat-dock-coordinator']:
				if 'boat-dock-master' in shifts:
					shifts['boat-dock-master'] += shifts['all-' + position + '-shifts']
				else:
					shifts['boat-dock-master'] = shifts['all-' + position + '-shifts']


def get_total_overlapping_shifts(shift,shifts_to_populate):
	total_overlapping_shifts = []
	for other_shift in shifts_to_populate:
		if shift != other_shift:
			if shift.at_same_time(other_shift):
				if shift.title == other_shift.title:
					total_overlapping_shifts.append(other_shift)
	return total_overlapping_shifts

def get_partial_overlapping_shifts(shift,shifts_to_populate):
	total_partial_shifts = []
	for other_shift in shifts_to_populate:
		if shift != other_shift:
			if not shift.at_same_time(other_shift) and shift.time_overlaps_with(other_shift):
				total_partial_shifts.append(other_shift)
	return total_partial_shifts

def get_row_end_from_overlap(row_start,overlap):
	if overlap == 0:
		row_end = row_start + 5
	elif overlap < 3:
		row_end = row_start + (3 - overlap)
	else:
		row_end = row_start
	return row_end

def get_minute(time):
	minute = time - int(time)
	if str(minute) == '0.33':
		minute = 0.25
	if str(minute) == '0.66':
		minute = 0.75
	return minute

def get_first_name(name):
	return name[:name.index(' ')]

def populate_master(wb,name,shifts_to_populate):
	# print name, len(shifts_to_populate)
	ws = wb.get_sheet_by_name(name)
	for shift in shifts_to_populate:
		total_overlapping_shifts = get_total_overlapping_shifts(shift,shifts_to_populate)
		partial_overlapping_shifts = get_partial_overlapping_shifts(shift,shifts_to_populate)
		row_start = 7 + (shift.day * 7)
		row_end = get_row_end_from_overlap(row_start, len(partial_overlapping_shifts))
		
		# total overlapping shifts
		start_hour = int(shift.start)
		start_minute = get_minute(shift.start)
		end_hour = int(shift.end)
		end_minute = get_minute(shift.end)
		start_col = 4 + ((start_hour - 6) * 4) + (start_minute * 4)
		end_col = 4 + ((end_hour - 6) * 4) + (end_minute * 4) - 1
		cell = ws.cell(row=row_start,column=start_col)
		# print shift
		if len(total_overlapping_shifts) > 0:
			# print '	',len(total_overlapping_shifts),'total overlap'
			title = get_first_name(shift.stapher.name) + ','
			for total_overlap_shift in total_overlapping_shifts:
				title += get_first_name(total_overlap_shift.stapher.name) + ', '
				shifts_to_populate.remove(total_overlap_shift)
			title = title[:-2]
		else:
			# print '	No total overlap'
			title = get_first_name(shift.stapher.name) + ':' + shift.title
		cell.value = title
		cell.alignment = Alignment(shrinkToFit=True, wrapText=True, horizontal='center',vertical='center')
		cell.border = Border(left=Side(style='thin'),right=Side(style='thin'),top=Side(style='thin'),bottom=Side(style='thin'))
		# print '		Cell:', shift,row_start,row_end,start_col,end_col,title
		ws.merge_cells(start_row=row_start,start_column=start_col,end_row=row_end,end_column=end_col)
		
		# Partial Overlapping Shift
		# print '	',len(partial_overlapping_shifts),'partial overlap.'
		for partial_overlapping_shift in partial_overlapping_shifts:
			other_total_lapping_shifts = get_total_overlapping_shifts(partial_overlapping_shift,partial_overlapping_shifts)
			if len(other_total_lapping_shifts) > 0:
				# print '	',len(other_total_lapping_shifts),'total overlap w/in partial overlap'
				title = get_first_name(partial_overlapping_shift.stapher.name)
				for shift in other_total_lapping_shifts:
					title = get_first_name(shift.stapher.name) + ', '
					other_total_lapping_shifts.remove(shift)
				title = title[:-2]
			else:
				# print '	No total overlap w/ in partial overlap'
				title = get_first_name(partial_overlapping_shift.stapher.name) + ': ' + partial_overlapping_shift.title
			row_start = row_end + 1
			row_end = get_row_end_from_overlap(row_start, len(partial_overlapping_shifts))
			start_hour = int(partial_overlapping_shift.start)
			start_minute = get_minute(partial_overlapping_shift.start)
			end_hour = int(partial_overlapping_shift.end)
			end_minute = get_minute(partial_overlapping_shift.end)
			start_col = 4 + ((start_hour - 6) * 4) + (start_minute * 4)
			end_col = 4 + ((end_hour - 6) * 4) + (end_minute * 4) - 1
			overlap_cell = ws.cell(row=row_start,column=start_col)
			overlap_cell.value = title
			# print '		Overlapping Cell:', partial_overlapping_shift,row_start,row_end,start_col,end_col,title
			overlap_cell.alignment = Alignment(shrinkToFit=True, wrapText=True, horizontal='center',vertical='center')
			overlap_cell.border = Border(left=Side(style='thin'),right=Side(style='thin'),top=Side(style='thin'),bottom=Side(style='thin'))
			ws.merge_cells(start_row=row_start,start_column=start_col,end_row=row_end,end_column=end_col)

			shifts_to_populate.remove(partial_overlapping_shift)



def make_new_masters(file,shifts,staph):
	group_masters(shifts,staph)
	wb = load_workbook(file)
	for key in shifts:
		if 'master' in key:
			name = key[:-7].upper() + ' MASTER'
			shifts_to_populate = list(shifts[key])
			# duplicate_xl_temp(file,name)
			print 'Making', name 
			populate_master(wb,name,shifts_to_populate)
	wb.save(file)


def get_who_is_free(staph,day,start_time,end_time):
	days = []
	for stapher in staph['all-staph']:
		if stapher.free_during_time(day,start_time,end_time):
			print '	',stapher.name,'is free during Wednesday, 2:30-4:30'

if __name__ == "__main__":
	year = '2017'
	staph_file = '../input/past-csv-files/' + year + '/staph.csv'
	shift_dir = '../input/past-csv-files/' + year + '/shifts'
	staph = get_staph_from_csv_file(staph_file)
	shifts = get_shifts(shift_dir)

	# Get what you've saved...
	# get_schedules_from_txt_files(staph,shifts)

	"""
	Place all off day shifts...
	"""
	# off_day_restrictions = get_off_day_restrictions(staph, shifts)
	# pairs_to_avoid = get_pairs_to_avoid('../input/past-csv-files/' + year + '/problem_pairs.csv')
	# off_days(staph, off_day_restrictions, pairs_to_avoid)
	
	"""
	Place all programming shifts...
	"""
	# programming(staph,shifts)

	"""
	Place all special shifts...
	"""
	# special_shift_rankings = get_special_shift_rankings(staph, shifts)
	# schedule_special_shifts(staph,shifts,constraint_info)


	"""
	Place all meal shifts...
	"""

	"""
	Place all boat dock shifts...
	"""

	"""
	Place all lifeguarding shifts...
	"""

	# Save it...
	# make_schedule_txt_files(staph)


	# Make it readable in XL
	# fill_xl_with_schedules(staph)
	
	# make_new_masters('../output/2017/masters/masters.xlsx',shifts,staph)

	# get_who_is_free(staph,3,14.5,16.5)








