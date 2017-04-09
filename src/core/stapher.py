from schedule import Schedule

#########################################################################################################
# A Class to represent the dopest type of person to ever exist, an SSC stapher, while all staphers are  #
# complex things, this class is not. It includes, a name, a type, and a schedule.						#
#########################################################################################################
class Stapher:

	id_counter = 1

	def __init__(self,name,gender,positions):
		self.name = name
		self.gender = gender
		self.positions = positions
		self.schedule = Schedule()
		self.special_shift_preferences = []
		self.restricted_off_days = []
		self.id = Stapher.id_counter
		Stapher.id_counter += 1

	def total_shifts(self):
		return self.schedule.total_shifts

	def programming_hours(self):
		return self.schedule.programming_hours

	def free_during_shift(self,new_shift):
		return self.free_during_time(new_shift.day, new_shift.start, new_shift.end)

	def free_during_time(self, day, start, end):
		day_schedule = self.schedule.get_day_schedule(day)
		for shift in day_schedule:
			if shift.time_overlaps(start, end):
				return False
		return True

	def add_shift(self, shift):
		self.schedule.add_shift(shift)

	def remove_shift(self, shift):
		self.schedule.remove_shift(shift)
		
	def print_info(self):
		print str(self)

	def clear_schedule(self):
		for day in self.schedule.all_shifts.keys():
			for shift in self.schedule.all_shifts[day]:
				self.remove_shift(shift)

	def clear_shifts_of_category(self,category):
		for day in self.schedule.all_shifts.keys():
			for shift in self.schedule.all_shifts[day]:
				if shift.category == category:
					self.remove_shift(shift)

	def reached_programming_limit_week(self, shift, constraint_info):
		max_hours = 0 - shift.length
		for position in self.positions:
			max_hours += constraint_info['max_programming_hours'][position]
		return self.schedule.programming_hours >= max_hours

	def reached_programming_limit_type(self, shift, constraint_info):
		max_hours = constraint_info['max_programming_hours_of_type'][shift.type][shift.day]
		return self.schedule.programming_hours_of_type_in_day(shift) >= max_hours

	# Not the best solution, but a quick way to implement without using python time objects
	def off_day_scheduled(self):
		return len(self.schedule.off_shifts) == 2

	def same_off_day(self, off_shift):
		for shift in self.schedule.off_shifts:
			if shift.type != off_shift.type:
				return False
		return True

	def __eq__(self, other):
		"""Override the default == behavior"""
		if type(other) is type(self):
			return self.name == other.name and self.position == other.position
		return False

	def __ne__(self, other):
		"""Override the default != behavior"""
		if type(other) is type(self):
			return not self.__eq__(other)

	def __str__(self):
		extra_pos = ''
		for pos in self.positions[1:]:
			extra_pos += ', ' + pos
		return ('NAME: '+ self.name + ", JOB(S): " + self.positions[0] + extra_pos)

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return self.id
