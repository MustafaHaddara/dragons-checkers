import pygame
import Board

#Template and fallback functions for Views
class ViewBase:
	#Constructor: Sets up the view template to use
	#screen: The screen to draw on; board: the active board; buttons: The buttons to display
	def __init__(self,screen, board, buttons):
		self._screen = screen
		self._board = board
		self._buttons = buttons

	#draw: Draws to the screen.
	def draw(self):
		pass

	#getBoard: Gets the current board
	#Returns the current Board class being used
	def getBoard(self):
		return self._board
