## timer.py
import pygame

#Timer control
class Timer:
	#Constructor: Initializes the Timer
	def __init__(self):
		self._timer = pygame.time.Clock()
		self._time = 60000

	#tick: Updates the timer
	def tick(self):
		self._time = self._time -  self._timer.tick()

	#reset: Resets the timer back to 60 seconds
	def reset(self):
		self._time = 60000

	#getTime: Returns the current time in seconds
	#Returns: the current time in seconds
	def getTime(self):
		t = self._time / 1000
		return t 

	#timeUP: Returns whether 60 seconds has elapsed
	#Returns: Whether 60 seconds has elapsed 
	def timeUp(self):
		return self._time <= 0

	#setTime: Sets the time
	def setTime(self, time):
		self._time = time