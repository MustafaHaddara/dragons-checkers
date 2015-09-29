import pygame
from ViewBase import *
import Button
import Timer
#Error message handler
import Tkinter
import tkMessageBox
import sys

#View for STATE_PLAY
class ViewPlayState(ViewBase):

	#Constructor: Sets up the view template to use
	#screen: The screen to draw on; board: the active board; buttons: The buttons to display
	def __init__(self,screen, board, buttons):
		ViewBase.__init__(self, screen, board, buttons)
		self._selectedPiece = None
		self._activePlayer = None
		self._colorMode = 0#0 for 1st player red, 1 for first player black
		self._boardLock = None
		self._AIPlayer = False
		self._fntColor = (244, 197, 8)
		self._timer = None
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
			self._player = [
						pygame.image.load("Graphics/player1.png"),
						pygame.image.load("Graphics/player2.png")
						]
			self._pieceColor = [
						pygame.image.load("Graphics/RedBar.png"),
						pygame.image.load("Graphics/BlackBar.png")
						]
			self._decal = [
						pygame.image.load("Graphics/redDecal.png"),
						pygame.image.load("Graphics/blackDecal.png")
			]
			self._fnt = pygame.font.Font("Graphics/font.ttf", 50)
		except:
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Uh oh!", "Images not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
			#Exit to stop a further exception
			sys.exit()

	#draw: Draws to the screen.
	def draw(self):
		self._screen.blit(self._background, (0,0))
		self._screen.blit(self._drawer, (0,640))
		if(self._boardLock != None):
			self._boardLock.acquire()
		for i in range(8):
			for j in Board.boardIterator(i):
				if(self._board.isPiece(i,j)):
					self._screen.blit(self._pieces[self._board.isKing(i,j)<<1 | self._board.getPlayer(i,j)], (i*80,j*80))
		if(self._boardLock != None):
			self._boardLock.release()
		for i in range(len(self._buttons)):
			self._buttons[i].draw(self._screen)
		#Draw lambda related functions:
		if(self._selectedPiece != None and self._selectedPiece() != [-1,-1]):
			self._screen.blit(self._pieceOverlay, (self._selectedPiece()[0]*80,self._selectedPiece()[1]*80))
		if(self._activePlayer != None):
			self._screen.blit(self._pieceColor[abs(self._colorMode-self._activePlayer())], (240,657))
			self._screen.blit(self._player[self._activePlayer()], (290,657))
			if(self._AIPlayer):
				self._screen.blit(self._decal[self._colorMode], (130,670))
			else:
				self._screen.blit(self._decal[abs(self._colorMode-self._activePlayer())], (130,670))
		#Timer updates
		if(self._timer != None):
			time = self._timer.getTime()
			if time < 10:
				self._fntColor = (255, 57, 65)
				t = "0" + str(time)
			else:
				self._fntColor = (244, 197, 8)
				t = str(time)
			self._screen.blit(self._fnt.render(t, True, self._fntColor), (410, 643))

	#setLambdasForView: Take a list of lambda functions to affect the drawing of components on the view
	#lambdas: Takes a list of lambda functions to be used
	def setLambdasForView(self, lambdas):
		self._selectedPiece = lambdas[1]
		self._activePlayer = lambdas[0]

	#setPlayerColors: Sets whether the first player is red or black.
	#Color: The color player 1 should be.
	def setPlayerColors(self, color):
		if color != self._colorMode:
			#Do a colour swap of the pieces indices and update colorMode
			self._pieces = [self._pieces[1], self._pieces[0], self._pieces[3], self._pieces[2]]
			self._colorMode = color

	#getPlayerColors: Returns whether the first player is red or black
	#Returns: whether player 1 is red or black
	def getPlayerColors(self):
		return self._colorMode

	#setAIPlayer: Sets a boolean that is used to associate which color is conceding when the button is clicked
	#AI: True if there is AI
	def setAIPlayer(self, AI):
		self._AIPlayer = AI

	#setBoardLockObj: Sets the _boardLock to avoid a race condition with board.
	def setBoardLockObj(self, lockObj):
		self._boardLock = lockObj

	#setTimer: Sets the timer object to track turns
	#timer: The Timer object to use
	def setTimer(self, timer):
		self._timer = timer

	#getTimer: Gets the timer
	#Returns: The Timer object
	def getTimer(self):
		return self._timer