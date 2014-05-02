"""
Gameserver written for course 41030 @ DTU.
Author: Nicholas Swiatecki, nicholas@swiatecki.com
Github: https://github.com/swiatecki/GameServer
License: Free for private/educational use. 
		Please leave a reference to the original code.
		Also, if you improve the code, share it with me :)
Tested on windows with python 3.3.5.
Hardware: Arudino Uno + NRF24l01
"""
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import serial
from serial import SerialException
import threading
import time
import random
import binascii


runstate = True
newInfo = False
playerList = []
started = False
Q = None;
sent = False
state =0


class Questions:


	questionList = []


	def __init__(self):
		self.curentQuestion = 1

		self.questionList.append({
			'Question': 'Which Animal is the heaviest?',
			'A': 'Monkey',
			'B': 'Elephant',
			'C': 'Slightly larger Goose',
			'D': 'Gese',
			})

		self.questionList.append({
			'Question': 'How many fingers do you have?',
			'A': '1',
			'B': '11',
			'C': '10',
			'D': '6',
			})

		self.questionList.append({
			'Question': 'How are you?',
			'A': 'bad',
			'B': 'terrible',
			'C': 'terrific',
			'D': 'good',
			})


		self.questionList.append({
			'Question': 'Who is the most awesome?',
			'A': 'design',
			'B': 'elektro',
			'C': 'design',
			'D': 'design',
			})


	

	def getQuestion(self):
		return self.questionList[self.curentQuestion-1]

	def nextQuestion(self):
		self.curentQuestion += 1

	def questionID(self):
		return self.curentQuestion



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
		global started
		global newInfo
		self.q = QuestionForm()
		self.q.resize(800, 600)
		self.q.show()
		started = True
		#print("Started is now" + str(started))
		newInfo = True

	def updateGUI(self,signal):
		global playerList
		global started
		if(signal):
			if started is False:
				# UPDATE!! 
				
				pl = [x.id for x in playerList]

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
			elif started is True:
				# Game started.
				
				self.q.titleLabel.setText(self.q.theQuestion['Question'])

				self.q.ans1.setText("A: " + self.q.theQuestion['A'])
				self.q.ans2.setText("B: " +self.q.theQuestion['B'])
				self.q.ans3.setText("C: " +self.q.theQuestion['C'])
				self.q.ans4.setText("D: " +self.q.theQuestion['D'])



class QuestionForm(QWidget):
	items = []
	def __init__(self, parent=None):
		super(QuestionForm, self).__init__(parent)
		global playerList
		""" THREADING """



		""" LAYOUT """
		f = QFont('Helvetica', 16)
		self.setFont(f)
		
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
	
		self.ans = []

		self.ans1 =  QLabel("[A]")
		self.ans2 =  QLabel("[B]")
		self.ans3 =  QLabel("[C]")
		self.ans4 =  QLabel("[D]")

		self.ans.append(self.ans1)
		self.ans.append(self.ans2)
		self.ans.append(self.ans3)
		self.ans.append(self.ans4)

		for x in self.ans:
			x.setFont(f)

		answers.addWidget(self.ans1, 0, 0)
		answers.addWidget(self.ans2, 0, 1)
		answers.addWidget(self.ans3, 1, 0)
		answers.addWidget(self.ans4, 1, 1)
		

		mainLayout = QGridLayout()
		self.titleLabel = QLabel("Question 1:")
		font = QFont('Helvetica', 42)
		self.titleLabel.setFont(font)


		#Status bar
		lblNumAns =  QLabel("Answers:")
		self.lblAns = QLabel("0")
		lblspacer =  QLabel("/")
		lblNumClients = QLabel()
		lblNumClients.setText(str(len(playerList)))
		
		statusLayout = QHBoxLayout()
		statusLayout.addWidget(lblNumAns)
		statusLayout.addWidget(self.lblAns)
		statusLayout.addWidget(lblspacer)
		statusLayout.addWidget(lblNumClients)



		#Nav buttons
		navLayout = QHBoxLayout()	
		self.next = QPushButton("Next")
		self.prev = QPushButton("Prev")
		navLayout.addWidget(self.prev)
		navLayout.addWidget(self.next)


		mainLayout.addWidget(self.titleLabel, 0, 0)
		mainLayout.addLayout(answers, 1, 0)
		mainLayout.addLayout(buttonLayout1, 2, 0)
		mainLayout.addLayout(navLayout, 3, 0)
		mainLayout.addLayout(statusLayout, 4, 0)

		self.setLayout(mainLayout)
		self.setWindowTitle("Question")



		self.next.clicked.connect(self.nextHandler)
		
		
		self.theQuestion = Q.getQuestion()



	def setText(self):
		pass

	def nextHandler(self):
		global newInfo
		global sent
		#global state

		Q.nextQuestion()
		self.theQuestion = Q.getQuestion()
		sent = False
		#state = 0

		newInfo = True







class serialThread(threading.Thread):
	def __init__(self, threadID,COMport):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.COMport = COMport
		pass


	def run(self):
		global newInfo
		global runstate
		global started
		global sent
		global state 

		test = True
		state = 0
		#This what actually happens
		try: 
			ser = serial.Serial()
			#ser.timeout(10) #should we have this?
			ser.baudrate = 115200
			ser.port = self.COMport
			ser.timeout = 0.5
			ser.open()
		except SerialException:
					#If no initial connection can be made..

					#Might want to change to a reconnect mode
					print ("Unable to open inital comm")	
					return -1
					#Lets use dummy data. Comment the return above out.

					
		print("Com status: ")	
		ser.isOpen()


		#ser.flushInput();
		#ser.flushOutput();

		""" The pySerial.write takes a byte String, but in python 3,
		strings are unicode per dafult. """
		#outString = b"s0" # Serial
		time.sleep(1)
		
		ser.write(str.encode("s0"))

		sent = False

		while(runstate):
			# Read from the comport
			if(ser.isOpen):
			#if(1!=1):
				#Port open, lets read

				currLine = ser.readline()

				hexl = binascii.hexlify(currLine);
				rawline = currLine
				#print(b"HEX:" + rawline)
				currLine = currLine.decode("utf-8",errors='ignore')
				#print(currLine)

				# We prefix out commands with //, if the line does not start with // its debug info
				print("SERIAL:" + currLine)
				if(currLine[:2] != '//'):
					#Printing debug info
					# print serial here
					#if currLine is None:
					
					if(rawline == b"STATE IS NOW:1.\r\n"):
						print("STATE CHANGE!")
						state =1
				else:
					#Its data! -> 
					#Strip of the // 
					currLine = currLine[2:]
					s = currLine.split(',')

					#Determine type
					type = s[0]
					

					if(type == 'a'): 
					#answer
						qID = int(s[1])
						#Join request or actual answer

						tID = int(s[2])

						answer = int(s[3])
						#print("Got ans: " + str(answer))

						if(qID == 0):
							#Join request
							print("GS: Got join request for team" + str(tID))
							"""
							1) Check is player ID exsits
							2) add it"""

							if (tID not in [p.id for p in playerList]):
								# Add it
								print("Adding player")
								p = Player(tID)
								playerList.append(p)

								#Lets make our GUI update
								newInfo = True

						else:
							print("GS: Got ans for team" + str(tID) + " on Q=" + str(qID) + " with ans = " + str(answer))

							

					else:
						#Something went wrong 
						pass

				# We have read, now - lets see if there is something to send

				""" SEND PART"""
				if(started):
					# Set state on arduino!
					if(state == 0):
						ser.write(str.encode("s1"))
					#print("STARTED!")
					
					#ser.flushOutput()

					if(sent == False and state ==1):
						print("GS: Sending")
					
						tmp = Q.getQuestion()

						
						tmp['A'] = tmp['A'].ljust(6)
						tmp['B'] = tmp['B'].ljust(6)
						tmp['C'] = tmp['C'].ljust(6)
						tmp['D'] = tmp['D'].ljust(6)



						outString = "q" + str(Q.questionID()) + \
						tmp['A'][:6]  + tmp['B'][:6]  \
						+ tmp['C'][:6] + tmp['D'][:6]

						
						print("Gonna write:")
						print(str.encode(outString) + b'\0')
						ser.write(str.encode(outString)+b'\0');
						sent = True





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
		print("Closing Serial")
		ser.close()
		print("Serial Closed")
		return
			
			

			
			
if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	#Spin up threads

	Q = Questions()
	#List ports python -m serial.tools.list_ports
	# the COM parameter on Windows:
		# To open COMn set COMport to n-1. Eg COM 24 = 23
	sthread = serialThread(1,22)

	

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
	except:
			sys.exit()


	print("All OK - good night")

	sys.exit()
