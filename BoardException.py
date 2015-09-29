class BoardException(Exception):
	def __init__(self, value):
		self._value = value

	#The "string" value of this error message
	def __str__(self):
		return self._value