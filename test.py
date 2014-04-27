from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import serial
from serial import SerialException
import threading
import time
import random


runstate = True
newInfo = False
playerList = []

class Player:
	
	

	def __init__(self, _id):
		self.id = _id
		self.score = 0

class qtUpdaterThread(QThread):
	trigger = pyqtSignal(int)

	def __init__(self, parent=None):
		super(qtUpdaterThread, self).__init__(parent)

	def run(self):
		global newInfo 
		global runstate 

		while(runstate):
			if(newInfo):
				print("EMIT!")
				newInfo = False
				self.trigger.emit(True)
				
			



class Form(QWidget):
	items = []
	def __init__(self, parent=None):
		super(Form, self).__init__(parent)

		""" THREADING """

		thread = qtUpdaterThread(self)
		thread.trigger.connect(self.updateGUI)
		thread.start()


		""" LAYOUT """

		nameLabel = QLabel("Name:")
		#self.nameLine = QLineEdit()
		self.test = QPushButton("Test")
		self.qlist = QListWidget()
		self.startBtn = QPushButton("Start Game")

		buttonLayout1 = QVBoxLayout()
		buttonLayout1.addWidget(nameLabel)
		buttonLayout1.addWidget(self.test)
		
		

		buttonLayout1.addWidget(self.startBtn)
		self.startBtn.clicked.connect(self.startGame)


		buttonLayout1.addWidget(self.qlist)
		
		
		"""for i in [1,2,4,1,7,3]:
			item = QListWidgetItem(self.qlist)
			icon = QIcon('ok.png')
			#icon = QIcon('D:\python-dev\ok.png')
			item.setText('Group #' + str(i))
			item.setIcon(icon)"""
		
		self.test.clicked.connect(self.submitContact)

		mainLayout = QGridLayout()
		#mainLayout.addWidget(nameLabel, 0, 0)
		mainLayout.addLayout(buttonLayout1, 0, 1)

		self.setLayout(mainLayout)
		self.setWindowTitle("Clients")

	def submitContact(self):

		global playerList	
		global newInfo	
		"""x = self.qlist.findItems('Group #7',Qt.MatchExactly)
		for item in x:
			self.qlist.takeItem(self.qlist.indexFromItem(item).row())
		name = self.nameLine.text()

		if name == "":
			QMessageBox.information(self, "Empty Field","Please enter a name and address.")
			return
		else:
			QMessageBox.information(self, "Success!","Hello \"%s\"!" % name)"""

		
		playerList.append(Player(2))

		#Lets make our GUI update
		newInfo = True	

	def startGame(self):
		self.q = QuestionForm()
		self.q.resize(800, 600)
		self.q.show()

	def updateGUI(self,signal):
		global playerList
		if(signal):
			# UPDATE!! 
			#Check which items are not in the items, but in playerlist
			#print("Items: " + str(len(self.items)))
			pl = [x.id for x in playerList]
			#print("PL "  + str(len(pl)))
			#print("ID:")
			#print(playerList[0].id)

			diff = list(set(pl).difference(self.items))

			#print(str(len(diff)))

			for x in diff:
				
				#None found, add! 
				item = QListWidgetItem(self.qlist)
				icon = QIcon('ok.png')
				#icon = QIcon('D:\python-dev\ok.png')
				item.setText('Group #' + str(x))
				item.setIcon(icon)	
				self.items.append(x)



class QuestionForm(QWidget):
	items = []
	def __init__(self, parent=None):
		super(QuestionForm, self).__init__(parent)

		""" THREADING """



		""" LAYOUT """

		
		self.qlist = QListWidget()

		buttonLayout1 = QVBoxLayout()
		
		
		buttonLayout1.addWidget(self.qlist)
		
		
		"""for i in [1,2,4,1,7,3]:
			item = QListWidgetItem(self.qlist)
			icon = QIcon('ok.png')
			#icon = QIcon('D:\python-dev\ok.png')
			item.setText('Group #' + str(i))
			item.setIcon(icon)"""

		answers = QGridLayout()
		f = QFont('Helvetica', 16)
	
		ans = []

		ans1 =  QLabel("[A]")
		ans2 =  QLabel("[B]")
		ans3 =  QLabel("[C]")
		ans4 =  QLabel("[D]")

		ans.append(ans1)
		ans.append(ans2)
		ans.append(ans3)
		ans.append(ans4)

		for x in ans:
			x.setFont(f)

		answers.addWidget(ans1, 0, 0)
		answers.addWidget(ans2, 0, 1)
		answers.addWidget(ans3, 1, 0)
		answers.addWidget(ans4, 1, 1)
		

		mainLayout = QGridLayout()
		titleLabel = QLabel("Question 1:")
		font = QFont('Helvetica', 42)
		titleLabel.setFont(font)

		#Nav buttons
		navLayout = QHBoxLayout()	
		self.next = QPushButton("Next")
		self.prev = QPushButton("Prev")
		navLayout.addWidget(self.prev)
		navLayout.addWidget(self.next)


		mainLayout.addWidget(titleLabel, 0, 0)
		mainLayout.addLayout(answers, 1, 0)
		mainLayout.addLayout(buttonLayout1, 2, 0)
		mainLayout.addLayout(navLayout, 3, 0)

		self.setLayout(mainLayout)
		self.setWindowTitle("Question")









class serialThread(threading.Thread):
	def __init__(self, threadID,COMport):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.COMport = COMport
		pass


	def run(self):
		global newInfo
		global runstate

		test = True

		#This what actually happens
		try: 
			ser = serial.Serial()
			#ser.timeout(10) #should we have this?
			ser.baudrate = 115200
			ser.port = self.COMport
			ser.open()
		except SerialException:
					#If no initial connection can be made..

					#Might want to change to a reconnect mode
					print ("Unable to open inital comm")	
					return -1
					#Lets use dummy data. Comment the return above out.

					
		print("Com status: ")	
		ser.isOpen()



		while(runstate):
			# Read from the comport
			if(ser.isOpen):
			#if(1!=1):
				#Port open, lets read

				currLine = ser.readline()
				currLine = currLine.decode("utf-8")
				print(currLine)

				s = currLine.split(',')

				#Determine type
				type = s[0]
				

				if(type == 'a'): 
				#answer
					qID = int(s[1])
					#Join request or actual answer

					answer = int(s[2])
					#print("Got ans: " + str(answer))

					if(qID == 0):
						#Join request

						"""
						1) Check is player ID exsits
						2) add it"""

						if (answer not in [p.id for p in playerList]):
							# Add it
							print("Adding player")
							p = Player(answer)
							playerList.append(p)

							#Lets make our GUI update
							newInfo = True

					else:
						# handle answer
						pass

				else:
					#Something went wrong 
					pass




			else:
				#Port not open, handle this
				print("Com was closed, trying to reopen")
				try:
					ser = serial.Serial(self.COMport)
				except SerialException:
					print ("Unable to open")
				# something went wrong?
				"""if(test):
					p = Player(2)
					playerList.append(Player(p))
					print ("sooo:")
					print (playerList[0].id)

					#Lets make our GUI update
					newInfo = True	
					test = False"""

		# Runstate changed. Close stuff and return

		ser.close()

		return
			
			

			
			
if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	#Spin up threads


	#List ports python -m serial.tools.list_ports
	# the COM parameter on Windows:
		# To open COMn set COMport to n-1. Eg COM 24 = 23
	sthread = serialThread(1,17)

	

	sthread.start()

	screen = Form()
	screen.resize(400, 600)
	screen.show()
	try:
		app.exec_() #blocks until the window is closed.
	except KeyboardInterrupt:
		sys.exit()

	runstate = False

	""" Spin down threads """
	try:
		sthread.join(2)
	except KeyboardInterrupt:
			sys.exit()


	print("All OK - good night")

	sys.exit()
