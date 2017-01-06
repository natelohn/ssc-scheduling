"""Hold values for all of the constants for the project."""

class Constants():

	"""This is a class for managing constants in the project."""

	STRINGS = {}

	@classmethod
	def get_string(cls, val, dictionary=None):
		"""Get the string representation of the given constant val.

		Looks in the subclass's dictionary called STRINGS. If there is none,
		returns the empty string.

		Parameters
		----------
		cls: class
			Name of the class in this file
		val: string
			value to retrieve
		dictionary: dictionary
			dictionary to use. default is cls.STRINGS

		Returns the value from the dictionary.
		"""
		if not dictionary:
			dictionary = cls.STRINGS

		if val in dictionary:
			return dictionary[val]

		return ""

	@classmethod
	def string_to_val(cls, string_rep):
		"""Find which constant value the STRING_REP is associated with.

		Given a string STRING_REP, find which constant value
		it is associated with.

		Parameters
		----------
		cls: class
			Name of the class in this file
		string_rep: string
			String representation of the constant value to look up

		Returns int.
		"""
		for pair in cls.STRINGS.iteritems():
			const = pair[0]
			string = pair[1]
			if string == string_rep:
				return const
		return -1

class Days(Constants):

	"""Constants for days of the week."""

	SUNDAY = 0
	MONDAY = 1
	TUESDAY = 2
	WEDNESDAY = 3
	THURSDAY = 4
	FRIDAY = 5
	SATURDAY = 6

	STRINGS = {}
	STRINGS[SUNDAY] = "Sunday"
	STRINGS[MONDAY] = "Monday"
	STRINGS[TUESDAY] = "Tuesday"
	STRINGS[WEDNESDAY] = "Wednesday"
	STRINGS[THURSDAY] = "Thursday"
	STRINGS[FRIDAY] = "Friday"
	STRINGS[SATURDAY] = "Saturday"

class Jobs(Constants):

	"""Constants for the different possible jobs."""

	MUNCHKINS = 0
	SNOOPERS = 1
	MENEHUNES = 2
	YAHOOS = 3
	MIDOREES = 4
	SUAVES = 5
	TEENS = 6
	SKI_DOCK = 7
	TENNIS = 8
	HIKING = 9
	OFFICE = 10
	CRAFTS = 11
	ART = 12
	PHOTO = 13
	KIDS_NAT = 14
	ADULT_NAT = 15
	THEATER = 16
	MUSIC = 17
	KGC = 18
	STAPH_D = 19

	STRINGS = {}
	STRINGS[MUNCHKINS] = "Munchkins"
	STRINGS[SNOOPERS] = "Snoopers"
	STRINGS[MENEHUNES] = "Menehunes"
	STRINGS[YAHOOS] = "Yahoos"
	STRINGS[MIDOREES] = "Midorees"
	STRINGS[SUAVES] = "Suaves"
	STRINGS[TEENS] = "Teens"
	STRINGS[SKI_DOCK] = "Ski Dock"
	STRINGS[TENNIS] = "Tennis"
	STRINGS[HIKING] = "Hiking"
	STRINGS[OFFICE] = "Office"
	STRINGS[CRAFTS] = "Crafts"
	STRINGS[ART] = "Art"
	STRINGS[PHOTO] = "Photo"
	STRINGS[KIDS_NAT] = "Kids Naturalist"
	STRINGS[ADULT_NAT] = "Adult Naturalist"
	STRINGS[THEATER] = "Theater"
	STRINGS[MUSIC] = "Music Director"
	STRINGS[KGC] = "Kids Group Coordinator"
	STRINGS[STAPH_D] = "Staph Director"


class ShiftCategory(Constants):

	"""Constants for the different types of shifts."""

	SPECIAL = 0
	OFF_DAY = 1
	PROGRAMMING = 2

	STRINGS = {}
	STRINGS[SPECIAL] = "Special"
	STRINGS[OFF_DAY] = "Off Day"
	STRINGS[PROGRAMMING] = "Programming"



	