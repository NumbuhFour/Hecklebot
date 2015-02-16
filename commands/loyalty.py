from command import Command
import json
class Loyalty(Command):
	#For adding money each time someone joins
	moneyPerView = 200
	fileName = "streamPaymentTracker.txt"
	alreadyPaid = []
	def __init__(self, hb):
		self.hb = hb
		self.money = self.hb.money
		self.helpString = "*!setMoneyPerStream [amount]: Sets amount received for viewing a stream ######## *!resetStreamTracking: Resets stream tracking for monies distribution"
		pass
		
	def writeConf(self, conf):
		conf['loyalty'] = { "moneyPerView":self.moneyPerView , "fileName":self.fileName}
		self.saveAlreadyPaid()
		pass
	
	def readFromConf(self, conf):
		self.moneyPerStream = conf['loyalty']['moneyPerView']
		self.fileName = conf['loyalty']['fileName']
		self.loadAlreadyPaid()
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if self.hb.isOp(user):
			if lower.find('!setmoneyperstream ') == 0:
				return True
			if lower.find('!resetstreamtracking') == 0:
				return True
				
		return False
		
	def onMessage(self, message, user):
		lower = message.strip().lower()

		if(self.hb.isOp(user) == True):
			if lower.find('!setmoneyperstream ') == 0:
				split = message.split(' ')
				if len(split) == 2:
					amt = split[1]
					try: 
						amount = int(amt)
						moneyPerView = amount
						self.hb.message(user + ": Now giving " + str(moneyPerView) + " monies per stream")
					except ValueError:
						self.hb.message(user + ": Error.")
						pass
			if lower.find('!resetstreamtracking') == 0:
				self.onStreamEnd()
				self.onStreamBegin()
				self.hb.message(user + ": Stream status reset.")
		pass
	
	def onJoin(self, user):
		if self.hb.checkStreamOnline():
			if (user in self.alreadyPaid) == False:
				self.hb.log("Paying " + user + " for loyalty")
				self.money.pay(user, self.moneyPerView)
				self.alreadyPaid.append(user.lower())
			self.saveAlreadyPaid()
		pass
	
	def onStreamBegin(self):
		for user in self.hb.viewers:
			self.hb.log("Paying " + user + " for loyalty (stream begin")
			self.money.pay(user, self.moneyPerView)
			self.alreadyPaid.append(user.lower())
		pass
	
	def onStreamEnd(self):
		self.alreadyPaid = []
		self.saveAlreadyPaid()
		pass
		
	def saveAlreadyPaid(self):
		with open(self.fileName, 'w') as outfile: 
			json.dump(self.alreadyPaid,outfile)
		pass
		
	def loadAlreadyPaid(self):
		f = open(self.fileName,'r')
		self.alreadyPaid = json.loads(f.read());
		f.close()