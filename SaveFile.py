## SaveFile.py
## Mustafa Haddara
## Tue Mar-18-2014

import hashlib
import struct
from BoardException import *

'''
File Format
Size	   | Description of content
0x04 bytes | CK02 , where CK is the "signature" for the file type and 02 is the version of save file (future revisions)
0x10 bytes | that hold the raw data for the board.
0x01 byte  | A byte that holds whos turn was last played and whether it was vs player or vs AI where the first five bits are reserved
		   | and the 6th is 0 if the first player controls red, 1 if the first player controls black
		   | and the 7th is 1 if the second player is human, 0 if AI and the eighth bit is whos turn as that bit + 1
0x01 byte  | Contains turn number
0x01 byte  | Contains the time remaining in the turn
0x20 bytes | An SHA256 hash of the previous content
'''

#saveFile: Saves the current game state to a file
#array: The array which holds the contents of the board; second_player: Whether the player is playing against a human or AI;
#turn: Who's turn it currently is; turn_number: The current number of turns played, currently unused.
def saveFile(array, first_player = 0, second_player = 0, turn = 0, turn_number = 1, time = 60):
	## array of board positions
	## first_player  = 0 if first player controls red
	##				 = 1 if first player controls black
	## second_player = 0 if playing against computer, 
	##				 = 1 if playing against human
	## turn = 0 if first player's turn, 
	##		= 1 if second player's turn

	outFile = open("save.chck", "wb")
	data = "CK02"

	## Writing data from the array into the data string
	for i in array:
		#data += str(i) + "i"
		data += struct.pack('H',i)
	data += struct.pack('B', (first_player << 2) | (second_player << 1) | turn)
	data += struct.pack('B', turn_number)
	data += struct.pack('B', time)
	data += hash(data[:]) 
	
	outFile.write(data)
	outFile.close()

#loadFile: Loads save.chck and sets the game to where the player left off
#Returns, the board configuration, whether the second player is human or not, and who's turn it is.
def loadFile():
	try:
		inFile = open("save.chck", "rb")
	except:
		raise BoardException("No save file found!")
	data = inFile.read()
	boardData = data[:-32]
	hashCheck = data[-32:]
	if hash(boardData) != hashCheck or data[0:2] != "CK":
		raise BoardException("Oi! Stop mucking with my save file!")
	if (data[2:4] != "01") and (data[2:4] != "02"):
		if int(data[2:4]) > 2: 
			raise BoardException("Unrecognized save file version. Please download version " + data[2:4] + " in order to load this game correctly.")
		else:
			raise BoardException("Unrecognized save file version. Unable to find appropriate version.")
	inFile.close()
	playerTurn = int(struct.unpack('B', boardData[20])[0]) & 0x1
	turn_number = 0
	#Some conditions for backward compatibility
	if data[2:4] == "01":
		first_player = 1
		time = 60
	elif data[2:4] == "02":
		first_player = int(struct.unpack('B', boardData[20])[0]) 
		turn_number = int(struct.unpack('B', boardData[21])[0])
		time = int(struct.unpack('B', boardData[22])[0])
	second_player = (first_player & 0x2) >> 1
	first_player = (first_player & 0x4) >> 2
	boardLayout = [];
	for i in range(4,19,2):
		boardLayout.append(int(struct.unpack('H', boardData[i:i+2])[0]))
	#Prevent "replays" of using older versions
	if data[2:4] == "01":
		saveFile(boardLayout, first_player, second_player, playerTurn, turn_number, time)
		boardLayout, first_player, second_player, playerTurn, turn_number,time = loadFile()
	return boardLayout, first_player, second_player, playerTurn, turn_number,time

#hash: Hashes a string
#Returns: The hash as a sequence of bits rather than it's string representation
def hash(string):
	secure = hashlib.sha256()
	secure.update(string)
	return secure.digest()
