from command import Command
class Koth(Command):
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "!help: DERP";
		pass
		
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
		
	def checkMessage(self, message, user):
		message = message.strip().lower()
		if(message == "!help"):
			self.hb.log("WOOO")
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		self.hb.log("GO!!!!")
		self.hb.message(user + ": You're a chicken!");
	
	def refreshPraises(self):
		self.kothFile = open(self.kothFileName, 'r+')
		self.kothPraises = self.kothFile.read().split('\n')
		self.kothFile.close() #refreshing list