import os
from schedule import Schedule

#########################################################################################################
# A Class to represent the dopest type of person to ever exist, an SSC stapher, while all staphers are  #
# complex things, this class is not. It includes, a name, a type, and a schedule.						#
#########################################################################################################
class Stapher:

	id_counter = 1

	def __init__(self,name,summers,class_year,gender,positions):
		self.name = name
		self.summers = int(summers)
		self.class_year = int(class_year)
		self.gender = gender
		self.positions = positions
		self.schedule = Schedule()
		self.special_shift_preferences = []
		self.restricted_off_days = []
		self.has_car = False
		self.pairs_to_avoid = []
		self.id = Stapher.id_counter
		Stapher.id_counter += 1

	def is_returner(self):
		return self.summers > 0

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

	def all_shifts(self):
		all_shifts = []
		for day in self.schedule.all_shifts:
			for shift in self.schedule.all_shifts[day]:
				all_shifts.append(shift)
		return all_shifts

	def all_programming_shifts(self):
		all_programming_shifts = []
		for day in self.schedule.all_shifts:
			for shift in self.schedule.all_shifts[day]:
				if shift.is_programming:
					all_programming_shifts.append(shift)
		return all_programming_shifts

	def get_programming_hours_by_day(self,day):
		programming_hours = 0
		for shift in self.schedule.all_shifts[day]:
			if shift.is_programming:
				programming_hours += shift.length
		return programming_hours

	def get_programming_shifts_by_day(self,day):
		programming_shifts = []
		for shift in self.schedule.all_shifts[day]:
			if shift.is_programming:
				programming_shifts.append(shift)
		return programming_shifts


	def work_times_by_day(self):
		work_times_by_day = {}
		for day in range(0,7):
			sorted_times = self.schedule.get_sorted_shift_times_for_day(day)
			last_shift_time = [0,0]
			squished_times = []
			for shift_time in sorted_times:
				if last_shift_time[1] == shift_time[0]:
					# print last_shift_time, shift_time
					last_shift_time = [last_shift_time[0],shift_time[1]]
					# print '	->', last_shift_time
				else:
					# print 'Add',last_shift_time
					squished_times.append(last_shift_time)
					last_shift_time = shift_time
			squished_times.append(last_shift_time)
			squished_times.remove([0,0])
			work_times_by_day[day] = squished_times
		return work_times_by_day

	def get_lengths_without_break(self):
		lengths = []
		times_by_day = self.work_times_by_day()
		for day in times_by_day:
			for time in times_by_day[day]:
				length = time[1] - time[0]
				lengths.append(length)
		return lengths
	

	def meal_break_violations(self):
		meal_break_violations = 0
		lengths_without_break = self.get_lengths_without_break()
		for length in lengths_without_break:
			if length > 5:
				meal_break_violations += 1
		return meal_break_violations


	def length_of_day(self,day):
		day_schedule = self.schedule.get_day_schedule(day)
		day_length = 0
		for shift in day_schedule:
			day_length += shift.length
		return day_length
		

	def add_shift(self, shift):
		if shift.covered:
			print self.name,'CANNOT TAKE',shift,'. IT IS ALREADY COVERED BY',shift.stapher.name
			quit()
		if self.free_during_shift(shift):
			self.schedule.add_shift(shift)
			shift.stapher = self
		else:
			print 'ERROR: CAN NOT ADD SHIFT "' +  str(shift) + '" TO', self.name, 'SCHEDULE.'
			quit()

	def remove_shift(self, shift):
		self.schedule.remove_shift(shift)
		
	def print_schedule(self):
		self.schedule.print_info()

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
