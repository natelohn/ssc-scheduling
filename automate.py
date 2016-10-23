import csv
from stapher import Stapher
from shift import Shift
from schedule import Schedule

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
		

if __name__ == "__main__":
	# all_staph = get_staph_data('clur-and-quads.csv')
	# all_shifts = get_shifts_data('clur-and-quads-shifts.csv')
	all_staph = get_staph_from_csv('2016-ski-dock.csv')
	all_shifts = get_shifts_from_csv('2016-ski-dock-shifts.csv')
	automate_schedules(all_staph,all_shifts)




