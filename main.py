import sys
import pygame

from View import ViewStartState
from View import ViewPlayState
from View import ViewNewGameState
from View import ViewGameOverState

from Controller import ControllerStartState
from Controller import ControllerPlayState
from Controller import ControllerNewGameState
from Controller import ControllerGameOverState

import Button
import Board
from BoardException import *
import SaveFile
import thread
import Timer

#Error message handler
import Tkinter
import tkMessageBox

#States
STATE_START_MENU = 0
STATE_NEW_GAME_MENU = 1
STATE_PLAY = 2
STATE_GAME_OVER = 3

class StateMachine:
	#Constructor: Constructor for the state machine
	def __init__(self):
		pygame.init()

		# Initial screen
		self._size = 640, 720

		try:
			icon = pygame.image.load("Graphics/icon.png")
		except:
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Uh oh!", "Image not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
			#Exit to stop a further exception
			sys.exit()
		pygame.display.set_icon(icon)
		self._screen = pygame.display.set_mode(self._size)
		pygame.display.set_caption("Here be Dragons, also Checkers")
	
		self._screen.convert_alpha()

		#State class association table
		self._stateClassAssocTable = [
										ViewStartState.ViewStartState, #STATE_START_MENU
										ViewNewGameState.ViewNewGameState,#STATE_NEW_GAME_MENU
										ViewPlayState.ViewPlayState, 	 #STATE_PLAY
										ViewGameOverState.ViewGameOverState #STATE_GAME_OVER
									]
		self._stateControllerAssocTable = [
											ControllerStartState.ControllerStartState, 	#STATE_START_MENU
											ControllerNewGameState.ControllerNewGameState,	#STATE_NEW_GAME_MENU
											ControllerPlayState.ControllerPlayState,		#STATE_PLAY
											ControllerGameOverState.ControllerGameOverState #STATE_GAME_OVER
										]
		self._stateButtonAssocTable = [
						[	
							Button.Button(240, 327, "startButton", lambda: self.newState(STATE_NEW_GAME_MENU)),
							Button.Button(240, 387, "loadButton", lambda: self.load())
						], #STATE_START_MENU
						[
							Button.Button(480,657, "startButton", lambda: self.newState(STATE_PLAY)),
							Button.Button(300,657, "ToggleAIOnButton", lambda: 0),
							Button.Button(20,660, "backArrow", lambda: self.newState(STATE_START_MENU)),
							Button.Button(70,650, "redButtonNormal", lambda: 0, Button.Button.TYPE_CIRCLE), 
							Button.Button(140,650, "blackButtonNormal", lambda: 0, Button.Button.TYPE_CIRCLE)
						],#START_NEW_GAME_MENU
						[
							Button.Button(0, 657, "quitButton", lambda: self.newState(STATE_START_MENU)),
							Button.Button(120, 657, "concedeButton", lambda: self.newState(STATE_GAME_OVER)),#Concede button based on turn
							Button.Button(480,657, "saveButton", lambda: self.save())
						], #STATE_PLAY
						[
							Button.Button(0, 657, "quitButton", lambda: self.newState(STATE_START_MENU))
						] #STATE_GAME_OVER
					]

		#set current state
		self._state = STATE_START_MENU
		self._controller = None
		self._sb = None

		self.newState(self._state)

		self._done = False

	#runEventLoop: Runs the event loop that handles the calls to the current view and controller
	def runEventLoop(self):
		while not self._done:
			for ev in pygame.event.get():
				self._controller.runEvents(ev)
			self._sb.draw()
			pygame.display.flip()
		pygame.quit()
		#sys.exit()
		

	#newState: Updates the state machine to a new state
	def newState(self, ns):
		#Some information that may be transferred between states
		boardTest = None
		color = 0
		AI = 1
		winner = 0#0 red, 1 black
		#In new game state, grab their selections
		if(self._state == STATE_NEW_GAME_MENU):
			color, AI = self._controller.getGameParams()
		#If the game is about to be over, get the current player and the color to determine the winner.
		if(self._state == STATE_PLAY and ns == STATE_GAME_OVER):
			winner = not (self._sb.getPlayerColors() ^ self._controller.getActivePlayer())
			color = self._sb.getPlayerColors()
			#unload controller dependent Lambdas from view
			self._sb.setLambdasForView((None, None))
		if(self._state == STATE_PLAY):
			self._controller.timerStop()
		self._state = ns
		if not (self._sb is None):
			boardTest = self._sb.getBoard()
		self._controller = self._stateControllerAssocTable[self._state](self.quit, boardTest)
		self._sb = self._stateClassAssocTable[self._state](self._screen, boardTest,self._stateButtonAssocTable[self._state])
		self._controller.setButtons(self._stateButtonAssocTable[self._state])

		#Set Play settings
		if(isinstance(self._controller, ControllerPlayState.ControllerPlayState)):
			#Set up a boardLock to prevent a race condition
			boardLock = thread.allocate_lock()
			self._sb.setBoardLockObj(boardLock)
			self._controller.setBoardLockObj(boardLock)
			#Set up the parameters for the view
			turn = lambda: self._controller.getActivePlayer()
			selectedPiece = lambda: self._controller.getSelectedPiece()
			self._sb.setLambdasForView([turn,selectedPiece])
			self._sb.setPlayerColors(color)
			self._sb.setAIPlayer(not AI)
			timer = Timer.Timer()
			self._sb.setTimer(timer)
			self._controller.setTimer(timer)
			#Set controller parameters
			self._controller.setSecondPlayer(AI)
			self._controller.setActivePlayer(color)
			self._controller.setLambdasForController(lambda:self.newState(STATE_GAME_OVER))
			self._controller.initialGameOverCheck()
		#Set game over settings
		if(isinstance(self._controller, ControllerGameOverState.ControllerGameOverState)):
			self._sb.setPlayerColors(color)
			self._sb.setWinner(winner)

	#quit: Starts the shutdown of the application, is a callback
	def quit(self):
		self._done = True

	#load: Tries to load a game from the save file.
	def load(self):
		try:
			positions, first_player, second_player, playerTurn, turn_number, time = SaveFile.loadFile()
			self._sb.getBoard().setPositions(positions)
			self.newState(STATE_PLAY)
			self._sb.setPlayerColors(first_player)
			self._controller.setSecondPlayer(second_player)
			self._controller.setActivePlayer(playerTurn)
			self._controller.setTurnNumber(turn_number)
			timer = Timer.Timer()
			timer.setTime(time*1000)
			self._sb.setTimer(timer)
			self._controller.setTimer(timer)
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Load", "Load completed successfully.")
			

		except BoardException as e:
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Load Error", e)

	#save: Tries to save the current game to save file.
	def save(self):
		if not self._controller.canSave():
			Tkinter.Tk().wm_withdraw()
			tkMessageBox.showinfo("Save", "Can't save right now. Someone's turn is in progress!")
			return
		array = self._sb.getBoard().getRawBoard() 
		first_player = self._sb.getPlayerColors()
		second_player = self._controller.getSecondPlayer()
		turn = self._controller.getActivePlayer()
		turn_number = self._controller.getTurnNumber()
		timer = self._sb.getTimer()
		time = timer.getTime()

		SaveFile.saveFile(array, first_player, second_player, turn, turn_number,time)

		Tkinter.Tk().wm_withdraw()
		tkMessageBox.showinfo("Save", "Save completed successfully.")

#Bootstraps the StateMachine
if __name__ == "__main__":
	sm = StateMachine()
	sm.runEventLoop()
