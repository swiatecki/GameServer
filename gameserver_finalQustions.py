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
			'Question': 'Where was mechatronics invented?',
			'A': 'Korea',
			'B': 'Germany',
			'C': 'USA',
			'D': 'Japan',
			'correctAnswer':'D'
			})
        #2
		self.questionList.append({
			'Question': 'What is the name of design methodology \n that is commonly used in mechatronics?',
			'A': 'V model',
			'B': 'W model',
			'C': 'Morphology model',
			'D': 'VDI 2246',
			'correctAnswer':'A'
			})
        #3
		self.questionList.append({
			'Question': 'Which domain is not related to mekatronik?',
			'A': 'Information Tech.',
			'B': 'Electronics Eng.',
			'C': 'Management Eng.',
			'D': 'Mechanical eng. ',
			'correctAnswer':'C'
			})

        #4
		self.questionList.append({
			'Question': 'Which one is not a mechatronics product \n ( or least mechatronics related..)?',
			'A': 'An iphone',
			'B': 'A vending machine',
			'C': 'A car',
			'D': 'A dymo labeling machine',
			'correctAnswer':'B'
			})
        
        #5 - img
		self.questionList.append({
			'Question': 'What is the current?',
			'A': '0.205A',
			'B': '0.0205A',
			'C': '0.0123A',
			'D': '0.123A',
			'correctAnswer':'C'
			})

	
        #6 - img
		self.questionList.append({
			'Question': 'Resistance between A-W is ..',
			'A': 'greater',
			'B': 'smaller',
			'C': 'equal',
			'D': 'not related',
			'correctAnswer':'B'
			})

	
        #7
		self.questionList.append({
			'Question': 'What is the chip on the arduino uno?',
			'A': 'Atmega 328',
			'B': 'Atmega u16',
			'C': 'Atmega u32',
			'D': 'Atmega2460',
			'correctAnswer':'A'
			})

	
        #8
		self.questionList.append({
			'Question': 'Which are the bare-essential function(s) \n for an arduino to be able to run?',
			'A': 'setup,serial',
			'B': 'serial,loop',
			'C': 'serial,println',
			'D': 'setup, loop',
			'correctAnswer':'D'
			})
        #9
		self.questionList.append({
			'Question': 'Your arduino is connected to USB power, and the \n analogRead(A0) = 346   / what is the voltage read by the ADC?',
			'A': '1.69',	
			'B': '2.31',
			'C': '2.69',
			'D': '3.31',
			'correctAnswer':'A'
			})

	
        #10
		self.questionList.append({
			'Question': 'Your arduino is connected to USB power, and if \n we use: analogWrite(6,135), how much Voltage \n is generated at the pin no 6?',
			'A': '0.66',
			'B': '1.22',
			'C': '2.06',
			'D': '2.65',
			'correctAnswer':'D'
			})

	
        #11
		self.questionList.append({
			'Question': 'which one is NOT correct about sensors?',
			'A': 'converts physical measurements to electrical',
			'B': 'can be active / passive',
			'C': 'can be used as an output',
			'D': 'can be analog or digital',
			'correctAnswer':'C'
			})
        #12
		self.questionList.append({
			'Question': 'which one can NOT be used to detect physical presence?',
			'A': 'gyroscope',
			'B': 'laser range finder',
			'C': 'sonar',
			'D': 'photoelectric switch',
			'correctAnswer':'A'
			})

	
        #13
		self.questionList.append({
			'Question': 'which one can be used to detect Rotation?',
			'A': 'sonar/ultrasonic rf',
			'B': 'photolectric switch',
			'C': 'linear potentiometer',
			'D': 'optical encoders',
			'correctAnswer':'D'
			})

	
        #14
		self.questionList.append({
			'Question': 'Which one is NOT related to sensor performance?',
			'A': 'range',
			'B': 'cost',
			'C': 'accuracy',
			'D': 'resolution',
			'correctAnswer':'B'
			})
        #15
		self.questionList.append({
			'Question': 'which one is NOT a typical machine element?',
			'A': 'battery',
			'B': 'belt',
			'C': 'spring',
			'D': 'gear',
			'correctAnswer':'A'
			})

	
        #16
		self.questionList.append({
			'Question': 'gears can NOT be used for? changing ..',
			'A': 'speed',
			'B': 'power',
			'C': 'torque',
			'D': 'axis of rotation',
			'correctAnswer':'B'
			})

	
        #17
		self.questionList.append({
			'Question': 'pulleys you got for the CNC project has ... teeth',
			'A': '8',
			'B': '12',
			'C': '16',
			'D': '20',
			'correctAnswer':'C'
			})
        #18
		self.questionList.append({
			'Question': 'the belt you got for the CNC project has \n ... tooth profile',
			'A': 'T2.5',
			'B': 'T5',
			'C': 'GT2.5',
			'D': 'GT5',
			'correctAnswer':'A'
			})

	
        #19 - img
		self.questionList.append({
            'Question': 'If gear A has the speed of 30 rpm,\n what is the speed of gear D? ',
			'A': '90',
			'B': '180',
			'C': '360',
			'D': '400',
			'correctAnswer':'C'
			})

	
        #20
		self.questionList.append({
			'Question': 'The x-axis of your machine have a 16 teeth pulley and \n t2.5 belt (2.5mm pitch). Your stepper motor can do \n 200 steps per revolution. what is the steps/mm \n value your controller needs to know?',
			'A': '2.5',
			'B': '5.0',
			'C': '25.0',
			'D': '31.25',
			'correctAnswer':'B'
			})

	
        #21
		self.questionList.append({
			'Question': 'Which 3d printing technology does not exist at dtu fablab?',
			'A': 'SLS - selective laser sintering',
			'B': 'FDM - Fused depositon manufacturing',
			'C': 'LENS - LAser Engineered Net Shaping',
			'D': 'LOM - Laminated object manufacturing',
			'correctAnswer':'C'
			})
        #22 - img
		self.questionList.append({
			'Question': 'you are printing on your good friend ultimaker. \n which one does not need any support structures?',
			'A': 'A',
			'B': 'B',
			'C': 'C',
			'D': 'D',
			'correctAnswer':'D'
			})

	
        #23
		self.questionList.append({
			'Question': 'degrees of freedom (DOF):in how many different ways an \n object’s orientation and position can be changed? \n What is the OPERATIONAL DOF a car?',
			'A': '1',
			'B': '2',
			'C': '3',
			'D': '6',
			'correctAnswer':'B'
			})

	
        #24 - img 
		self.questionList.append({
			'Question': 'A revolute joint (hinge) has 1 DOF. \n Which moments are NOT transmitted from one link to another? ',
			'A': 'Mx',
			'B': 'My',
			'C': 'Mz',
			'D': 'None',
			'correctAnswer':'B'
			})
        
        #25 - img
		self.questionList.append({
			'Question': 'A sperical joint has 3 DOF. Which moments are \n NOT transmitted from one link to another?',
			'A': 'Mx',
			'B': 'My',
			'C': 'Mz',
			'D': 'None',
			'correctAnswer':'D'
			})

	
        #26
		self.questionList.append({
			'Question': 'Which type of motor is most prone to internal \n mechanical friction and failure?',
			'A': 'Brushed DC motor',
			'B': 'Brushless DC motor',
			'C': 'AC motor',
			'D': 'Stepper motor',
			'correctAnswer':'A'
			})

	
        #27
		self.questionList.append({
			'Question': 'Which one does not need a closed-loop \n feedback for position control?',
			'A': 'Servo motor',
			'B': 'Brushless DC motor',
			'C': 'Brushless DC motor w/ gearbox',
			'D': 'Stepper motor',
			'correctAnswer':'D'
			})
        #28
		self.questionList.append({
			'Question': 'Which type of actuation is not electromagnetic?',
			'A': 'Solenoid',
			'B': 'Peltier',
			'C': 'Stepper',
			'D': 'Servo motor',
			'correctAnswer':'B'
			})

	
        #29
		self.questionList.append({
			'Question': 'Resistance of a nichrome wire does NOT depend on ..',
			'A': 'length',
			'B': 'thickness',
			'C': 'temperature',
			'D': 'voltage',
			'correctAnswer':'D'
			})

	
        #30
		self.questionList.append({
			'Question': 'You have a 5V power source and 24 WG (4.563 Ohms/m) \n wire. You want to cut foam at 316 C (2.76 A current needed).\n What should be the length of your wire?',
			'A': '82.6 cm',
			'B': '62.9 cm',
			'C': '39.7 cm',
			'D': '30.2 cm',
			'correctAnswer':'C'
			})
        
       #31
		self.questionList.append({
			'Question': 'A typical (e.g. radiator) thermostat uses ..',
			'A': 'open-loop control',
			'B': 'closed-loop control',
			'C': 'PI control',
			'D': 'PID control',
			'correctAnswer':'B'
			})
    

       #32 - img 
		self.questionList.append({
			'Question': 'which one uses a PID controller?',
			'A': 'A',
			'B': 'B',
			'C': 'C',
			'D': 'D',
			'correctAnswer':'A'
			})
    

        #33
		self.questionList.append({
			'Question': 'we can build logic gates with ...',
			'A': 'resistors',
			'B': 'capacitors',
			'C': 'diodes',
			'D': 'transistors',
			'correctAnswer':'D'
			})
    

        #34
		self.questionList.append({
			'Question': 'If we have two variables: X = 10 and Y= 900, \n what is the reulst of this boolean expression:\n NOT((X==10)OR(Y>1000))AND (X>Y)',
			'A': 'true',
			'B': 'false',
			'C': 'neither',
			'D': 'no idea',
			'correctAnswer':'B'
			})
    

        #35
		self.questionList.append({
			'Question': 'what are c,d?',
			'A': '1,1',
			'B': '1,0',
			'C': '0,1',
			'D': '0,0',
			'correctAnswer':'A'
			})
    

        #36 - img
		self.questionList.append({
			'Question': 'We have a coffee machine that sells coffee for 60 cents \n and can accept 5, 10, 25 cents. If we design a state machine\n based on the amount of money put in the vending machine, \nhow many states we would have?  ',
			'A': '8',
			'B': '10',
			'C': '12',
			'D': '14',
			'correctAnswer':'C'
			})
    

        #37
		self.questionList.append({
			'Question': 'NRF24L01 uses .. ',
			'A': '1-Wire',
			'B': 'I2C',
			'C': 'TWI',
			'D': 'SPI',
			'correctAnswer':'D'
			})
    

        #38
		self.questionList.append({
			'Question': 'Which one is not suitable for the laser \n cutting/engraving machine?',
			'A': 'Acrylic',
			'B': 'plywood',
			'C': 'PET',
			'D': 'Stone',
			'correctAnswer':'C'
			})
    

        #39 - img
		self.questionList.append({
			'Question': 'What should we do?',
			'A': 'inc-inc',
			'B': 'dec-inc',
			'C': 'na-dec',
			'D': 'inc-na',
			'correctAnswer':'B'
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
