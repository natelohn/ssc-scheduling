import csv

def get_staph_data(filename):
	staph_file = open(filename)
	csv_staph_file = csv.reader(staph_file)
	all_staph = []
	for i, staph_info in enumerate(csv_staph_file):
		stapher = {'id':i, 'name':staph_info[0], 'position':staph_info[1], 'schedule':{0:[],1:[],2:[],3:[],4:[],5:[],6:[]}}
		all_staph.append(stapher)
	staph_file.close()
	return all_staph

def get_shifts_data(filename):
	shifts_file = open(filename)
	csv_shifts_file = csv.reader(shifts_file)
	all_shifts = []
	for i, shift_info in enumerate(csv_shifts_file):
		shift = {'id':i, 'day':int(shift_info[0]),'title':shift_info[1],'start_time':float(shift_info[2]), 'end_time':float(shift_info[3]), 'covered':False}
		all_shifts.append(shift)
	shifts_file.close()
	return all_shifts


def working(stapher, new_shift):
	schedule_for_day = stapher['schedule'][new_shift['day']]
	for shift in schedule_for_day:
		if new_shift['start_time'] is shift['start_time']:
			return True
		if new_shift['start_time'] < shift['end_time'] and new_shift['end_time'] > shift['start_time']:
			return True
	return False


def meets_constraints(stapher,shift):
	# no two people can work one shift
	if shift['covered']:
		return False
	# a worker can't work 2 shifts at once
	elif working(stapher, shift):
		return False
	else:
		return True
		

def automate_schedules(staph,shifts):
	uncovered_shifts = {'name':'UNCOVERED', 'schedule':{0:[],1:[],2:[],3:[],4:[],5:[],6:[]}}
	for shift in shifts:
		for stapher in staph:
			if meets_constraints(stapher, shift):
				stapher['schedule'][shift['day']].append(shift)
				shift['covered'] = True
		if not shift['covered']:
			uncovered_shifts['schedule'][shift['day']].append(shift)
	# just testing code
	staph.append(uncovered_shifts)
	for stapher in staph:
		s = stapher['schedule']
		total_shifts = len(s[0]) + len(s[1]) + len(s[2]) + len(s[3]) + len(s[4]) + len(s[5]) + len(s[6])
		print stapher['name'], ':', total_shifts, 'shifts'
		print_schedule(stapher)

def print_schedule(stapher):
	print stapher['name'], '\'s Schedule'
	days = ['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
	for i in range(0,7):
		print '	',days[i]
		for shift in stapher['schedule'][i]:
			print '		',shift['title'], 'from', shift['start_time'],'to', shift['end_time']		

if __name__ == "__main__":
	all_staph = get_staph_data('2016-ski-dock.csv')
	all_shifts = get_shifts_data('2016-ski-dock-shifts.csv')
	automate_schedules(all_staph,all_shifts)




