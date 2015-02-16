from command import Command
from random import randint
import threading
import time
class Giveaway(Command):

	auctionRunning = False
	auctionTime = 0
	timeRemaining = 0
	auctionPrize = ""
	currentLeader = "no one"
	currentBid = 0
	auctionStarted = 0

	def __init__(self, hb):
		self.hb = hb
		self.money = self.hb.money
		self.helpString = "*!giveaway [viewers] [followers] [subscribers]: Pick a person for the giveaway ######## *!startAuction [startingBid] [seconds] [prize]: Start a monies auction for the prize ######## *!cancelAuction: Cancels the current auction";
		self.publicHelpString = "!bid [amount]: Bid for the current auction"
		pass
		
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		isOp = self.hb.isOp(user)
		if lower.find('!bid ') == 0:
			return True
		elif lower.find('!giveaway ') == 0 and isOp == True:
			return True
		elif lower.find('!startauction ') == 0 and isOp == True:
			return True
		elif lower.find('!cancelauction') == 0 and isOp == True:
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!bid ') == 0:
			try:
				amount = int(lower[5:])
				self.bid(user, amount)
			except ValueError:
				pass
		elif lower.find('!giveaway ') == 0:
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
		elif lower.find('!startauction ') == 0:
			split = message.split(' ')
			if len(split) >= 3:
				try:
					starting = int(split[1])
					duration = int(split[2])
					prize = ""
					if len(split) > 3:
						prize = message[len(split[0]) + len(split[1]) + len(split[2]) + 3:]
					
					self.startAuction(starting,duration,prize)
				except ValueError:
					pass
		elif lower.find('!cancelauction ') == 0:
			self.cancelAuction()
			self.hb.message(user + ": Auction cancelled")
		
	def startAuction(self, startingBid, duration, prize):
		#an auction has started for prize! Starting bid: bid. x seconds remain!
		self.timeRemaining = duration
		self.auctionTime = duration
		self.auctionPrize = prize
		self.currentBid = startingBid
		self.auctionRunning = True
		
		prizeMsg = ""
		print ("RAWR " + prize)
		if prize != "":
			prizeMsg = " for " + prize
		self.hb.message("An auction has started" + prizeMsg + "! Starting bid: " + str(startingBid) + ". Type !bid [amount] to bid points. Time remaining: " + str(int(self.timeRemaining)))
		
		remTime = duration%10
		if remTime == 0:
			remTime = 10
		print ("Start wait " + str(remTime))
		threading.Timer(remTime, self.checkAuction).start()
		self.auctionStarted = time.time()
		pass
	
	def bid(self, user, amount):
		bal = self.money.checkBalance(user)
		if amount > bal:
			self.hb.message(user + ": You don't have that many monies! " + self.getAuctionStatus())
		elif self.currentBid > amount:
			self.hb.message(user + ": You must bid more than the current winner! " + self.getAuctionStatus())
		else:
			self.currentBid = amount
			self.currentLeader = user
			self.hb.message(user + ": You have taken the lead! " + self.getAuctionStatus())
		pass
	
	def getAuctionStatus(self):
		curTime = time.time()
		self.timeRemaining = self.auctionTime - (curTime - self.auctionStarted)
		return str(int(round(self.timeRemaining))) + " seconds remain with " + self.currentLeader + " winning by " + str(self.currentBid) + " monies"
		
	def checkAuction(self):
		if self.auctionRunning == False or self.hb.stop == True:
			return
		#curTime = time.time()
		#self.timeRemaining = self.auctionTime - (curTime - self.auctionStarted)
		self.hb.message(self.getAuctionStatus())
		
		if(self.timeRemaining < 5):
			threading.Timer(self.timeRemaining, self.endAuction).start()
		elif(self.timeRemaining < 10):
			threading.Timer(5, self.checkAuction).start()
		else:
			threading.Timer(min(10, self.timeRemaining), self.checkAuction).start()
		pass
	
	def cancelAuction(self):
		self.auctionRunning = False
		pass
	
	def endAuction(self):
		self.hb.message("The auction has ended! " + self.currentLeader + " has won with a bid of " + str(self.currentBid) + "!")
		if self.currentLeader != "no one":
			self.money.pay(self.currentLeader, -self.currentBid)
		pass
		
	def autoHeckle(self): #auto heckles
		if self.hb.stop == False:
			threading.Timer(10, self.autoHeckle).start()
		else:
			return
			
		self.heckleTimerCountdown -= 10
		if(self.heckleTimerCountdown <= 0):
			if self.hb.checkStreamOnline() == True:
				self.sendHeckle(self.hb.streamer)
			self.heckleTimerCountdown = self.heckleTimer