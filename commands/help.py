from command import Command
class Help(Command):
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
		if(message == "!help" and self.hb.isOp(user)):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		output = ""
		for cmd in self.hb.commands:
			help = cmd.helpString
			if help != "":
				output += help + " ######## "
		self.hb.message(user + ": " + output)