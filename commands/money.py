from command import Command
import json
import time
import threading

class Money(Command):
	fileName = 'money.txt'
	bank = {}
	karmaTimer = {}
	karmaPerVote = 1
	voteDelay = 10*60
	payPerViewDelay = 45*60 # How often in seconds currency is distributed
	karmaGiveLimit = 5
	
	moneyString = "Oreos"
	karmaString = "Warm Fuzzies"
	
	streamThreadRunning = False
	streamThread = None
	
	def __init__(self, hb):
		self.hb = hb
		self.publicHelpString = "!balance: Prints out your current balance ### !pay [target] [amount]: Pays target x monies from your account ### [user]++ : Grant a user " + str(self.karmaPerVote) + " " + self.karmaString + " for being awesome ### !top: Shows the top 5 " + self.karmaString + " earners "
		self.helpString = "*!setUpvoteAmount [amount]: Sets the number of monies granted by [user]++ ### *!setUpvoteDelay [seconds]: Sets how long you must wait between upvotes ### *!grant [target] [amount]: Grants target user x monies";
		pass
	
	def writeConf(self, sqli):
		sqli.writeToConfig(self.getName(), 'votedela', str(self.voteDelay))
		sqli.writeToConfig(self.getName(), 'kpervote', str(self.karmaPerVote))
		"""
		conf['money'] = {}
		conf['money']['fileName'] = self.fileName
		conf['money']['upvoteDelay'] = self.voteDelay
		conf['money']['moneyPerVote'] = self.karmaPerVote
		"""
		pass
	
	def readFromConf(self, sqli):
		self.voteDelay = int(sqli.readFromConfig(self.getName(), 'votedela', "600"))
		self.karmaPerVote = int(sqli.readFromConfig(self.getName(), 'kpervote', "1"))
		self.loadBankFile()
		"""
		if('money' in conf):
			self.fileName = conf['money']['fileName']
			self.voteDelay = conf['money']['upvoteDelay']
			self.karmaPerVote = conf['money']['moneyPerVote']
			self.loadBankFile()
		"""
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!bal') != -1 or lower.find('!pay ') == 0  or lower.find('!give ') == 0 or lower.find('!top') != -1:
			return True
		elif lower.find('++') != -1:
			return True;
		elif self.hb.isOp(user) == True:
			if lower.find('!grant ') == 0:
				return True
			if lower.find('!setupvoteamount ') == 0:
				return True
			if lower.find('!setupvotedelay ') == 0:
				return True
				
		return False
		
	def onMessage(self, msg, user):
		lower = msg.strip().lower()
		if lower.find('!top') != -1:
			sort = sorted(self.bank, key=lambda x: self.bank[x]['karma'], reverse=True)
			viewerOnly = lower.find('view') != -1
			output = ""
			index = 0
			for i in range(min(5,len(sort))):
				entry = self.bank[sort[index]]
				while(viewerOnly and index < len(sort) and self.hb.quickIsOp(entry['name'])):
					index += 1
					entry = self.bank[sort[index]]
				if viewerOnly and self.hb.quickIsOp(entry['name']):
					break;
				output += "#" + str(i+1) + ") " + entry['name'] + " with " + str(entry["karma"]) + " &nbsp; &nbsp; "
				index += 1
			self.hb.message(user + ": The top " + self.karmaString + " earners are &nbsp;" + output)
			pass
		elif lower.find('!bal') != -1:
			if len(self.hb.viewers) == 0:
				self.hb.message(user + ": Give me a sec, I just woke up!")
			else:
				self.hb.message(user + ": You currently have " + str(self.checkBalance(user)["money"]) + " " + self.moneyString + " and have earned " + str(self.checkBalance(user)["karma"]) + " " + self.karmaString + ".")
		elif lower.find('++') != -1:
			curTime = time.time()
			given = 0
			if (user in self.karmaTimer) == False or (self.karmaTimer[user]['points'] < self.karmaGiveLimit):
				split = lower.split(' ')
				for iter in range(0,len(split)):
					t = split[iter]
					name = ''
					if t == '++' and iter != 0: # In case its formatted "name ++" with a space
						name = split[iter-1]
					elif t.find('++') == (len(t)-2) and len(t) > 2: #Check if at end and not alone
						name = t[:-2]
					
					if (name.find('@') == 0):
						name = name[name.find('@')+1:]
					if(name.find('+') != -1):
						break;
					
					if name == user:
						self.hb.message(user + ": Narcissism can only get you so far!")
						break
					elif name != '' and self.checkBalance(name) != None:
						giveValid = True
						#
						if((user in self.karmaTimer) == False): # Not in the slowing tracker list
							self.karmaTimer[user] = {'time':curTime, 'points':1}
						elif(self.karmaTimer[user]['points'] < self.karmaGiveLimit): # Has not given their limit
							self.karmaTimer[user]['points'] += 1
						elif(curTime-self.karmaTimer[user]['time'] > self.voteDelay and given < self.karmaGiveLimit): # Has given their limit, but they've waited (and not gone over in this single string)
							self.karmaTimer[user] = {'time':curTime, 'points':1}
						else:
							giveValid = False
						
						if (giveValid == True):
							given += 1
							self.upvote(name, self.karmaPerVote)
						else:
							self.hb.message(user + ": You can only give out " + str(self.karmaGiveLimit) + " " + self.karmaString + " every " + str(self.voteDelay/1000) + " seconds!")
							pass
			if (given > 0):
				self.karmaTimer[user]['time'] = curTime
			pass
		elif lower.find('!pay ') == 0 or lower.find('!give ') == 0:
			split = msg.split(' ')
			if len(split) >= 3:
				amt = split[2]
				target = split[1].lower()
				if target == user:
					self.hb.message(user + ": You can't pay yourself!")
				else:
					try: 
						amount = int(amt)
						bal = self.checkBalance(user)["money"]
						if target.find('@') != -1:
							target = target[1:]

						if amount <= 0:
							self.hb.message(user + ": You must pay a positive amount!")
						elif amount > bal:
							self.hb.message(user + ": You don't have enough!")
						elif not (target in self.bank):
							self.hb.message(user + ": Target does not exist!")
						else:
							self.hb.message(user + ": Paying " + target + " " + str(amount) + " " + self.moneyString + ".")
							self.pay(target, amount)
							self.pay(user, -amount)
					except ValueError:
						pass

		if(self.hb.isOp(user) == True):
			if lower.find('!grant ') == 0:
				split = msg.split(' ')
				if len(split) >= 3:
					amt = split[2]
					target = split[1]
					try: 
						amount = int(amt)
						if self.checkUser(target) == False:
							self.hb.message(user + ": Target does not exist!")
						else:
							self.hb.message(user + ": Giving " + target + " " + str(amount) + " " + self.moneyString + ".")
							self.pay(target, amount)
					except ValueError:
						self.hb.message(user + ": Error giving money.")
						pass
			if lower.find('!setupvoteamount ') == 0:
				split = msg.split(' ')
				if len(split) >= 2:
					amt = split[1]
					try: 
						amount = int(amt)
						self.karmaPerVote = amount
						self.hb.message(user + ": Upvote amount set to " + str(amount))
						self.hb.saveSettings()
					except ValueError:
						self.hb.message(user + ": Error setting upvote amount.")
						pass
			if lower.find('!setupvotedelay ') == 0:
				split = msg.split(' ')
				if len(split) >= 2:
					amt = split[1]
					try: 
						amount = int(amt)
						self.voteDelay = amount
						self.hb.message(user + ": Upvote delay set to " + str(amount))
						self.hb.saveSettings()
					except ValueError:
						self.hb.message(user + ": Error setting upvote delay.")
						pass
		
	
	def checkBalance(self,user):
		self.loadBankFile()
		if(user.lower() in self.bank) == False: # and self.hb.isOnline(user) == True:
			print user + " not found, adding"
			self.bank[user.lower()] = {"money":0, "karma":0, "name":user}
			# self.saveBankFile()
			self.setBank(user.lower(), 0, 0)
		#elif self.hb.isOnline(user) == False:
		#	print user + " not online"
		#	return 0
		# print ("Derp " + str(user.lower() in self.bank))
		# print ("What " + str(self.bank))
		
		return self.bank[user.lower()]
	
	def setBank(self, user, money, karma):
		self.bank[user]["money"] = money
		self.bank[user]["karma"] = karma
		self.hb.sqli.writeKeyForUser('money', user.lower(), str(money))
		self.hb.sqli.writeKeyForUser('karma', user.lower(), str(karma))
	
	def loadBankFile(self):
		"""f = open(self.fileName,'r')
		self.bank = json.loads(f.read());
		f.close()"""
		self.bank = {}
		moneyList = self.hb.sqli.readAllUsersForKey('money')
		karmaList = self.hb.sqli.readAllUsersForKey('karma')
		klen = len(karmaList)
		# They should both be equal in length
		for i in range(0, len(moneyList)):
			moneyEntry = moneyList[i]
			name = moneyEntry[0]
			money = float(moneyEntry[1])
			
			if(not name in self.bank):
				self.bank[name] = {"money": 0, "karma": 0, "name": name}
			
			self.bank[name]["money"] = money
			
			if( i < klen ): # They should be equal but I've got trust issues
				karmaEntry = karmaList[i]
				name = karmaEntry[0]
				karma = float(karmaEntry[1])
				if(not name in self.bank):
					self.bank[name] = {"money": 0, "karma": 0, "name": name}
				self.bank[name]["karma"] = karma
	
	"""def saveBankFile(self):
		with open(self.fileName, 'w') as outfile: 
			json.dump(self.bank,outfile)""" # Ideally we should stay synced
	
	def checkUser(self,user):
		if(user.lower() in self.bank) == True:
			return True
		else:
			return False
		
	def pay(self, user, amount):
		if self.checkBalance(user) != None:
			self.setBank(user.lower(), self.bank[user.lower()]['money']+ amount, self.bank[user.lower()]['karma'])
			#self.saveBankFile()
	def upvote(self, user, amount):
		if self.checkBalance(user) != None:
			self.setBank(user.lower(), self.bank[user.lower()]['money'], self.bank[user.lower()]['karma'] + amount)
			#self.saveBankFile()
		
	def onJoin(self, user):
		self.checkBalance(user)
		
	def onStreamBegin(self):
		if(not self.streamThreadRunning):
			print("Starting money pay thread")
			self.streamThreadRunning = True
			self.streamThread = threading.Timer(self.payPerViewDelay,self.tickMoney)
			self.streamThread.start()
		pass
	
	def start(self):
		if(not self.streamThreadRunning):
			print("Starting money pay thread")
			self.streamThreadRunning = True
			self.streamThread = threading.Timer(self.payPerViewDelay,self.tickMoney)
			self.streamThread.start()
		pass

	def stop(self):
		if(self.streamThreadRunning):
			self.streamThread.cancel()
	
	def onStreamEnd(self):
		if(self.streamThreadRunning == True):
			self.streamThread.cancel()
			self.streamThreadRunning = False
	
	def tickMoney(self):
		streaming = self.hb.checkStreamOnline()
		print("Paying viewers " + str(streaming))
		# For all viewers, give monz
		if streaming == True:
			self.hb.checkViewers()
			for viewer in self.hb.viewers:
				self.pay(viewer,1)
		
		if(self.hb.stop == False and streaming == True):
			self.streamThread = threading.Timer(self.payPerViewDelay,self.tickMoney)
			self.streamThread.start()
		else:
			self.streamThread = None
			self.streamThreadRunning = False
		pass

'''
Free to use
Point Reward System
Drawing/Giveaway System
Balance Checking
Question Queuing
Greeting, Welcome Back, & Part/Quit Messages
Multiple Timed Advertisements
Custom Command Responses
Custom Greetings
Follower, Subscriber, and Donation Overlay Alerts
Chat Filter
Betting Games
Voting System
Fast & Friendly Support
'''