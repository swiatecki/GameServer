runstate = True
playerList = []

class Player:
	id = None
	score = None

	def __init__(self, _id):
		self.id = _id
		self.score = 0




p1 = Player(1)
p2 = Player(2)

playerList.append(p1)
playerList.append(p2)


print (3 in [x.id for x in playerList])

items = []
pl = [x.id for x in playerList]

diff = list(set([x.id for x in playerList]).difference(items))

print(diff)