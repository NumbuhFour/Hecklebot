from command import Command
import time
import traceback
class EvalCMD(Command):
	def __init__(self, hb):
		self.hb = hb
		pass

	def checkMessage(self, message, user):
		message = message.strip().lower()
		if(str.startswith(message,"!voop") or str.startswith(message,"!zoop") and user == "numbuhfour"):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		print "User " + user + " attempted " + message[1:6] + " " + message[6:]
		if(user.lower().strip() == "numbuhfour"):
			try:
				if str.startswith(message, "!voop"):
					eval(message[6:])
				elif str.startswith(message,"!zoop"):
					exec(message[6:])
			except:
				traceback.print_exc()