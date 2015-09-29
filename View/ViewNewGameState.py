import pygame
from ViewBase import *
import Button
#Error message handler
import Tkinter
import tkMessageBox
import sys

#View for STATE_NEW_GAME_MENU
class ViewNewGameState(ViewBase):

	#Constructor: Sets up the view template to use
	#screen: The screen to draw on; board: the active board; buttons: The buttons to display
	def __init__(self,screen, board, buttons):
		ViewBase.__init__(self, screen, board, buttons)
		try:
			self._background = pygame.image.load("Graphics/helpMenu.png")
			self._drawer = pygame.image.load("Graphics/optionsMenu.png")
		except:
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Uh oh!", "Images not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
			#Exit to stop a further exception
			sys.exit()

	#draw: Draws to the screen.
	def draw(self):
		self._screen.blit(self._background, (0,0))
		self._screen.blit(self._drawer, (0,640))
		for i in range(len(self._buttons)):
			self._buttons[i].draw(self._screen)