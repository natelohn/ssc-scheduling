import csv, os
from core import Stapher, Shift, Schedule
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

def get_shifts_from_csv_files(directory):
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
					shift = Shift(day, title, start, end)
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


def DFS_Schedules(staph, shifts):
	if shifts == []:
		return True
	else:
		for shift in shifts:
			for stapher in staph:
				if passes_all_constraints(shift, stapher):
					stapher.add_shift(shift)
					shifts.remove(shift)
					return DFS_Schedules(staph, shifts)
			if shift in shifts:
				print 'Could not place shift', shift
				return False
		



def passes_all_constraints(shift, stapher):
	"""Add all of the constraints we want to the CSP."""
	if shift == None or stapher == None:
		return False
	return stapher.free_during_shift(shift)
	# TODO: Add more constraints!

# For testing...
def print_staph(staph_by_positions):
	for position in staph_by_positions:
		print position
		for stapher in staph_by_positions[position]:
			print '	', stapher



if __name__ == "__main__":
	year = '2016'
	test = 'c-and-q'
	staph_file = '../input/past-csv-files/' + year + '/full-staph.csv'
	shift_dir = '../input/past-csv-files/' + year + '/shifts'
	full_staph_shifts = get_shifts_from_csv_files(shift_dir + '/full-staph')
	general_shifts = get_shifts_from_csv_files(shift_dir + '/general')
	meal_shifts = get_shifts_from_csv_files(shift_dir + '/meal')
	off_day_shifts = get_shifts_from_csv_files(shift_dir + '/off-day')
	programming_shifts = get_shifts_from_csv_files(shift_dir + '/programming')
	special_shifts = get_shifts_from_csv_files(shift_dir + '/special')
	all_staph = get_staph_from_csv_file(staph_file)
	staph_by_positions = get_staph_by_positions(all_staph)

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

	# 	# For printing...
	# 	for stapher in staph_group:
	# 		if stapher not in all_staphers:
	# 			all_staphers.append(stapher)
	print_staph(staph_by_positions)

