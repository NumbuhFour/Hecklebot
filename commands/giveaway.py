from command import Command
from random import randint
class Giveaway(Command):

	def __init__(self, hb):
		self.hb = hb
		self.helpString = "!giveaway [viewers] [followers] [subscribers]: Pick a person for the giveaway";
		pass
		
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!giveaway ') == 0 and self.hb.isOp(user):
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!giveaway ') == 0:
			pool = []
			if lower.find('followers') != -1:
				fol = self.hb.getFollowers()
				if fol == None:
					self.hb.message(user + ": Error fetching followers. Try again in a bit.")
					return
				pool += fol
			if lower.find('viewers') != -1:
				pool += self.hb.viewers
			if lower.find('subscribers') != -1:
				sub = self.hb.getSubscribers()
				if sub == None:
					self.hb.message(user + ": Error fetching followers. Try again in a bit.")
					return
				pool += sub
			pool = list(set(pool)) #remove duplicates
			print pool
			self.hb.message("{0}: And the winner is...... {1}!".format(user, pool[randint(0,len(pool)-1)]))
			#return