import pygame
from ControllerBase import *

#Controller for STATE_NEW_GAME_MENU
class ControllerNewGameState(ControllerBase):

	#Constructor: Sets up the controller template to use
	#quitmethod: The method to call if pygame wishes to terminate; board: The current board being used
	def __init__(self, quitmethod, board):
		ControllerBase.__init__(self, quitmethod, board)
		self._board.setPositions()
		self._lastSelectedPiece = 0
		self._selectedColor = 0
		self._toggledAI = 0

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
				buttonClicked = self._buttons[i].isClicked(mPos_x, mPos_y);
				if  buttonClicked[0] == True:
					if(buttonClicked[1].endswith("Normal")):
						self._buttons[self._lastSelectedPiece].setOverlay(None)
						self._buttons[i].setOverlay("pieceOverlay")
						self._lastSelectedPiece = i
						self._selectedColor = (buttonClicked[1].startswith("black"))*1
					if(buttonClicked[1].endswith("AIOnButton")):
						if(not self._toggledAI):
							self._buttons[i].setOverlay("ToggleAIOffButton")
						else: 
							self._buttons[i].setOverlay(None)
						self._toggledAI = not self._toggledAI
					self._buttons[i].function()()
		#Check to see if the Base handles this message
		ControllerBase.runEvents(self, event)

	#setButtons: Registers the current buttons on the view with the controller
	#buttons: A list of buttons to make the list of buttons recognized by the controller
	#Extends the setButtons method of the base class by setting the default overlay when loaded
	def setButtons(self, buttons):
		ControllerBase.setButtons(self, buttons)
		for i in range(len(self._buttons)):
			if(self._buttons[i].getKind() == "redButtonNormal"):
				self._lastSelectedPiece = i
				self._selectedColor = 0
				self._buttons[i].setOverlay("pieceOverlay")
			else:
				self._buttons[i].setOverlay(None)

	#getGameParams: Returns the colour of player one as 0 for red and 1 for black, as well as whether the AI is toggled as a boolean.
	#Returns: The colour of player 1 and whether the AI is toggled.
	def getGameParams(self):
		return self._selectedColor, not self._toggledAI
