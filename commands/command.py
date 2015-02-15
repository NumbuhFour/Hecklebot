class Command:
	reqOp = False;
	helpString = ""
	def __init__(self, hb):
		self.hb = hb
		pass
		
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
	
	''' Returns true if the message is a call for this command '''
	def checkMessage(self, message, user):
		pass
	
	def onMessage(self, message, user):
		pass
	
	#In case a class has a thread
	def start(self):
		pass