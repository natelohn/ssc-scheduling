from schedule import Schedule

#########################################################################################################
# A Class to represent the dopest type of person to ever exist, an SSC stapher, while all stapher's     #
# a complex things, this class is not. It includes, a name, a type, and a schedule.						#
#########################################################################################################
class Stapher:

	def __init__(self,name,position):
		self.name = name
		self.position = position
		self.schedule = Schedule()


	def free_during_shift(self,new_shift):
		day_schedule = self.schedule.get_day_schedule(new_shift.day)
		for shift in day_schedule:
			if new_shift.start is shift.start:
				return False
			if new_shift.start < shift.end and new_shift.end > shift.start:
				return False
		return True

	def print_info(self):
		print self.name, 'works', self.position, 'and has' , self.schedule.total_shifts, 'shifts.'