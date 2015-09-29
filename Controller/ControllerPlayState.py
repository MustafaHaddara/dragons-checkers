import pygame
from ControllerBase import *
import AI
import thread#For AI to not lock up the UI thread with artificial delays
import time

#Controller for STATE_PLAY
class ControllerPlayState(ControllerBase):

	#Constructor: Sets up the controller template to use
	#quitmethod: The method to call if pygame wishes to terminate; board: The current board being used
	def __init__(self, quitmethod, board):
		ControllerBase.__init__(self, quitmethod, board)
		self._2ndPlayer = 1 #0 for AI, 1 for Human
		self._playerTurn = 1#Current players turns
		self._selectedPiece = [-1,-1] #The selected piece to use for the overlay
		self._jumpedThisTurn = False #Whether the current player has jumped this turn
		self._board.updateJumpList() #Update movable and jumpable piece
		self._gameOverStub = None#A lambda to execute when the game is over
		self._AIHandle = None #A handle for the AI class
		self._boardLock = None #A lock to prevent a race condition
		self._gameConceded = False #Check whether the game is conceded
		self._timer = None
		self._timerAbort = False
		self._timerRunning = False


	#runEvents: Checks if the current event in the queue has a defined behaviour for it.
	#event: The event currently being evaluated/dispatched
	def runEvents(self, event):
		#Clicks are handled when the mouse is released
		if pygame.mouse.get_pressed()[0]:
			self._mouseState[0] = True

		if pygame.mouse.get_pressed()[2]:
			self._mouseState[2] = True


		#The mouse was released
		if (not pygame.mouse.get_pressed()[0]) and self._mouseState[0]:
			self._mouseState[0] = False
			mPos_x = pygame.mouse.get_pos()[0]
			mPos_y = pygame.mouse.get_pos()[1]
			#Check to see if the click occurred within the bounds of a button
			for i in range(len(self._buttons)):
				if self._buttons[i].isClicked(mPos_x, mPos_y)[0] == True:
					if(self._buttons[i].isClicked(mPos_x, mPos_y)[1].startswith("concede")):
						#If we're playing the AI we always concede
						if(self._2ndPlayer == 0):
							self._playerTurn = 0
						self._gameConceded = True
					self._buttons[i].function()()

			#If we're playing the AI and it's the AI's turn, we can't select pieces
			if(not (self._playerTurn == 1 and self._2ndPlayer == 0)):
				mPos_x = mPos_x/80
				mPos_y = mPos_y/80
				#Check to see if a click was on a piece
				if(self._selectedPiece[0] == -1):
					if(self._playerTurn == self._board.getPlayer(mPos_x,mPos_y)):
						if(self._board.isSelectablePiece(mPos_x, mPos_y)):
							self._selectedPiece = [mPos_x, mPos_y]
				#A piece was selected
				else:
					if(self._playerTurn == self._board.getPlayer(self._selectedPiece[0],self._selectedPiece[1]) ):
						if(not self._board.isPiece(mPos_x, mPos_y) and self._board.isValidPosition(mPos_x, mPos_y) ):
							moveResult = self._board.movePiece(self._selectedPiece[0],self._selectedPiece[1], mPos_x, mPos_y)
							if(moveResult == 1):
								self._selectedPiece = [mPos_x, mPos_y]
								self._jumpedThisTurn = True
							if (moveResult == 0):
								self._changeTurns()
						#Implemented to select another piece if one is selected via left mouse as suggested in feedback
						if(self._board.isPiece(mPos_x, mPos_y) and self._board.getPlayer(mPos_x, mPos_y) == self._playerTurn and not self._jumpedThisTurn and (mPos_x, mPos_y) in self._board.getMovablePieces(self._playerTurn)):
							self._selectedPiece = [mPos_x, mPos_y]

		#Right Mouse release
		if (not pygame.mouse.get_pressed()[2]) and self._mouseState[2]:
			self._mouseState[2] = False
			mPos_x = pygame.mouse.get_pos()[0]/80
			mPos_y = pygame.mouse.get_pos()[1]/80
			#Deselect a piece if it's selected and hasn't been forced to jump
			if(self._jumpedThisTurn == False or not (self._playerTurn == 1 and self._2ndPlayer == 0)):
				if (mPos_x == self._selectedPiece[0] and mPos_y == self._selectedPiece[1]):
					self._selectedPiece = [-1,-1]

		#Check to see if the Base handles this message
		ControllerBase.runEvents(self, event)

	#_AISelectedPiece: AI Callback to allow the controller to set which piece it slected.
	#x: The x-coordinate of the piece selected; y: The y coordinate of the piece selected
	def _AISelectedPiece(self, x,y):
		self._selectedPiece = [x,y]

	#_changeTurns: Changes the turn of who is currently playing, runs the AI if it is it's turn.
	def _changeTurns(self):
		self._selectedPiece = [-1,-1]
		self._board.updateJumpList()
		self._playerTurn = not self._playerTurn
		self._timer.reset()
		#Returns if we get a game over to prevent the thread from starting
		if self._gameOverCheck(self._playerTurn) or self._gameConceded:
			return
		self._jumpedThisTurn = False
		#AI Thing: Do your thing
		if(self._2ndPlayer == 0 and self._playerTurn == 1):
			thread.start_new_thread(self._AIHandle.runAI, (lambda:self._changeTurns(),lambda:self._AIConcede(),self._AISelectedPiece))

	#_AIConcede: AI callback when it wants to concede
	def _AIConcede(self):
		self._gameConceded = True
		self._gameOverStub()


	#initialGameOverCheck: Checks if the save file came from an earlier version and somehow they saved a "bad" game, check if the game is already over
	def initialGameOverCheck(self):
		self._gameOverCheck(0)
		self._gameOverCheck(1)

	#_gameOverCheck: Checks if the game is over for a given player
	#player: The player to check if they are done
	#Returns: True if the game is over and a player loses.
	def _gameOverCheck(self, player):
		if self._board.isNoMovesAvailable(player):
			if(self._gameOverStub != None):
				self._gameOverStub()
				return True
		return False

	def setLambdasForController(self, lam):
		self._gameOverStub = lam

	#setActivePlayer: Sets the active player whose turn it is.
	#activePlayer: An integer of 0 or 1 for Player 1 and 2 respectively.
	def setActivePlayer(self, activePlayer):
		self._playerTurn = not activePlayer
		self._changeTurns()

	#setSecondPlayer: Sets whether the second player is a human or AI
	#secondPlayer: An integer of 0 or 1 representing 0 for AI and 1 for human
	def setSecondPlayer(self, secondPlayer):
		self._2ndPlayer = secondPlayer
		if(self._2ndPlayer == 0):
			self._AIHandle = AI.AI(self._board)
			if(self._boardLock != None):
				self._AIHandle.setBoardLockObj(self._boardLock)

	#getSecondPlayer: Returns whether the second player is human or not
	#Returns: An integer of 0 if the second player is AI and 1 if it is human
	def getSecondPlayer(self):
		return self._2ndPlayer

	#getActivePlayer: Returns whether the it is player 0 or 1's turn
	#Returns: An integer of who's turn it is.
	def getActivePlayer(self):
		return self._playerTurn

	#getSelectedPiece: Get's the actively selected piece
	#Returns: A 2 element array with the x position and y position of the selected piece
	def getSelectedPiece(self):
		return self._selectedPiece

	#getTurnNumber: returns the turn number
	def getTurnNumber(self):
		if(self._AIHandle != None):
			return self._AIHandle.getTurnNumber()
		else:
			return 0


	#setTurnNumber: Sets the number of jumpless turns the AI has had
	#number: The number of turns
	def setTurnNumber(self, number):
		if(self._AIHandle != None):
			self._AIHandle.setTurnNumber(number)

	#To prevent cheating, a player could make a move that gives the AI two jump possibilities, they could you a specific timing of saving before the AI makes a move
	#to save, if the AI takes a jump that is less favourable for the player, then they can back out and keep retrying until the AI picks the less favourable route. 
	#Of course they could take the more difficult route of saving before starting their turn, but if they want to cheat through trial and error, that's their choice.
	def canSave(self):
		if(self._playerTurn == 0 and self._selectedPiece == [-1,-1] or self._playerTurn == 1 and self._2ndPlayer == 1 and self._selectedPiece == [-1,-1]):
			return True
		return False

	#setBoardLockObj: Sets the _boardLock to avoid a race condition with board.
	def setBoardLockObj(self, lockObj):
		self._boardLock = lockObj

	#setTimer: Sets the timer object to track turns
	#timer: The Timer object to use
	def setTimer(self, timer):
		self._timer = timer
		if(not self._timerRunning):
			thread.start_new_thread(self._timerLogic,())
			self._timerRunning = True

	#timerStop: Stops the timer running in the background
	def timerStop(self):
		self._timerAbort = True

	#_timerLogic: Runs the logic to determine whether a player's turn has run out
	def _timerLogic(self):
		while True:
			if(self._timerAbort):
				self._timerRunning = False
				thread.exit()
			self._timer.tick()
			if(self._timer.timeUp()):
				break
			time.sleep(0.5)
		self._gameOverStub()
		self._timerRunning = False
		thread.exit()
