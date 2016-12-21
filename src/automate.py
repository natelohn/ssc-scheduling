import csv, os
from core import Stapher, Shift, Schedule
from constraint import Problem, Variable, Domain


def get_staph_from_csv_files(directory):
	all_staph = {}
	for filename in os.listdir(directory):
		if filename.endswith('.csv'):
			staph_group = filename[5:-10] # to remove the 'year' and '-staph.csv' from the string
			filename = directory + '/' + filename
			staph_file = open(filename)
			csv_staph_file = csv.reader(staph_file)
			staph_in_group = []
			for staph_info in csv_staph_file:
				name = staph_info[0]
				main_position = staph_info[1]
				alt_positions = staph_info[2:]
				stapher = Stapher(name,main_position,alt_positions)
				staph_in_group.append(stapher)
				if alt_positions:
					for position in alt_positions:
						if position in all_staph:
							all_staph[position].append(stapher)
						else:
							all_staph[position] = [stapher]
			all_staph[staph_group] = staph_in_group
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

def generate_schedules(staph, shifts):
	"""Generates schedules for the given staph."""

	# Create the scheulding CSP (Constraint Satisfaction Problem)
	scheduling_csp = Problem()

	# Add all the variables
	# A shift's domain is all staphers, a shift could potentially
	# be assigned any stapher
	for shift in shifts:
		scheduling_csp.addVariable(shift, staph)

	# Add all the constraints to the CSP
	add_constraints(scheduling_csp, shifts)

	# Get the first possible solution to the CSP
	solution = scheduling_csp.getSolution()

	if solution:
		for shift, stapher in solution.iteritems():
			stapher.add_shift(shift)

		for stapher in staph:
			schedule = stapher.schedule
		print 'IT WORKED I AM A GOD!'
	else:
		print staph
		print 'No solution found :('


def add_constraints(scheduling_csp, shifts):
	"""Add all of the constraints we want to the CSP."""

	no_overlapping_shifts_constraint(scheduling_csp, shifts)

	# TODO: Add more constraints!


def no_overlapping_shifts_constraint(scheduling_csp, shifts):
	"""
	A stapher cannot work two shifts at the same time.

	This loops over all shifts, and if two shifts overlap in time,
	adds a constraint between them that they cannot have the same
	stapher assigned to them.


	Parameters
	----------
	scheulding_csp : Problem
		Represents the scheduling constraint satisfaction problem.

	shifts : List of Shifts
		List of all Shift objects that need to be covered.
	"""
	for shift1 in shifts:
		for shift2 in shifts:
			if shift1 != shift2 and shift1.time_overlaps_with(shift2):
				scheduling_csp.addConstraint(
					lambda stapher1, stapher2: stapher1 != stapher2,
					[shift1, shift2]
				)

if __name__ == "__main__":
	year = '2016'
	test = 'ski-dock'
	# all_staph = get_staph_from_csv_files('../input/test-csv-files/' + test + '/staph')
	# all_shifts = get_shifts_from_csv_files('../input/test-csv-files/' + test + '/shifts')
	all_staph = get_staph_from_csv_files('../input/past-csv-files/' + year + '/staph')
	all_shifts = get_shifts_from_csv_files('../input/past-csv-files/' + year + '/shifts')

	"""
	Here I need to order the shifts to assure that those groups with the smallest number of people in them
	get their required shifts placed first. This is to assure that one person groups get all the shifts they have to cover before
	they are placed in the automator w/ bigger groups.
	"""
	ordered_groups = []
	for i in range(0,61):
		for group_name in all_staph:
			if len(all_staph[group_name]) < i and group_name not in ordered_groups:
				ordered_groups.append(group_name)
	"""
	Now I build the schedules step by step...
	"""
	all_staphers = [] # For testing 
	for group_name in ordered_groups:
		# print 'Building', group_name, 'schedules...'
		staph_group = all_staph[group_name]
		shifts_for_group = all_shifts[group_name]
		generate_schedules(staph_group, shifts_for_group)
		for stapher in staph_group:
			if stapher not in all_staphers:
				all_staphers.append(stapher)
				
	# print the final scheudles
	for stapher in all_staphers:
		print stapher
		stapher.schedule.print_info()
