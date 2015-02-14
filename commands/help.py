from command import Command
class Help(Command):
	def __init__(self, hb):
		self.hb = hb
		pass
		
	def writeToConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
		
	def checkMessage(self, message, user):
		if(message.lower() == "!help"):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		self.hb.message(user + ": You're a chicken!");