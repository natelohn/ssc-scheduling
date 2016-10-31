import constants as C

#########################################################################################################
# A Class to represent a single shift, it has a day of the week (represented by an int 0-6), 			#
# a start time and an end time (represented by a float 0.0-24.0), and a title.							#
# What it doesn't have is the touch of magic that is experienced by everyone involed					#
#########################################################################################################
class Shift:

	id_counter = 1

	def __init__(self,day,title,start,end,shift_type=C.ShiftTypes.GENERAL):
		self.day = day
		self.title = title
		self.start = start
		self.end = end 
		self.covered = False
		self.shift_type = shift_type
		self.id = Shift.id_counter
		Shift.id_counter += 1

	def time_overlaps_with(self, other):
		# If the shifts are on different days, no overlap
		if self.day != other.day:
			return False

		# If shifts start at the same time, then they overlap
		if self.start == other.start:
			return True
		# If self starts earlier, they overlap if other's start is before self's end
		elif self.start < other.start:
			return other.start < self.end
		# If self starts later, they overlap if self's start is before other's end
		else:
			return self.start < other.end

		return False


	def __eq__(self, other):
		"""Overwrite the default == behavior."""
		if type(self) is type(other):
			return self.id == other.id
		return False

	def __ne__(self, other):
		"""Overwrite the default != behavior."""
		if type(self) is type(other):
			return not self.__eq__(other)
		return False

	def __str__(self):
		return (self.title + ": " + get_day_string(self.day) + " " + 
			str(self.start) + " - " + str(self.end))

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return self.id

def get_day_string(day_num):
	day_strings = {
		0 : "Sunday",
		1 : "Monday",
		2 : "Tuesday",
		3 : "Wednesday",
		4 : "Thursday",
		5 : "Friday",
		6 : "Saturday"
	}

	return day_strings[day_num]

