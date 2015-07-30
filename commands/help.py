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
		isOp = self.hb.isOp(user)
		modList = message.find("mod") != -1
		topic = ""
		split = message.lower().split(' ')
		if(len(split) > 1 and not modList):
			topic = split[1].strip()
		if(isOp and modList):
			output = "Type !help [topic] for more info. Available topics: "
			for cmd in self.hb.commands:
				if cmd.helpString != "":
					output += cmd.getName().lower() + ", "
			output = output[:-2]
		elif(topic == "" or not isOp):
			for cmd in self.hb.commands:
				pubHelp = cmd.publicHelpString
				if pubHelp != "":
					output += pubHelp + " ### "
						
				if(len(output) > 800):
					self.hb.message(user + ": " + output)
					output = ""
					time.sleep(1.5)
		elif(topic != ""):
			found = False
			for cmd in self.hb.commands:
				if cmd.getName().lower() == topic:
					found = True
					output = cmd.helpString + " ### " + cmd.publicHelpString
					break
			if( not found ):
				output = "Topic '" + topic + "' not found."
			
		self.hb.message(user + ": " + output)