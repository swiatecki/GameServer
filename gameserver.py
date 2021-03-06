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
F = None;
L = None;



class Questions:


	questionList = []
	currentAnswers = {} #team, ans - good for lokking up


	def __init__(self):
		self.curentQuestion = 1

		#1
		self.questionList.append({
			'Question': 'Who drinks the most coffee',
			'A': 'Ali',
			'B': 'Jakob',
			'C': 'Nicholas',
			'D': 'Dronning M.',
			'correctAnswer':'A'
			})
            
        #2
		self.questionList.append({
			'Question': 'Who smokes the most?',
			'A': 'Ali',
			'B': 'Jakob',
			'C': 'Nicholas',
			'D': 'Dronning M.',
			'correctAnswer':'D'
			})
            
    	#3
		self.questionList.append({
			'Question': 'What sqrt(625)?',
			'A': '20',
			'B': '25',
			'C': '50',
			'D': '75',
			'correctAnswer':'B'
			})

            
        #4
		self.questionList.append({
			'Question': 'Would you rather fight 1 horse-sized duck \n or 100 duck-sized horses?',
			'A': '1 h.s.d',
			'B': '100 d.s.h',
			'C': '-',
			'D': '-',
			'correctAnswer':'B'
			})
            
        #5 - img
		self.questionList.append({
			'Question': 'Who is heavier?',
			'A': 'Per Boelskifte',
			'B': 'Ali',
			'C': 'Yutaka',
			'D': 'Master Fatman',
			'correctAnswer':'D'
			})
            
        #6
		self.questionList.append({
			'Question': 'What is the course no for mekatronik?',
			'A': '41030',
			'B': '41031',
			'C': '42030',
			'D': '42031',
			'correctAnswer':'A'
			})

	

	def getQuestion(self):
		return self.questionList[self.curentQuestion-1]

	def nextQuestion(self):
		#Before we proceed, check answers and add points 

		for teamID, answer in self.currentAnswers.items():

			# Get the current question, and retrieve the answer.
			if(answer == self.getQuestion()['correctAnswer']):

				#We got a correct answer, find the player in playerList. who has the correct ID
				# Could try the python style matches = (x for x in lst if x > 6), which returns a list of items which meet the requirements

				for p in playerList:
					if(p.id == teamID):
						# It's the one! Add points
						out = "GS: Adding point to team" + str(teamID) + " for the answer:" + answer
						print(out)
						L.addLog(out)
						p.addPoint()
						out = "GS: Score for "+  str(teamID) + " is now:" + str(p.getScore())
						L.addLog(out)
						print(out)





		#Then empty out answers 
		#Maybe write to file before emptying?

		self.currentAnswers.clear()


		#OK, on to the next question


		self.curentQuestion += 1

	def questionID(self):
		return self.curentQuestion
	def getAnswers(self):
		return self.currentAnswers

	def addAnswer(self,teamID,answer):
		self.currentAnswers[teamID] = answer 



class Player:
	
	

	def __init__(self, _id):
		self.id = _id
		self.score = 0

	def addPoint(self):
		self.score += 1

	def getScore(self):
		return self.score



class qtUpdaterThread(QThread):
	trigger = pyqtSignal(int)

	def __init__(self, parent=None):
		super(qtUpdaterThread, self).__init__(parent)

	def run(self):
		global newInfo 
		global runstate 

		while(runstate):
			if(newInfo):
				#print("EMIT!")
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
				
				self.q.titleLabel.setText(str(Q.questionID()) +": " + self.q.theQuestion['Question'])

				self.q.ans1.setText("A: " + self.q.theQuestion['A'])
				self.q.ans2.setText("B: " +self.q.theQuestion['B'])
				self.q.ans3.setText("C: " +self.q.theQuestion['C'])
				self.q.ans4.setText("D: " +self.q.theQuestion['D'])
				self.q.lblAns.setText(str(len(Q.getAnswers())))

				self.q.updateAnsList()



class QuestionForm(QWidget):
	items = []
	def __init__(self, parent=None):
		super(QuestionForm, self).__init__(parent)
		global playerList
		""" THREADING """



		""" LAYOUT """
		f = QFont('Helvetica', 16)
		self.setFont(f)
		
		self.ansList = QListWidget()
		self.ansList.setFont(f)

		##buttonLayout1 = QVBoxLayout()
		
		
		##buttonLayout1.addWidget(self.qlist)
		
		
		"""for i in [1,2,4,1,7,3]:
			item = QListWidgetItem(self.qlist)
			icon = QIcon('ok.png')
			#icon = QIcon('D:\python-dev\ok.png')
			item.setText('Group #' + str(i))
			item.setIcon(icon)"""

		answers = QGridLayout()
		f = QFont('Helvetica', 20)
	
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



		finalLayout = QHBoxLayout()
		self.finalBtn = QPushButton("Finish Game")
		finalLayout.addWidget(self.finalBtn)


		self.finalBtn.clicked.connect(self.finalHandler)
		

		mainLayout.addWidget(self.titleLabel, 0, 0)
		mainLayout.addLayout(answers, 1, 0)
		mainLayout.addWidget(self.ansList, 2, 0)
		mainLayout.addLayout(navLayout, 3, 0)
		mainLayout.addLayout(statusLayout, 4, 0)
		mainLayout.addLayout(finalLayout, 5, 0)

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
		self.ansList.clear()
		Q.nextQuestion()
		self.theQuestion = Q.getQuestion()
		sent = False
		#state = 0

		newInfo = True

	def finalHandler(self):
		global F
		global playerList
		
		for teamID, answer in Q.currentAnswers.items():

			# Get the current question, and retrieve the answer.
			if(answer == Q.getQuestion()['correctAnswer']):

				#We got a correct answer, find the player in playerList. who has the correct ID
				# Could try the python style matches = (x for x in lst if x > 6), which returns a list of items which meet the requirements

				for p in playerList:
					if(p.id == teamID):
						# It's the one! Add points
						print("GS: Adding point to team" + str(teamID) + " for the answer:" + answer)
						p.addPoint()
						print("GS: Score is now:" + str(p.getScore()))


		##
		
		#Game has ended, show score frame!

		self.close()
		F = FinalForm()

		F.show()




	def updateAnsList(self):
		#Check if there are more answers than thoose displayed
		if(len(Q.getAnswers()) > self.ansList.count()):
			# Redraw the list
			
			#First delte the old
			self.ansList.clear()

			# Add the new
			for teamID in Q.getAnswers(): #Should get the key, which is the teamID
				item = QListWidgetItem(self.ansList)
				icon = QIcon('arrow.png')
				item.setText('Group #' + str(teamID))
				item.setIcon(icon)

				

class FinalForm(QWidget):
	
	def __init__(self, parent=None):
		super(FinalForm, self).__init__(parent)
		global playerList
		""" THREADING """

		# Create a list of lists where

		results  = []

		#pl = [x.id for x in playerList]


		""" LAYOUT """
		f = QFont('Helvetica', 16)
		self.setFont(f)
		
		self.resultList = QListWidget()
		self.resultList.setFont(f)

	


		f = QFont('Helvetica', 16)
		

		mainLayout = QGridLayout()
		self.titleLabel = QLabel("Results")
		font = QFont('Helvetica', 42)
		self.titleLabel.setFont(font)




		for p in playerList:
				#print(p.getScore())
				r = [p.id,p.getScore() ]
				#print(r)
				results.append(r)


		for r in results:
			item = QListWidgetItem(self.resultList)
			icon = QIcon('ok.png')
			item.setText('Group #' + str(r[0]) + ":" + str(r[1]))
			item.setIcon(icon)



		endLayout = QHBoxLayout()
		self.exitbtn = QPushButton("Exit Game")
		endLayout.addWidget(self.exitbtn)

		mainLayout.addWidget(self.titleLabel, 0, 0)
		#mainLayout.addLyout(answers, 1, 0)
		mainLayout.addWidget(self.resultList, 2, 0)
		mainLayout.addLayout(endLayout, 5, 0)

		self.setLayout(mainLayout)
		self.setWindowTitle("Results")



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
			ser.timeout = 2
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
							#print("here!!!")
							# Got a real answer, lets handle this.
							
							print("GS: Got ans for team" + str(tID) + " on Q=" + str(qID) + " with ans = " + str(answer) + "@ " + time.strftime("%H:%M:%S", time.gmtime()))
							L.addLog("GS: Got ans for team" + str(tID) + " on Q=" + str(qID) + " with ans = " + str(answer) + "@ " + time.strftime("%H:%M:%S", time.gmtime()))
							#Add to internal structure
							numToLet = ['A','B','C','D']
							

							Q.addAnswer(tID,numToLet[answer])

							#Update GUI!
							newInfo = True

							

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
						L.addLog("Sending Question" + str(Q.questionID()))
					
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
			
			
class NLogger():
	def __init__(self):
		logname = "logs/log-"+time.strftime("%H-%M-%S", time.gmtime())
		self.f = open(logname, 'a')
		self.f.write("test\n")



	def close(self):
		self.f.close()

	def addLog(self,data):
		self.f.write("[" + time.strftime("%H-%M-%S", time.gmtime()) + "] " + data + "\n")

			
			
if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	#Spin up threads

	Q = Questions()

	L = NLogger()

	L.addLog("Stating log")

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
	L.close()
	sys.exit()
