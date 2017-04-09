from schedule import Schedule

#########################################################################################################
# A Class to represent the dopest type of person to ever exist, an SSC stapher, while all staphers are  #
# complex things, this class is not. It includes, a name, a type, and a schedule.						#
#########################################################################################################
class Stapher:

	id_counter = 1

	def __init__(self,name,position,alt_positions):
		self.name = name
		self.position = position
		self.alt_positions = alt_positions
		self.schedule = Schedule()
		self.id = Stapher.id_counter
		Stapher.id_counter += 1


	def free_during_shift(self,new_shift):
		day_schedule = self.schedule.get_day_schedule(new_shift.day)
		
		for shift in day_schedule:
			if shift.time_overlaps_with(new_shift):
				return False
		
		return True

	def add_shift(self, shift):
		self.schedule.add_shift(shift)

	def print_info(self):
		print str(self)

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
		return (self.name + " works " + self.position + " and has " + 
			str(self.schedule.total_shifts) + " total shifts.")

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return self.id
