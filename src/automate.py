import csv, os, random
from core import Stapher, Shift, Schedule, constants
from constraint import Problem, Variable, Domain


def get_staph_from_csv_file(file):
	all_staph = []
	staph_file = open(file)
	csv_staph_file = csv.reader(staph_file)
	for staph_info in csv_staph_file:
		name = staph_info[0]
		main_position = staph_info[1]
		alt_positions = staph_info[2:]
		stapher = Stapher(name,main_position,alt_positions)
		all_staph.append(stapher)
	staph_file.close()
	return all_staph

def get_shifts_from_csv_files(directory, shift_category):
	all_shifts = {}
	for filename in os.listdir(directory):
		if filename.endswith('.csv'):
			shift_type = filename[5:-11]
			filename = directory + '/' + filename
			shifts_file = open(filename)
			csv_shifts_file = csv.reader(shifts_file)
			shifts_in_type = []
			for shift_info in csv_shifts_file:
				day = int(shift_info[0])
				title = shift_info[1]
				start = float(shift_info[2])
				end = float(shift_info[3])
				ammount = int(shift_info[4])
				for i in range(0,ammount):
					shift = Shift(day, title, start, end, shift_category, shift_type)
					shifts_in_type.append(shift)
			all_shifts[shift_type] = shifts_in_type
			shifts_file.close()
	return all_shifts


def get_staph_by_positions(all_staph):
	staph_by_positions = {}
	for stapher in all_staph:
		stapher_positions = [stapher.position]
		if stapher.alt_positions:
			stapher_positions += stapher.alt_positions
		for position in stapher_positions:
			if position in staph_by_positions:
				staph_by_positions[position].append(stapher)
			else:
				staph_by_positions[position] = [stapher]
	return staph_by_positions

def DFS_Schedules(staph, unassigned_shifts):
	# print 'finding a place for', len(unassigned_shifts), 'shifts w/', len(staph), 'staphers...'
	if unassigned_shifts == []:
		return True
	else:
		shift = unassigned_shifts[0]
		for stapher in staph:
			if passes_all_constraints(shift, stapher):
				stapher.add_shift(shift)
				unassigned_shifts.remove(shift)
				if not DFS_Schedules(staph, unassigned_shifts):
					stapher.remove_shift(shift)
					unassigned_shifts.append(shift)
				else:
					return True
		if not shift.covered:
			return False
		



def passes_all_constraints(shift, stapher):
	"""Add all of the constraints we want to the CSP."""
	if shift == None or stapher == None:
		return False
	if shift.is_special() and fails_special_shift_constraints(shift, stapher):
		return False
	return stapher.free_during_shift(shift) and not shift.covered
	# TODO: Add more constraints!

def fails_special_shift_constraints(shift, stapher):
	# No one can get more the the even number of shifts
	if stapher.schedule.total_special_shifts >= 4:
		return True
	# No one can have 2 of the same type of shift
	elif shift.type in stapher.schedule.special_shift_types:
		return True
	else:
		return False

def schedule_special_shifts(all_staph, special_shifts):
	max_prefference = len(special_shifts.keys())
	left_over_shifts = []
	for shift_type in special_shifts:
		unassigned_shifts = [] + special_shifts[shift_type]
		current_prefference = 0
		while current_prefference < max_prefference and unassigned_shifts != []:
			for stapher in all_staph:
				if stapher.special_shift_preferences[current_prefference] == shift_type:
					for shift in unassigned_shifts:
						if passes_all_constraints(shift, stapher):
							stapher.add_shift(shift)
							unassigned_shifts.remove(shift)
							break
			current_prefference += 1
		left_over_shifts += unassigned_shifts
	for stapher in all_staph:
		for shift in left_over_shifts:
			if passes_all_constraints(shift, stapher):
				stapher.add_shift(shift)
				left_over_shifts.remove(shift)



# For testing...
def print_staph_by_position(staph_by_positions):
	for position in staph_by_positions:
		print position
		for stapher in staph_by_positions[position]:
			print '	',stapher
			stapher.schedule.print_info()
def print_staph(staph):
	for stapher in staph:
		print stapher
		w = stapher.special_shift_preferences
		print stapher.name, 'wanted: 1.', w[0], '2.',w[1],'3.',w[2],'4.',w[3],'5.',w[4]
		stapher.schedule.print_info()

def print_uncovered_shifts(shifts):
	print '======================='
	uncovered = []
	for shift_type in shifts:
		for shift in shifts[shift_type]:
			if not shift.covered:
				uncovered.append(shift)
	if len(uncovered) > 0:
		for shift in uncovered:
			print shift
	print len(uncovered) ,'SHIFTS LEFT UNCOVERED'

def generate_rand_preferences(all_staph, special_shifts):
	special_shift_types = special_shifts.keys()
	for stapher in all_staph:
		type_prefferences = []
		while len(type_prefferences) < len(special_shift_types): # only looks at top 4 choices
			r = random.randint(0,len(special_shift_types) - 1)
			if special_shift_types[r] not in type_prefferences:
				type_prefferences.append(special_shift_types[r])
		stapher.special_shift_preferences = type_prefferences

def find_special_shift_sucess_rate(all_staph, special_shifts):
	top_choices = 10
	total_shifts = 0
	total_unwanted = 0
	placed_not_top_choice = 0
	uncovered_shifts = 0
	trials = 1000
	for i in range(0,trials):
		for stapher in all_staph:
			stapher.clear_schedule()
		generate_rand_preferences(all_staph, special_shifts)
		schedule_special_shifts(all_staph, special_shifts)
		not_top_choice = 0
		for stapher in all_staph:
			for day in stapher.schedule.all_shifts.keys():
				for shift in stapher.schedule.all_shifts[day]:
					total_shifts += 1
					if shift.type not in stapher.special_shift_preferences[:top_choices]:
						not_top_choice += 1
						total_unwanted += 1
		if not_top_choice > 0:
			placed_not_top_choice += 1
		not_covered = 0
		for s_type in special_shifts:
			for shift in special_shifts[s_type]:
				if not shift.covered:
					not_covered += 1
		if not_covered > 0:
			uncovered_shifts += 1
	sucess_rate = (float(total_unwanted)/total_shifts) * 100
	print  sucess_rate, '% of shifts placed were not ranked in top', top_choices
	print placed_not_top_choice,'/', trials,' trials, shifts include scheduled special shifts not in top', top_choices,'choices'
	print uncovered_shifts,'/', trials,' trials, has special shifts not scheduled'



if __name__ == "__main__":
	year = '2016'
	test = 'c-and-q'
	staph_file = '../input/past-csv-files/' + year + '/full-staph.csv'
	shift_dir = '../input/past-csv-files/' + year + '/shifts'
	special_shifts = get_shifts_from_csv_files(shift_dir + '/special', constants.ShiftCategory.SPECIAL)
	# full_staph_shifts = get_shifts_from_csv_files(shift_dir + '/full-staph')
	# general_shifts = get_shifts_from_csv_files(shift_dir + '/general')
	# meal_shifts = get_shifts_from_csv_files(shift_dir + '/meal')
	# off_day_shifts = get_shifts_from_csv_files(shift_dir + '/off-day')
	# programming_shifts = get_shifts_from_csv_files(shift_dir + '/programming')
	all_staph = get_staph_from_csv_file(staph_file)
	staph_by_positions = get_staph_by_positions(all_staph)


	"""
	First we schedule the special shifts...
	The current algorithm gives staphers a 70% chance of getting all shifts in their top 5,
	 an 87% chance of getting all shifts in their top 10, and a 95% chance of getting all in their top 15
	"""
	generate_rand_preferences(all_staph, special_shifts) #These shifts will be manually input during actual schedule building.
	schedule_special_shifts(all_staph, special_shifts)

	# special shift prefferences will be added manually later, but this will have to work for now...
	# This portion will not be in the final code
	# generate_rand_preferences(all_staph, special_shifts)
	# DFS_Schedules(all_staph, special_shifts_arr)
	# schedule_special_shifts(all_staph, special_shifts)
	# print_staph(all_staph)
	# print_uncovered_shifts(smaller_shifts)


	

	"""
	Here we need to order the shifts to assure that those groups with the smallest number of people in them
	get their required shifts placed first. This is to assure that smaller person groups get all the shifts they 
	have to cover before staphers that hold multiple positions are placed in the automator w/ bigger groups.
	"""
	# ordered_groups = []
	# for i in range(0,61):
	# 	for group_name in all_staph_groups:
	# 		if len(all_staph_groups[group_name]) < i and group_name not in ordered_groups:
	# 			ordered_groups.append(group_name)
	# # """
	# # Now we build the schedules step by step...
	# # """
	# all_staphers = [] # For testing 
	# for group_name in ordered_groups:
	# 	# print 'Building', group_name, 'schedules...'
	# 	staph_group = all_staph_groups[group_name]
	# 	shifts_for_group = all_shifts[group_name]
	# 	if DFS_Schedules(staph_group, shifts_for_group):
	# 		print 'schedules found for', group_name
	# 	else:
	# 		print 'incomplete schedule for', group_name


	# print_staph_by_position(staph_by_positions)
	print_staph(all_staph)
	print_uncovered_shifts(special_shifts)
	# find_special_shift_sucess_rate(all_staph, special_shifts)

