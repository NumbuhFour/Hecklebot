from command import Command
from random import randint
import threading
import time
import json
class Giveaway(Command):

	auctionRunning = False
	auctionTime = 0
	timeRemaining = 0
	auctionPrize = ""
	currentLeader = "no one"
	currentBid = 0
	auctionStarted = 0
	bucket = []
	bucketStarted = False
	auctionThread = None
	
	raffleStarted = False
	maxRaffleEntries = 1
	minRaffleEntries = 1
	raffle = {}
	
	bucketFile = "giveawayBucket.txt"
	raffleFile = "raffle.txt"

	def __init__(self, hb):
		self.hb = hb
		if(hasattr(self.hb, 'money')):
			self.money = self.hb.money
		else:
			self.money = None
		self.helpString = "*!startgiveaway: Clears the names currently in the giveaway bucket ### *!giveaway [viewers] [followers] [subscribers] [bucket]: Pick a person for the giveaway"
		self.publicHelpString = "!pickme: Add yourself to the bucket for the next giveaway"
		if(self.money != None):
			self.helpString += "### *!startAuction [startingBid] [seconds] [prize]: Start a " + self.money.moneyString + " auction for the prize ### *!cancelAuction: Cancels the current auction ### *!startRaffle [minimum entries] [maximum entries]: Start a raffle using " + self.money.moneyString + " as tickets ### *!cancelRaffle: Cancels the running raffle "
			self.publicHelpString += " ### !bid [amount]: Bid for the current auction ### !enterRaffle [" + self.money.moneyString + "]: Enter X number of " + self.money.moneyString + " with your name on them into the raffle ### !leaveRaffle: Remove your " + self.money.moneyString + " from the raffle "
		pass
		
	def writeConf(self, sqli):
		
		sqli.writeToConfig(self.getName(), 'givstart', str(self.giveawayStarted))
		sqli.writeToConfig(self.getName(), 'rafstart', str(self.raffleStarted))
		sqli.writeToConfig(self.getName(), 'maxrafen', str(self.maxRaffleEntries))
		sqli.writeToConfig(self.getName(), 'minrafen', str(self.minRaffleEntries))
		"""
		conf['giveaway'] = {}
		conf['giveaway']['bucketFile'] = self.bucketFile
		conf['giveaway']['giveawayStarted'] = self.bucketStarted
		conf['giveaway']['raffleFile'] = self.raffleFile
		conf['giveaway']['raffleStarted'] = self.raffleStarted
		conf['giveaway']['maxRaffleEntries'] = self.maxRaffleEntries
		conf['giveaway']['minRaffleEntries'] = self.minRaffleEntries
		"""
		
		self.writeBucketFile()
		self.writeRaffleFile()
		pass
	
	def readFromConf(self, sqli):
		self.bucketStarted = sqli.readFromConfig(self.getName(), 'givstart', "False") == "True"
		self.raffleStarted = sqli.readFromConfig(self.getName(), 'rafstart', "False") == "True"
		self.maxRaffleEntries = int(sqli.readFromConfig(self.getName(), 'maxrafen', "1"))
		self.minRaffleEntries = int(sqli.readFromConfig(self.getName(), 'minrafen', "1"))
		"""
		self.bucketFile = conf['giveaway']['bucketFile']
		self.bucketStarted = conf['giveaway']['giveawayStarted']
		if('raffleFile' in conf['giveaway']):
			self.raffleFile = conf['giveaway']['raffleFile']
			self.raffleStarted = conf['giveaway']['raffleStarted']
			self.maxRaffleEntries = conf['giveaway']['maxRaffleEntries']
			self.maxRaffleEntries = conf['giveaway']['minRaffleEntries']
		else:
			self.raffleFile = 'raffle.txt'
			self.raffleStarted = False
			self.maxRaffleEntries = 1
		"""
		self.readBucketFile()
		self.readRaffleFile()
		pass
	
	def writeBucketFile(self):
		with open(self.bucketFile, 'w') as outfile: 
			json.dump(self.bucket,outfile)
		pass
	
	def readBucketFile(self):
		f = open(self.bucketFile,'r')
		self.bucket = json.loads(f.read());
		f.close()
		
	def writeRaffleFile(self):
		with open(self.raffleFile, 'w') as outfile: 
			json.dump(self.raffle,outfile)
		pass
	
	def readRaffleFile(self):
		f = open(self.raffleFile,'r')
		self.raffle= json.loads(f.read());
		f.close()
	
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		isOp = self.hb.isOp(user)
		if self.money != None and lower.find('!bid ') == 0:
			return True
		if lower.find('!pickme') == 0:
			return True
		elif lower.find('!unpickme') == 0:
			return True
		elif lower.find('!enterraffle') == 0:
			return True
		elif lower.find('!leaveraffle') == 0:
			return True
		elif lower.find('!giveaway ') == 0 and isOp == True:
			return True
		elif self.money != None and lower.find('!startauction ') == 0 and isOp == True:
			return True
		elif self.money != None and lower.find('!cancelauction') == 0 and isOp == True:
			return True
		elif lower.find('!startgiveaway') == 0 and isOp == True:
			return True
		elif lower.find('!addname') == 0 and isOp == True:
			return True
		elif self.money != None and lower.find('!startraffle') == 0 and isOp == True:
			return True
		elif self.money != None and lower.find('!cancelraffle') == 0 and isOp == True:
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
		elif lower.find('!pickme') == 0:
			if self.bucketStarted == False:
				self.hb.message(user + ": The giveaway hasn't started yet!")
			elif(not user in self.bucket):
				self.hb.message(user + ": Your name has been added to the giveaway pool.")
				self.bucket.append(user)
				print(self.bucket)
				self.writeBucketFile()
			else:
				self.hb.message(user + ": Your name is already in the giveaway pool! Type !unpickMe if you want to cancel.")
		elif lower.find('!unpickme') == 0 and user in self.bucket:
			self.hb.message(user + ": You've been removed from the pool!")
			self.bucket.remove(user)
			self.writeBucketFile()
		elif lower.find('!enterraffle') == 0:
			if(self.raffleStarted == False):
				self.hb.message(user + ": The raffle hasn't started yet!")
				return
			amount = 1
			split = lower.split(" ")
			if len(split) > 0:
				amount = int(split[1])
			if amount <= 0:
				self.hb.message(user + ": You must enter a postive number of " + self.money.moneyString + "!")
				return
			elif amount < self.minRaffleEntries:
				self.hb.message(user + ": You must enter more than " + str(self.minRaffleEntries) + " " + self.money.moneyString + " into this raffle!")
				return
			elif amount > self.maxRaffleEntries:
				self.hb.message(user + ": You cannot enter more than " + str(self.maxRaffleEntries) + " " + self.money.moneyString + " into this raffle!")
				return
			
			if user in self.raffle:
				if self.raffle[user] == amount:
					self.hb.message(user + ": You are already entered in the raffle with " + str(amount) + " " + self.money.moneyString)
				elif (self.money.checkBalance(user)["money"] + self.raffle[user]) >= amount:
					self.money.pay(user,self.raffle[user]) # Pay back previous amount
					self.raffle[user] = amount
					self.money.pay(user, -amount)
					self.writeRaffleFile()
					self.hb.message(user + ": You have changed your raffle entry to " + str(amount) + " " + self.money.moneyString + "!" )
				else:
					self.hb.message(user + ": You don't have " + str(amount) + " " + self.money.moneyString + " to enter into the raffle!")
			else:
				if self.money.checkBalance(user)["money"] >= amount:
					self.raffle[user] = amount
					self.money.pay(user, -amount)
					self.writeRaffleFile()
					self.hb.message(user + ": You have entered " + str(amount) + " " + self.money.moneyString + " into the raffle!" )
				else:
					self.hb.message(user + ": You don't have " + str(amount) + " " + self.money.moneyString + " to enter into the raffle!")
		elif lower.find('!leaveraffle') == 0 and user in self.raffle:
			self.hb.message(user + ": You've been removed from the raffle!")
			self.money.pay(user, self.raffle[user])
			del self.raffle[user]
			self.writeRaffleFile()

		elif lower.find('!startgiveaway') == 0:
			self.bucketStarted = True
			self.bucket = []
			self.hb.message('/me A givaway begins! Type !pickme to put your name in the pool!')
			#self.writeBucketFile()
			self.hb.saveSettings()
		elif lower.find('!addname ') == 0:
			split = lower.split(' ')
			if(len(split) >1):
				name = split[1]
				if name.find("@") == 0:
					name = name[1:]
				if self.bucketStarted == False:
					self.hb.message(user + ": The giveaway hasn't started yet!")
				elif(not name in self.bucket):
					self.hb.message(user + ": " + name + "'s name has been added to the giveaway pool.")
					self.bucket.append(name)
					print(self.bucket)
					self.writeBucketFile()
				else:
					self.hb.message(user + ": " + name + "'s name is already in the giveaway pool! Type !unpickMe if you want to cancel.")
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
				if self.hb.streamer in pool: # remove streamer
					pool.remove(self.hb.streamer)
			if lower.find('subscribers') != -1:
				sub = self.hb.getSubscribers()
				if sub == None:
					self.hb.message(user + ": Error fetching followers. Try again in a bit.")
					return
				pool += sub
				if self.hb.streamer in pool: # remove streamer
					pool.remove(self.hb.streamer)
			if lower.find('bucket') != -1 or lower.find('pool') != -1:
				pool += self.bucket
			pool = list(set(pool)) #remove duplicates
			if lower.find('raffle') != -1:
				for name in self.raffle:
					for i in range(self.raffle[name]):
						pool.append(name)
			
			print pool
			if len(pool) == 0:
				self.hb.message("There's no one for me to pick from in that category!")
			else:
				self.hb.message("/me {0}: And the winner is...... {1}!".format(user, pool[randint(0,len(pool)-1)]))
				self.bucketStarted = False
				self.hb.saveSettings()
			#return
		elif lower.find('!startraffle') == 0:
			split = lower.split(' ')
			self.maxRaffleEntries = 1
			if len(split) >= 2:
				self.minRaffleEntries = int(split[1])
			else:
				self.minRaffleEntries = 1
			if len(split) >= 3:
				self.maxRaffleEntries = int(split[2])
			else:
				self.maxRaffleEntries = 200
			self.raffleStarted = True
			self.raffle = {}
			self.hb.message('/me A raffle begins! Type "!enterRaffle X" where X is the number of ' + self.money.moneyString + " you'd like to enter to put your name in the pool!")
			# self.writeRaffleFile()
			self.hb.saveSettings()
			pass
		elif lower.find('!cancelraffle') == 0:
			self.raffleStarted = False
			self.hb.message(user + ": Raffle canceled")
			for name in self.raffle:
				self.money.pay(name,self.raffle[name])
			self.raffle = {}
			self.hb.saveSettings()
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
		self.auctionThread = threading.Timer(remTime, self.checkAuction)
		self.auctionThread.start()
		self.auctionStarted = time.time()
		pass
	
	def bid(self, user, amount):
		if(not self.auctionRunning):
			self.hb.message(user + ": No auction currently running!")
			return
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
			self.auctionThread = threading.Timer(self.timeRemaining, self.endAuction)
			self.auctionThread.start()
		elif(self.timeRemaining < 15):
			self.auctionThread = threading.Timer(5, self.checkAuction)
			self.auctionThread.start()
		elif(self.timeRemaining < 40):
			self.auctionThread = threading.Timer(min(10, self.timeRemaining), self.checkAuction)
			self.auctionThread.start()
		elif(self.timeRemaining < 300):
			self.auctionThread = threading.Timer(min(30, self.timeRemaining), self.checkAuction)
			self.auctionThread.start()
		else:
			self.auctionThread = threading.Timer(min(60, self.timeRemaining), self.checkAuction)
			self.auctionThread.start()
		pass
	
	def cancelAuction(self):
		self.auctionRunning = False
		self.auctionThread.cancel()
		pass
	
	def endAuction(self):
		self.auctionRunning = False
		self.auctionThread = threading.Timer(3, self.announceEndAuction)
		self.auctionThread.start()
		
	# Because people can slip in and break it
	def announceEndAuction(self):
		self.hb.message("The auction has ended! " + self.currentLeader + " has won with a bid of " + str(self.currentBid) + "!")
		if self.currentLeader != "no one":
			self.money.pay(self.currentLeader, -self.currentBid)
		pass
		
	def stop(self):
		if(self.auctionRunning):
			self.auctionThread.cancel()