from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import serial
import threading

class Form(QWidget):
	def __init__(self, parent=None):
		super(Form, self).__init__(parent)

		nameLabel = QLabel("Name:")
		self.nameLine = QLineEdit()
		self.submitButton = QPushButton("Submit")
		self.qlist = QListWidget()

		buttonLayout1 = QVBoxLayout()
		buttonLayout1.addWidget(nameLabel)
		buttonLayout1.addWidget(self.nameLine)
		buttonLayout1.addWidget(self.submitButton)
		buttonLayout1.addWidget(self.qlist)
		
		
		for i in [1,2,4,1,7,3]:
			item = QListWidgetItem(self.qlist)
			icon = QIcon('ok.png')
			#icon = QIcon('D:\python-dev\ok.png')
			item.setText('Group #' + str(i))
			item.setIcon(icon)
		
		self.submitButton.clicked.connect(self.submitContact)

		mainLayout = QGridLayout()
		# mainLayout.addWidget(nameLabel, 0, 0)
		mainLayout.addLayout(buttonLayout1, 0, 1)

		self.setLayout(mainLayout)
		self.setWindowTitle("Hello Qt")

	def submitContact(self):
		#self.qlist.sortItems()
		x = self.qlist.findItems('Group #7',Qt.MatchExactly)
		for item in x:
			self.qlist.takeItem(self.qlist.indexFromItem(item).row())
		name = self.nameLine.text()

		if name == "":
			QMessageBox.information(self, "Empty Field","Please enter a name and address.")
			return
		else:
			QMessageBox.information(self, "Success!","Hello \"%s\"!" % name)

if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	screen = Form()
	screen.show()

	sys.exit(app.exec_())
