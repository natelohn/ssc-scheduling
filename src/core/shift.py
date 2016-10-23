#########################################################################################################
# A Class to represent a single shift, it has a day of the week (represented by an int 0-6), 			#
# a start time and an end time (represented by a float 0.0-24.0), and a title.							#
# What it doesn't have is the touch of magic that is experienced by everyone involed					#
#########################################################################################################
class Shift:

	def __init__(self,day,title,start,end):
		self.day = day
		self.title = title
		self.start = start
		self.end = end 
		self.covered = False