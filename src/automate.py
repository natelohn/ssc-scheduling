import csv
from core import Stapher, Shift, Schedule
from constraint import Problem, Variable, Domain

def get_staph_from_csv(filename):
	staph_file = open(filename)
	csv_staph_file = csv.reader(staph_file)
	all_staph = []
	for staph_info in csv_staph_file:
		name = staph_info[0]
		position = staph_info[1]
		stapher = Stapher(name,position)
		all_staph.append(stapher)
	staph_file.close()
	return all_staph

def get_shifts_from_csv(filename):
	shifts_file = open(filename)
	csv_shifts_file = csv.reader(shifts_file)
	all_shifts = []
	for shift_info in csv_shifts_file:
		day = int(shift_info[0])
		title = shift_info[1]
		start = float(shift_info[2])
		end = float(shift_info[3])
		shift = Shift(day, title, start, end)
		all_shifts.append(shift)
	shifts_file.close()
	return all_shifts


def meets_constraints(stapher,shift):
	# no two people can work one shift
	if shift.covered:
		return False
	# a worker can't work 2 shifts at once
	elif not stapher.free_during_shift(shift):
		return False
	else:
		return True
		

def automate_schedules(staph,shifts):
	uncovered_shifts = Schedule() 
	for shift in shifts:
		for stapher in staph:
			if meets_constraints(stapher, shift):
				stapher.schedule.add_shift(shift)
		if not shift.covered:
			uncovered_shifts.add_shift(shift)
	# just testing code
	for stapher in staph:
		stapher.print_info()
		stapher.schedule.print_info()
	print uncovered_shifts.total_shifts, 'LEFT UNCOVERED'	

def generate_schedules(staph, shifts):
	scheduling_csp = Problem()
	for shift in shifts:
		scheduling_csp.addVariable(shift, staph)

	add_constraints(scheduling_csp, shifts)

	solution = scheduling_csp.getSolution()

	for shift, stapher in solution.iteritems():
		stapher.add_shift(shift)

	for stapher in staph:
		schedule = stapher.schedule
		print stapher
		schedule.print_info()


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
	all_staph = get_staph_from_csv('../input/2016-ski-dock.csv')
	all_shifts = get_shifts_from_csv('../input/2016-ski-dock-shifts.csv')
	# automate_schedules(all_staph,all_shifts)
	generate_schedules(all_staph, all_shifts)
