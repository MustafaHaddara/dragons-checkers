import pygame
from ControllerBase import *

#Controller for STATE_START_MENU
class ControllerStartState(ControllerBase):

	#Constructor: Sets up the controller template to use
	#quitmethod: The method to call if pygame wishes to terminate; board: The current board being used
	def __init__(self, quitmethod, board):
		ControllerBase.__init__(self, quitmethod, board)

	#runEvents: Checks if the current event in the queue has a defined behaviour for it.
	#event: The event currently being evaluated/dispatched
	def runEvents(self, event):
		#Clicks are handled when the mouse is released
		if pygame.mouse.get_pressed()[0]:
			self._mouseState[0] = True
		#The mouse was released
		if (not pygame.mouse.get_pressed()[0]) and self._mouseState[0]:
			self._mouseState[0] = False
			mPos_x = pygame.mouse.get_pos()[0]
			mPos_y = pygame.mouse.get_pos()[1]
			#Check to see if the click occurred within the bounds of a button
			for i in range(len(self._buttons)):
				if self._buttons[i].isClicked(mPos_x, mPos_y)[0] == True:
					self._buttons[i].function()()
		#Check to see if the Base handles this message
		ControllerBase.runEvents(self, event)
