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



if __name__ == "__main__":
	year = '2016'
	test = 'c-and-q'
	# all_staph = get_staph_from_csv_files('../input/test-csv-files/' + test + '/staph')
	# all_shifts = get_shifts_from_csv_files('../input/test-csv-files/' + test + '/shifts')
	all_staph_groups = get_staph_from_csv_files('../input/past-csv-files/' + year + '/staph')
	all_shifts = get_shifts_from_csv_files('../input/past-csv-files/' + year + '/shifts')

	"""
	Here I need to order the shifts to assure that those groups with the smallest number of people in them
	get their required shifts placed first. This is to assure that one person groups get all the shifts they have to cover before
	they are placed in the automator w/ bigger groups.
	"""
	ordered_groups = []
	for i in range(0,61):
		for group_name in all_staph_groups:
			if len(all_staph_groups[group_name]) < i and group_name not in ordered_groups:
				ordered_groups.append(group_name)
	# """
	# Now I build the schedules step by step...
	# """
	all_staphers = [] # For testing 
	for group_name in ordered_groups:
		# print 'Building', group_name, 'schedules...'
		staph_group = all_staph_groups[group_name]
		shifts_for_group = all_shifts[group_name]
		if DFS_Schedules(staph_group, shifts_for_group):
			print 'schedules found for', group_name
		else:
			print 'incomplete schedule for', group_name

		# For printing...
		for stapher in staph_group:
			if stapher not in all_staphers:
				all_staphers.append(stapher)
				
	# print the final scheudles
	print len(all_staphers)
	for stapher in all_staphers:
		print stapher
		stapher.schedule.print_info()
