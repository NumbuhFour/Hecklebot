from command import Command
import time
class Help(Command):
	def __init__(self, hb):
		self.hb = hb
		self.publicHelpString = "!help: Print help";
		pass
		
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
		
	def checkMessage(self, message, user):
		message = message.strip().lower()
		if(message == "!help"):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		output = ""
		isOp = self.hb.isOp(user)
		for cmd in self.hb.commands:
			pubHelp = cmd.publicHelpString
			if pubHelp != "":
				output += pubHelp + " ######## "
			if isOp == True:
				help = cmd.helpString
				if help != "":
					output += help + " ######## "
					
			if(len(output) > 800):
				self.hb.message(user + ": " + output)
				output = ""
				time.sleep(1.5)
			
		self.hb.message(user + ": " + output)