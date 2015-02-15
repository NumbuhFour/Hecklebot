from command import Command
class Koth(Command):
	koth = "numbuhfour"
	kothEnabled = True
	kothDelay = 2400
	kothFileName = "praises.txt"
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "!toggleKOTH: Toggles king of the hill ####### !addPraise [praise]: Add a praise to the king! Use @user@ for name ######## !setKOTHDelay [seconds]: Sets seconds between koth rolls";
		pass
		
	def writeConf(self, conf):
		conf['koth']['king'] = self.koth
		conf['koth']['enabled'] = self.kothEnabled
		conf['koth']['kothDelay'] = self.kothDelay
		conf['koth']['fileName'] = self.kothFileName
		pass
	
	def readFromConf(self, conf):
		self.koth = conf['koth']['king']
		self.kothEnabled = conf['koth']['enabled']
		self.kothDelay = conf['koth']['kothDelay']
		self.kothFileName = conf['koth']['fileName']
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