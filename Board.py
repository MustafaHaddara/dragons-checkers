import math

from BoardException import *

class Board:


	'''
	The board is stored as an array of 8 integers.
	Each index represents a row. One row can have a maximum of 4 squares in use and of only one colour, 
	so there is no point storing 4 potential piece locations if they can never be accessed. 
	Each index has 4 numbers. Each nibble represents a piece or in hexidecimal, each digit.
	Within a nibble, each spot can be broken down as
	[Reserved bit, King bit, Player bit, Enabled bit],
	where Reserved bit is set to 0
	The piece is a king if the bit is 1
	The player in human-readable terms is the bit + 1 
	And the piece is only enabled if enabled bit is 1
	'''

	#Constructor: Sets up the initial state of the board
	#Throws BoardException from setPositions
	def __init__(self):
		self.setPositions()
		
	#setPositions: Sets the pieces on the board in mass
	#newBoard: What should be on the new board and where
	#Raises BoardException if the board is of incorrect size or has too many pieces
	def setPositions(self, newBoard = [
		0x3333,
		0x3333,
		0x3333,
		0x0000,
		0x0000,
		0x1111,
		0x1111,
		0x1111]):
		if(len(newBoard) != 8):
			raise BoardException("The board is of invalid size. Expected 8, got " + str(len(newBoard)))

		self._board = newBoard[:]#Copy the array, not ref it
		self._jumpList = [[],[]]#[valid red jumps, valid black jumps]
		self._moveList = [[],[]]#[valid red jumps, valid black jumps]

		#Count the pieces on the board to check if either side has more than 12 pieces.
		#[Player 1, Player 2]
		self._numPieces = [0,0]
		for i in range(len(self._board)):
			for j in boardIterator(i):
				if(self.isPiece(i,j)):
					self._numPieces[self.getPlayer(i,j)] += 1
				if((j == 0 and not self.isKing(i,j) and self.getPlayer(i,j) == 0) or (j == 7 and not self.isKing(i,j) and self.getPlayer(i,j) == 1)):
					raise BoardException("Attempted to set a normal piece where a king should be. Aborting board setup.")
				if(self._numPieces[0] > 12 or self._numPieces[1] > 12):
					break

		if(self._numPieces[0] > 12 or self._numPieces[1] > 12):
			raise BoardException("The board has too many pieces. Expected a maximum of 12 per side. Got " + self._numPieces[0] + " and " + self._numPieces[1] + ".")

		#Set the initial jump list
		self.updateJumpList()
	
	#updateJumpList: Updates the internal list of pieces that can jump other pieces, and any pieces that can be moved.
	#FIXME: Find a quicker way of doing this				
	def updateJumpList(self):
		self._jumpList = [[],[]]
		self._moveList = [[],[]]
		#Iterate through again looking for jumps
		for i in range(len(self._board)):
			for j in boardIterator(i):
				if(self.isPiece(i,j)):
					player = self.getPlayer(i,j)
					multiplier = abs(player-1)
					if(self.isKing(i,j)):
						yRange = [j-1,j+1]
					else:
						yRange = [j+(-2)*multiplier+1]

					#Found a piece, check if it matches jump conditions
					for k in [i-1,i+1]:
						for l in yRange:
							if(self.isPiece(k, l) and (k != 0 and k != 7) and (l != 0 and l!= 7)):
								if(self.getPlayer(k, l) == (not player)):
									if(not self.isPiece(k + k - i, l + l - j) and (i,j) not in self._jumpList[player]):
										self._jumpList[player].append((i,j))
							elif(not self.isPiece(k,l) and not (k < 0 or k > 7) and not (l < 0 or l > 7) and (i,j) not in self._moveList[player]):
								self._moveList[player].append((i,j))
		if self._jumpList[0] != []:
			self._moveList[0] = self._jumpList[0]
		if self._jumpList[1] != []:
			self._moveList[1] = self._jumpList[1]

	#getJumpablePiece: Returns the list of pieces that have a jump move available
	#player: The player's jump list to retrieve
	#Returns: The selected players jump list
	def getJumpablePieces(self,player):
		return self._jumpList[player]

	#getMovablePiece: Returns the list of pieces that have a move available
	#player: The player's move list to retrieve
	#Returns: The selected players move list
	def getMovablePieces(self,player):
		return self._moveList[player]

	#isNoMovesAvailable: Returns if there are no moves a player can make
	#player: player - 1 for the player to check for.
	#Returns: True if player can make no moves.
	def isNoMovesAvailable(self, player):
		return self._moveList[player] == []

	#isSelectablePiece: Returns whether the piece selected is a valid piece to be moved
	#x: The x coordinate of the piece; y: The y coordinate of the pieces
	#Returns: True if the piece is a valid selectable piece
	def isSelectablePiece(self, x, y):
		#If it isn't a piece
		if(not self.isPiece(x,y)):
			return False

		#Any piece is selectable
		if(len(self._jumpList[self.getPlayer(x,y)]) == 0):
			return True

		return self._isForcableJumpPiece(x,y)#First call is redudant, but needs to proceed an empty list

	#isForcableJumpPiece: Returns whether a piece is in the jumpList
	#x: The x coordinate of the piece; y: The y coordinate of the piece
	#Returns: True if the piece is in the jump list
	def _isForcableJumpPiece(self, x, y):
		if(not self.isPiece(x,y)):
			return False

		player = self.getPlayer(x,y)
		listLen = len(self._jumpList[player])

		for i in range(listLen):
			if (self._jumpList[player][i] == (x,y)):
				return True
		return False

	#clearPieces: Clears all pieces from the board
	#Throws BoardException from setPositions
	def clearPieces(self):
		self.setPositions([0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0])

	#getRawBoard: Get's the raw board array
	#Returns: The raw board array
	def getRawBoard(self):
		return self._board

	#_getBitShift: Gets the amount to bitsdhift for a given row to get the piece at the position
	#x: The x coordinate; y: The y coordinate
	#Returns: The amount to bitshift by
	def _getBitShift(self, x, y):
		return max((7 - (y%2) - x)*2, 0)

	#isValidPosition: Checks whether a piece is on a valid square
	#x: The x coordinate of the piece; y: The y coordinate of the piece
	#Returns if the square is valid to hold a piece.
	def isValidPosition(self, x,y):
		if((x+y)%2 == 0 or x > 7 or y > 7 or x < 0 or y < 0):
			return False
		return True

	#getNumPieces: Returns a 2 element array of how many pieces each player has on the board
	#Returns: A 2-element array of how many pices each player has
	def getNumPieces(self):
		return self._numPieces;


	#isPiece: States whether a piece exists at location x,y
	#x: The x coordinate of the square to check; y: The y coordinate to check
	#Returns: if there is a piece on that square
	def isPiece(self, x, y):
		if(not self.isValidPosition(x,y)):
			return False
		bitShift = self._getBitShift(x,y)
		return  ((self._board[y]  & (0x1 <<  bitShift) ) >> bitShift) == 1

	#getPlayer: Returns which player a piece belongs to
	#x: The x coordinate of the square; y: The y coordinate of the square
	#Returns: The player (Player 1, Player 2), but subtracting 1, returns < 0 if there is no piece
	def getPlayer(self, x, y):
		if(not self.isPiece(x,y)):
			return -1
		bitShift = self._getBitShift(x,y)
		return  ((self._board[y]  & (0x2 <<  bitShift) ) >> (bitShift + 0x1)) 

	#isKing: Returns whether the piece in a square is a king
	#x: The x coordinate of the square; y: The y coordinate of the square
	#Returns: Whether the piece is a king or not
	def isKing(self, x, y):
		if(not self.isPiece(x,y)):
			return False
		bitShift = self._getBitShift(x,y)
		return  ((self._board[y]  & (0x4 <<  bitShift) ) >> (bitShift + 0x2)) == 1


	#deletePiece: Deletes a piece from the board
	#x: The x coordinate of the square; y: The y coordinate of the square
	#Returns True if the piece was successfully deleted otherwise returns False
	def deletePiece(self, x, y):
		if(not self.isPiece(x,y)):
			return False
		self._numPieces[self.getPlayer(x,y)] -= 1
		bitShift = self._getBitShift(x,y)
		self._board[y] ^= ((0x0*0x8 | self.isKing(x,y)*0x4 | self.getPlayer(x,y)*0x2 | self.isPiece(x,y)*0x1)  << bitShift)
		return True
		

	#addPiece: Adds a piece to the board
	#x: The x coordinate of the square; y: The y coordinate of the square; player: which player the new piece belongs to; king: if the new piece is a king
	#Returns True if the piece was added and false if it could not be added.
	def addPiece(self, x, y, player, king):
		if(self._numPieces[player] >= 12):
			raise BoardException("Player " + str(player+1) + " has too many pieces!")
		if(not self.isValidPosition(x,y)):
			return False#May be a simple misclick so an error here would be annoying
		if(self.isPiece(x,y)):
			raise BoardException("Piece already exists on that square. To delete it, right-click first.")
		#Can't add a non king to the opposing side
		if((y == 7 and player == 1 and not king) or (y == 0 and player == 0 and not king)):
			raise BoardException("You can't place a regular piece on the opposing edge without it being a king.")
		bitShift = self._getBitShift(x,y)
		self._board[y] |= ((0x01 | player*0x02 | king*0x04) <<  bitShift)
		self._numPieces[self.getPlayer(x,y)] += 1
		return True

	#movePiece: Moves a piece from one position to another 
	#oldx: The x coordinate of the piece you are moving; oldy: The y coordinate of the piece you are moving; 
	#newx: The location where the piece is moving; newy: The location where the piece is moving
	#Returns: -1 on invalid move, 0 is successful and terminated move, 1 was a jumped that can be "chained" with another jump
	def movePiece(self, oldx, oldy, newx, newy):
		#Basic information about the piece
		returnValue = 1
		player = self.getPlayer(oldx,oldy)
		king = self.isKing(oldx,oldy)
		kingTrap = False
		jumpTrap = False

		#Not 1 or 2 diagonal moves
		if(abs(newx-oldx) != abs(newy-oldy) or not (abs(newx-oldx) != 1 ^ abs(newx-oldx) != 2)):
			return -1

		#IF they're trying to jump and it isn't a forcable jump
		if(self._isForcableJumpPiece(oldx,oldy) and abs(newx-oldx) != 2):
			return -1

		#IF it's not a king, reduce the search area of checking the valid move
		if(not king):
			if(newy != oldy - int(math.pow(-1, player))*1 and newy != oldy - int(math.pow(-1, player))*2):
				return -1
			if((newy-oldy == -int(math.pow(-1, player))*2) and self.getPlayer(oldx + (newx-oldx)/2, oldy - int(math.pow(-1, player))*1) != (not player)):
					return -1
		#If it's a king, it can move either way
		else:
			if((abs(newy-oldy) == 2) and self.getPlayer(oldx + (newx-oldx)/2, oldy + (newy-oldy)/2) != (not player)):
					return -1

		#Move the piece
		returnValue = returnValue and self.deletePiece(oldx,oldy)
		if((newy == 7 and player == 1 or newy == 0 and player == 0) and not king):
			king = 1
			kingTrap = True
		returnValue = returnValue and self.addPiece(newx,newy, player,king)
		#Someone was jumped
		if(abs(newx-oldx) == 2):
			self.deletePiece(oldx + (newx-oldx)/2,oldy + (newy-oldy)/2)
			self.updateJumpList()
			#Check if the piece is in the list again
			if(self._isForcableJumpPiece(newx,newy)):
				jumpTrap = True

		#Since True and False are just 1 and 0 respectively, it's fine to return the boolean value here without explicit casting
		if(kingTrap or jumpTrap):
			return (not kingTrap and jumpTrap)
		return -abs(not returnValue)
#boardIterator: Returns a list of valid y coordinates to use for a given row
#Returns: a list of valid y-coordinates to use for a given row
def boardIterator(x):
	return range((x%2 == 0), 8, 2)
