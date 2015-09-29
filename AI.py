from random import *
from Board import *
from BoardException import *
import thread
import time
class AI:

	#Constructor: Sets up the initial state of the AI
	#board: A copy of the board in use
	def __init__(self, board):
		self.AIBoard = board#A copy of the board
		seed()#Seeds the RNG
		self._concedeThreshold = 40#If the AI doesn't make a jump in 40 moves, it concedes
		self._sinceLastJump = 0
		self._boardLock = None#Board lock to prevent a race condition

	#runAI: The AI's "body". Chooses a move from the current board
	#callback: The function to be run when it is done its turn; 
	#concedeCallback: The function to be run if the AI decides to concede;
	#selectedPieceCallback: The function to run when the AI has selected a piece to move
	def runAI(self, callback,concedeCallback,selectedPieceCallback):
		#Concede if we haven't jumped anything in 40 turns
		if(self._sinceLastJump >= self._concedeThreshold):
			concedeCallback()
			thread.exit()
		jumpPiece = True
		moveList = self.AIBoard.getJumpablePieces(1)
		#If there are no forced jump moves, get all available moves
		if moveList == []:
			moveList = self.AIBoard.getMovablePieces(1)
			jumpPiece = False
		time.sleep(uniform(0.2,0.4))
		#Pick a piece
		movingPiece = moveList[randint(0, len(moveList)-1)]
		while True:
			#Show the selected piece
			selectedPieceCallback(movingPiece[0],movingPiece[1])
			#Choose the new2 location
			newPosition = self._chooseMove(movingPiece, jumpPiece)
			#Get the boardLock and move the piece
			if(self._boardLock != None):
				self._boardLock.acquire()
			moveStatus = self.AIBoard.movePiece(movingPiece[0],movingPiece[1],newPosition[0],newPosition[1])
			if(self._boardLock != None):
				self._boardLock.release()
			#If the move hasn't terminated, go again.
			if(moveStatus == 0):
				break
			if(moveStatus == 1):
				movingPiece = newPosition
				self._sinceLastJump = 0
			if(moveStatus == -1):
				BoardException("The AI made an invalid move! Aborting turn.")
				break
		self._sinceLastJump = self._sinceLastJump + 1
		callback()
		thread.exit()

	#setBoardLockObj: Sets the _boardLock to avoid a race condition with board.
	def setBoardLockObj(self, lock):
		self._boardLock = lock

	#getTurnNumber: Returns the number of turns since last jump
	#Returns: The number of turns since th last jump
	def getTurnNumber(self):
		return self._sinceLastJump

	#setTurnNumber: Sets the number of turns since the AI last jumped a piece
	#turns: The number of turns
	def setTurnNumber(self, turns):
		self._sinceLastJump = turns

	#_chooseMove: Chooses the new position for a given piece
	#movingPiece: The piece bing moved; jumpPiece: If the current piece is in a forced jump situation
	#Returns: The location of where the piece should be placed.
	def _chooseMove(self, movingPiece, jumpPiece):
		xRange = []
		if(movingPiece[0] > jumpPiece):
			xRange.append(movingPiece[0] - 1 - jumpPiece)
		if(movingPiece[0] < 7 - jumpPiece):
			xRange.append(movingPiece[0] + 1 + jumpPiece)

		yRange = []
		player = self.AIBoard.getPlayer(movingPiece[0], movingPiece[1])
		if(self.AIBoard.isKing(movingPiece[0],movingPiece[1])):
			if(movingPiece[1] > jumpPiece):
				yRange.append(movingPiece[1]-1-jumpPiece)
				#Weighted kings to "go home"
				if(player):
					yRange.append(movingPiece[1]-1-jumpPiece)
			if(movingPiece[1] < 7 - jumpPiece):
				yRange.append(movingPiece[1]+1+jumpPiece)
				#Weighted kings to "go home"
				if(player):
					yRange.append(movingPiece[1]+1+jumpPiece)
		else:
			#Should always be available, if it's not a king and it can move
			yRange.append(movingPiece[1]+((-1)**(player+1))*(1+jumpPiece))

		validMoves = []
		#Build valid moves
		for i in range(len(xRange)):
			for j in range(len(yRange)):
				if(jumpPiece):
					if(not self.AIBoard.isPiece(xRange[i],yRange[j]) and self.AIBoard.isPiece(movingPiece[0] + (xRange[i] - movingPiece[0])/2,movingPiece[1] + (yRange[j] - movingPiece[1])/2)  and self.AIBoard.getPlayer(movingPiece[0] + (xRange[i] - movingPiece[0])/2,movingPiece[1] + (yRange[j] - movingPiece[1])/2) == (not player)):
						# == (not self.AIBoard.getPlayer(movingPiece[0], movingPiece[1]))
						validMoves.append((xRange[i],yRange[j]))
				else:
					if(not self.AIBoard.isPiece(xRange[i], yRange[j])):
						validMoves.append((xRange[i],yRange[j]))

		newPosition = validMoves[randint(0,len(validMoves)-1)]
		time.sleep(uniform(0.7,2.0))
		return newPosition
