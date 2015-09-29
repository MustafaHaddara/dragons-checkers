import pygame
from ViewBase import *
import Button
#Error message handler
import Tkinter
import tkMessageBox
import sys

#View for STATE_GAME_OVER
class ViewGameOverState(ViewBase):

	#Constructor: Sets up the view template to use
	#screen: The screen to draw on; board: the active board; buttons: The buttons to display
	def __init__(self,screen, board, buttons):
		ViewBase.__init__(self, screen, board, buttons)
		self._colorMode = 0#0 for 1st player red, 1 for first player black
		self._winner = 0
		try:
			self._background = pygame.image.load("Graphics/board.png")
			self._drawer = pygame.image.load("Graphics/optionsMenu.png")
			self._pieceOverlay = pygame.image.load("Graphics/pieceOverlay80.png")
			self._pieces = [
						pygame.image.load("Graphics/redNormal.png"),
						pygame.image.load("Graphics/blackNormal.png"),
						pygame.image.load("Graphics/redKing.png"),
						pygame.image.load("Graphics/blackKing.png")
						]
			self._win = [
						pygame.image.load("Graphics/RedWin.png"),
						pygame.image.load("Graphics/BlackWin.png"),
			]
		except:
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Uh oh!", "Images not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
			#Exit to stop a further exception
			sys.exit()

	#draw: Draws to the screen.
	def draw(self):
		self._screen.blit(self._background, (0,0))
		self._screen.blit(self._drawer, (0,640))
		for i in range(8):
			for j in Board.boardIterator(i):
				if(self._board.isPiece(i,j)):
					self._screen.blit(self._pieces[self._board.isKing(i,j)<<1 | self._board.getPlayer(i,j)], (i*80,j*80))
		for i in range(len(self._buttons)):
			self._buttons[i].draw(self._screen)			
		self._screen.blit(self._win[self._winner], (0,320))

	#setPlayerColors: Sets whether the first player is red or black.
	#Color: The color player 1 should be.
	def setPlayerColors(self, color):
		if color != self._colorMode:
			#Do a colour swap of the pieces indices and update colorMode
			self._pieces = [self._pieces[1], self._pieces[0], self._pieces[3], self._pieces[2]]
			self._colorMode = color

	#setWinner: Sets the winner of the game
	#winner: The winner
	def setWinner(self, winner):
		self._winner = winner