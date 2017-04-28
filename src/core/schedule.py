#########################################################################################################
# A Class to represent a set of shifts in a 7 day work week. The best set of 7 days ever.				#
#########################################################################################################
class Schedule:

	def __init__(self):
		self.all_shifts = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
		self.total_shifts = 0
		self.total_special_shifts = 0
		self.special_shift_types = []
		self.off_shifts = []
		self.programming_hours = 0


	def get_day_schedule(self,day):
		return self.all_shifts[day]

	def add_shift(self,shift):
		shift.covered = True
		self.all_shifts[shift.day].append(shift)
		self.total_shifts = self.total_shifts + 1

	def remove_shift(self,shift):
		shift.covered = False
		self.all_shifts[shift.day].remove(shift)
		self.total_shifts = self.total_shifts - 1

	def get_sorted_shift_times_for_day(self,day):
		times = []
		for shift in self.all_shifts[day]:
			if shift.title != 'Off Day':
				times.append([shift.start,shift.end])
		last_time = [0,0]
		for time_set in sorted(times):
			if last_time[1] > time_set[0]:
				print '*****************************************I FUCKED UP SORTING TIMES!*****************************************', last_time,time_set
			last_time = time_set
		return sorted(times)

	def print_info(self):
		days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
		for i, day in enumerate(days):
			print '		', day
			shifts = self.get_day_schedule(i)
			order_shifts = []
			for time in range(0,24):
				for shift in shifts:
					if shift.start < time and shift not in order_shifts:
						order_shifts.append(shift)
			for shift in order_shifts:
				print ' 			',shift.title,'from',shift.start,'to',shift.end