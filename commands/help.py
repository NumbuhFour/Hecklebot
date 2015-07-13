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
		if(message.find("!help") == 0 or message.find("!commands") == 0):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		output = ""
		isOp = self.hb.isOp(user) and message.find("mod") != -1
		for cmd in self.hb.commands:
			pubHelp = cmd.publicHelpString
			if isOp == True:
				help = cmd.helpString
				if help != "":
					output += help + " ### "
			elif pubHelp != "":
				output += pubHelp + " ### "
					
			if(len(output) > 800):
				self.hb.message(user + ": " + output)
				output = ""
				time.sleep(1.5)
			
		self.hb.message(user + ": " + output)