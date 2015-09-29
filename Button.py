import pygame
import math
import sys
#Error message handler
import Tkinter
import tkMessageBox

class Button:
	#buttonTypes
	TYPE_RECT = 0
	TYPE_CIRCLE = 1

	
	#The various kinds of buttons
	_kinds = ["startButton", "loadButton",
			"redButtonNormal", "blackButtonNormal",
			"backArrow", "quitButton", 
			"saveButton", "ToggleAIOnButton", 
			"concedeButton"]

	#Try to load all the button images to memory
	try:
		_button_images = [pygame.image.load("Graphics/"+_kinds[i]+".png")for i in range(len(_kinds))]
	except:
		Tkinter.Tk().wm_withdraw()
		tkMessageBox.showinfo("Uh oh!", "Images not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
		#Exit to stop a further exception
		sys.exit()

	#Constructor: Creates the button
	#X: the x coordinate of the button, Y: the y coordinate of the button, kind: The kind of the button, function: The function to be run when the button is pressed,
	#[OPTIONAL]buttonType: The type of the button which reflects the bounds in which a click is recognized.
	def __init__(self, X, Y, kind, function, buttontype = TYPE_RECT):
		## Initialization with a position (X, Y) and a type of button
		## The kind of button is given by a string that is in the list defined above in sprites
		## but not including the png extension

		self._function = function
		self._kind = kind
		self._buttontype = buttontype
		self._image = Button._button_images[Button._kinds.index(kind)]  ## Look up index of the kind of the button
		## Find the button in the list of images
		self._X = X 
		self._Y = Y
		self._width = self._image.get_width()
		self._height = self._image.get_height()
		self._speedX = 0
		self._speedY = 0
		self._delete = False ## Used for garbage collection
		self._overlay = None

	#draw: Draws the button to the window
	#win: The window to draw to
	def draw(self, win):
		## Draws the button to the window given
		win.blit(self._image, (self._X, self._Y))
		if not (self._overlay == None):
			win.blit(self._overlay, (self._X, self._Y))

	#move: Moves the button on the screen
	def move(self):
		## Moves the button
		self._X += self._speedX
		self._Y += self._speedY
		
		if self._X > 640 or self._X < -160 or self._Y > 720 or self._Y < -160:
			## If outside the window
			self._delete = True

	#setOverlay: Sets the overlay of a button
	#image: The image to overlay
	def setOverlay(self, image):
		if not (image == None):
			try:
				self._overlay = pygame.image.load("Graphics/"+image+".png")
			except:
				Tkinter.Tk().wm_withdraw()
				tkMessageBox.showinfo("Uh oh!", "Images not found! The game can't continue with some resources missing. You should redownload it from the original source and see if that helps.")
				#Exit to stop a further exception
				sys.exit()
		else:
			self._overlay = None

	#isClicked: Determines whether this button was clicked
	#x_pos: The x coordinate the click occurred, y_pos: The y coordinate the position occurred
	#Returns a tuple of whether the button was clicked and the kind of button it was if it was clicked
	def isClicked(self, x_pos, y_pos):
		## Returns true if the coordinate (x_pos, y_pos) is within the button
		## i.e. if the button is clicked. 
		if self._buttontype == Button.TYPE_CIRCLE:
			center = [self._X+self._width/2, self._Y+self._height/2]
			if math.sqrt((x_pos - center[0])**2 + (y_pos - center[1])**2) <= self._width/2:
				return (True, self._kind)
		else:
			if self._X <= x_pos <= self._X + self._width and self._Y <= y_pos <= self._Y + self._height:
				return (True, self._kind)
		return (False, "none")

	#getKind: Gets the kind of the button
	#Returns: The kind of the button
	def getKind(self):
		return self._kind

	#function: returns the function bound to the button
	#Returns: The function bound to the button
	def function(self):
		return self._function

	
					 
