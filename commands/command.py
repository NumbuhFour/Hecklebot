class Command:
	reqOp = False;
	def __init__(self, hb):
		self.hb = hb
		pass
		
	def writeToConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
	
	''' Returns true if the message is a call for this command '''
	def checkMessage(self, message, user):
		pass
	
	def onMessage(self, message, user):
		pass
	
	def requireOP(self):
		return self.reqOp;