class Command:
	reqOp = False;
	helpString = ""
	publicHelpString = ""
	def __init__(self, hb):
		self.hb = hb
		pass
	def getName(self):
		return self.__class__.__name__
	
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
	
	''' Returns true if the message is a call for this command '''
	def checkMessage(self, message, user):
		pass
	
	def onMessage(self, message, user):
		pass
	
	def onTerminalCommand(self, message):
		pass
	
	#In case a class has a thread
	def start(self):
		pass
	def stop(self):
		pass
		
	def onJoin(self, user):
		pass
	
	def onPart(self, user):
		pass
		
	def onStreamBegin(self):
		pass
	
	def onStreamEnd(self):
		pass
		