import pygame

#Template and fallback functions for controllers
class ControllerBase:
	#Constructor: Sets up the controller template to use
	#quitmethod: The method to call if pygame wishes to terminate; board: The current board being used
	def __init__(self, quitmethod, board):
		self._buttons = []
		self._board = board
		#[Left mouse button, middle mouse button, right mouse button]
		self._mouseState = [0,0,0]
		self._quitmethod = quitmethod

	#setButtons: Registers the current buttons on the view with the controller
	#buttons: A list of buttons to make the list of buttons recognized by the controller
	def setButtons(self, buttons):
		self._buttons = buttons

	#runEvents: Checks if the current event in the queue has a defined behaviour for it.
	#Acts as a default to handle the termination of pygame, if it wishes to quit.
	#event: The event currently being evaluated/dispatched
	def runEvents(self, event):
		if event.type == pygame.QUIT:
			self._quitmethod()
