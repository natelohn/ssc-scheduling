import csv, os, random
from core import Stapher, Shift, Schedule, constants
from constraint import Problem, Variable, Domain


def get_staph_from_csv_file(file):
	staph_file = open(file)
	csv_staph_file = csv.reader(staph_file)
	staph = {}
	staph['all-staph'] = []
	for staph_info in csv_staph_file:
		name = staph_info[0]
		positions = staph_info[1:]
		stapher = Stapher(name,positions)
		staph['all-staph'].append(stapher)
		for position in positions:
			if position in staph:
				staph[position].append(stapher)
			else:
				staph[position] = [stapher]
	staph_file.close()
	return staph


def get_shifts_from_csv_file(filename, shift_category, worker_group, shift_type):
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
			shift = Shift(day, title, start, end, shift_category, worker_group, shift_type)
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
							shifts_of_type = get_shifts_from_csv_file(file, category, worker_group, shift_type)
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
	for group in ordered_groups:
		staphers = staph[group]
		print '\n\n\nGROUP:', group
		for shift_type in shifts[group]:
			print '	',shift_type
			programming_shifts = shifts[shift_type]
			print '	',len(staphers), 'staphers,', len(programming_shifts), 'shifts.'
			print '	Starting DFS search...'
			if DFS_Schedules(staphers, programming_shifts, constraint_info):
				print '	... SUCESS!'
			else:
				print '	... FAILURE :('
			print '======================='

# Takes in an array of shifts and an array of workers
# and places them given they pass the constraint
def DFS_Schedules(staph, unassigned_shifts, constraint_info):
	# indent = ''
	# for i in range(0,len(unassigned_shifts)):
	# 	indent += '=='
	# print indent,len(unassigned_shifts), 'shifts left...'
	if unassigned_shifts == []:
		return True
	else:
		shift = unassigned_shifts[0]
		for stapher in staph:
			if passes_all_constraints(shift, stapher, constraint_info):
				stapher.add_shift(shift)
				unassigned_shifts.remove(shift)
				if not DFS_Schedules(staph, unassigned_shifts, constraint_info):
					stapher.remove_shift(shift)
					unassigned_shifts.append(shift)
				else:
					return True
		if not shift.covered:
			return False

# FAILS TOO SOON!!!
def BFS_Schedules(staph, unassigned_shifts, constraint_info):
	# indent = ''
	# for i in range(0,len(unassigned_shifts)):
	# 	indent += '--'
	# print indent,len(unassigned_shifts), 'shifts left...'
	if unassigned_shifts == []:
		return True
	shift = unassigned_shifts[0]
	for stapher in staph:
		if passes_all_constraints(shift, stapher, constraint_info):
			stapher.add_shift(shift)
			unassigned_shifts.remove(shift)
			if not BFS_Schedules(staph, unassigned_shifts, constraint_info):
				stapher.remove_shift(shift)
				unassigned_shifts.append(shift)
			else:
				return True
		else:
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
	if stapher.reached_programming_limit_week(shift.length, constraint_info):
		return True
	if fails_ski_dock_constraints(shift, stapher, constraint_info):
		return True
	return False

def fails_special_shift_constraints(shift, stapher, constraint_info):
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



def add_off_day_restrictions(staph_by_positions, programming_shifts):
	ammout_workers_needed = {}
	for position in programming_shifts:
		staphers_in_position = staph_by_positions[position]
		for shift in programming_shifts[position]:
			if shift.day in ammout_workers_needed and shift.start in ammout_workers_needed[shift.day]:
				ammout_workers_needed[shift.day][shift.start] += 1
			else:
				ammout_workers_needed[shift.day] = {shift.start:1}
			if not ammout_workers_needed[shift.day][shift.start] < len(staphers_in_position):
				for stapher in staphers_in_position:
					if shift.day not in stapher.restricted_off_days:
						stapher.restricted_off_days.append(shift.day)

def max_programming_hours_by_group(staph, shifts):
	programming_groups = shifts['programming']
	average_programming_hours_by_group = {}
	variance = 3 # need to make this specific to each group
	for group in programming_groups:
		total_programming_hours = 0
		for shift_type in shifts[group]:
			for shift in shifts[shift_type]:
				total_programming_hours += shift.length
		average_programming_hours_by_group[group] = (total_programming_hours / len(staph[group])) + variance
	return average_programming_hours_by_group




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

if __name__ == "__main__":
	year = '2016'
	staph_file = '../input/past-csv-files/' + year + '/staph.csv'
	shift_dir = '../input/past-csv-files/' + year + '/shifts'
	staph = get_staph_from_csv_file(staph_file)
	shifts = get_shifts(shift_dir)
	
	'''
	First we gather all the information we will need while placing shifts...
	'''
	constraint_info = {}
	constraint_info['number_of_staphers'] = len(staph['all-staph'])
	constraint_info['max_special_shifts'] = (len(shifts['all-special-shifts']) / len(staph['all-staph'])) + 1
	constraint_info['number_special_shift_types'] = len(shifts['special']['staph'])
	constraint_info['max_programming_hours'] = max_programming_hours_by_group(staph, shifts)
	# print constraint_info

	"""
	Next we will place all programming shifts...
	"""
	schedule_programming_shifts(staph, shifts, constraint_info)
	

	"""
	Schedule the special shifts...
	The current algorithm gives staphers a 70% chance of getting all shifts in their top 5,
	 an 87% chance of getting all shifts in their top 10, and a 95% chance of getting all in their top 15.
	 But,only whenever special shifts are placed before anything else!
	 """
	generate_rand_preferences(staph, shifts) #These preferences will be manually input during actual schedule building.
	# schedule_special_shifts(staph, shifts, constraint_info)


	"""
	Place all off day shifts...
	"""
	# add_off_day_restrictions(staph_by_positions, programming_shifts)




	"""
	See how well we're placing the special shifts...
	"""
	# find_special_shift_sucess_rate(staph, shifts, constraint_info)

	# See what happened...
	print_staph(staph['ski-dock'], constraint_info)

	# See what is missing...
	print_uncovered_shifts(shifts['all-programming-shifts'])


