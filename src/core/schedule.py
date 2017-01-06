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
		if shift.is_special():
			self.total_special_shifts = self.total_special_shifts + 1
			self.special_shift_types.append(shift.type)
		if shift.is_off_day():
			self.off_shifts.append(shift)
		if shift.is_programming():
			self.programming_hours += shift.length

	def remove_shift(self,shift):
		shift.covered = False
		self.all_shifts[shift.day].remove(shift)
		self.total_shifts = self.total_shifts - 1
		if shift.is_special():
			self.total_special_shifts = self.total_special_shifts - 1
			self.special_shift_types.remove(shift.type)
		if shift.is_off_day():
			self.off_shifts.remove(shift)
		if shift.is_programming():
			self.programming_hours -= shift.length

	def programming_hours_in_day(self, day):
		programming_hours = 0
		for shift in self.get_day_schedule(day):
			if shift.is_programming():
				programming_hours += shift.length
		return programming_hours

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