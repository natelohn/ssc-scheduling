#########################################################################################################
# A Class to represent a set of shifts in a 7 day work week. The best set of 7 days ever.				#
#########################################################################################################
class Schedule:

	def __init__(self):
		self.all_shifts = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
		self.total_shifts = 0


	def get_day_schedule(self,day):
		return self.all_shifts[day]

	def add_shift(self,shift):
		self.all_shifts[shift.day].append(shift)
		shift.covered = True
		self.total_shifts = self.total_shifts + 1 

	def print_info(self):
		days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
		for i, day in enumerate(days):
			print '	', day
			day = self.get_day_schedule(i)
			order_shifts = []
			for time in range(0,24):
				for shift in day:
					if shift.start < time and shift not in order_shifts:
						order_shifts.append(shift)
			for shift in order_shifts:
				print ' 		', shift.title, 'from', shift.start, 'to', shift.end



		

