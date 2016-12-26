import csv, os
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
	if len(unassigned_shifts) < 4:
		print 'finding a place for', len(unassigned_shifts), 'shifts w/', len(staph), 'staphers...'
	if unassigned_shifts == []:
		print '============MADE IT================'
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
	return stapher.free_during_shift(shift)
	# TODO: Add more constraints!

def fails_special_shift_constraints(shift, stapher):
	# No one can get more the the even number of shifts
	if stapher.schedule.total_special_shifts >= 4:
		return True
	# No one can have 2 of the same type of shift
	if shift.type in stapher.schedule.special_shift_types:
		return True
	else:
		return False


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
		stapher.schedule.print_info()

def print_uncovered_shifts(shifts):
	uncovered = []
	for shift in shifts:
		if not shift.covered:
			uncovered.append(shift)
	if len(uncovered) > 0:
		print '======================='
		for shift in uncovered:
			print shift
	print len(uncovered) ,'SHIFTS LEFT UNCOVERED'



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
	For the simple solution we will ignore special shift preferences and special shift type. 
	"""
	# This will change later.
	special_shift_arr = []
	for shift_type in special_shifts: 
		special_shift_arr += special_shifts[shift_type]
	# DFS_Schedules(all_staph, special_shift_arr)


	smaller_staph = all_staph[:len(all_staph) / 5]
	smaller_shifts = special_shift_arr[:len(special_shift_arr) / 10]
	if DFS_Schedules(all_staph, special_shift_arr):
		print_staph(all_staph)
	else:
		print 'no solution found'
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
	# print_staph(all_staph)
	# print_uncovered_shifts(special_shift_arr)

