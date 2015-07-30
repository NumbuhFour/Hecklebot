from command import Command
from random import randint
import threading
import time
import json
import math

class Betting(Command):

	betRunning = False
	betClosed = False
	betQuestion = ""
	betters = {}
	bettingFile = "bets.txt"
	bettingThread = None
	pool = 0
	"""
	{
		"Option 1": { "billy":123 }
		"Option 2": []
		"Option 3": []
	}
	"""

	def __init__(self, hb):
		self.hb = hb
		if(hasattr(self.hb, 'money')):
			self.money = self.hb.money
		else:
			raise Exception("No money system loaded")
		self.helpString = "*!startBet [question]? [option1], [option2]...: Starts a bet ### *!cancelBet: Refunds all betters ### *!betWinner [winning option]: Names the winner of the bet ### *!closeBetting [seconds delay]: Close the betting in X seconds (default 0) ### !openBetting: Reopen a closed bet"
		self.publicHelpString = "!bet [choice] [bet]: Add yourself to the betting pool "
		pass
		
	def writeConf(self, sqli):
		sqli.writeToConfig(self.getName(), 'running', str(self.betRunning))
		sqli.writeToConfig(self.getName(), 'closed', str(self.betClosed))
		sqli.writeToConfig(self.getName(), 'question', str(self.betQuestion))
		sqli.writeToConfig(self.getName(), 'pool', str(self.pool))
		"""
		conf['betting'] = {}
		conf['betting']['bettingFile'] = self.bettingFile
		conf['betting']['betRunning'] = self.betRunning
		conf['betting']['betClosed'] = self.betClosed
		conf['betting']['betQuestion'] = self.betQuestion
		conf['betting']['pool'] = self.pool
		"""
		
		self.writeBetFile()
		pass
	
	def readFromConf(self, sqli):
		
		self.betRunning = sqli.readFromConfig(self.getName(), 'running', "False") == "True"
		self.betClosed = sqli.readFromConfig(self.getName(), 'closed', "False") == "True"
		self.betQuestion = sqli.readFromConfig(self.getName(), 'question', "")
		self.pool = int(sqli.readFromConfig(self.getName(), 'pool', "0"))
		"""
		if('betting' in conf):
			self.bettingFile = conf['betting']['bettingFile']
			self.betRunning = conf['betting']['betRunning']
			self.betClosed = conf['betting']['betClosed']
			self.betQuestion = conf['betting']['betQuestion']
			self.pool = conf['betting']['pool']
		else:
			self.bettingFile = "bets.txt"
			self.betRunning = False
			self.betClosed = False
			self.betQuestion = ""
			self.pool = 0
		"""
			
		self.readBetFile()
		pass
	
	def writeBetFile(self):
		for choice in self.betters:
			for name in self.betters[choice]:
				self.hb.sqli.writeKeyForUser("bet", name, str(choice) + ":" + str(self.betters[choice][name]))
		#with open(self.bettingFile, 'w') as outfile: 
		#	json.dump(self.betters,outfile)
		pass
		
	def readBetFile(self):
		rows = self.hb.sqli.readAllUsersForKey("bet")
		for r in rows:
			user = r[0]
			data = r[1].split(':')
			choice = data[0]
			bet = int(data[1])
			if not choice in self.betters:
				self.betters = {}
			
			self.betters[user] = bet
			
		"""f = open(self.bettingFile,'r')
		self.betters = json.loads(f.read());
		f.close()"""
	
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		isOp = self.hb.isOp(user)
		if lower.find('!bet') == 0:
			return True
			
		elif lower.find('!startbet ') == 0 and isOp == True:
			return True
		elif lower.find('!betwinner ') == 0 and isOp == True:
			return True
		elif lower.find('!cancelbet') == 0 and isOp == True:
			return True
		elif lower.find('!closebet') == 0 and isOp == True:
			return True
		elif lower.find('!openbet') == 0 and isOp == True:
			return True
		else:
			return False
		
	def onMessage(self, message, user):
		lower = message.strip().lower()
		if lower == "!bet":
			if not(self.betRunning):
				self.hb.message(user + ": There is no bet running!")
				return
			options = ""
			for opt in self.betters:
				options += opt + ", "
			options = options[:-2]
			self.hb.message(user + ': The current bet is "' + self.betQuestion + '" The options are' + options)
			
		elif lower.find('!bet ') == 0:
			if not(self.betRunning):
				self.hb.message(user + ": There is no bet running!")
				return
			if(self.betClosed):
				self.hb.message(user + ": Betting has been closed!")
				return
			choice = ""
			amount = ""
			split = lower.split(' ')
			amount = split[len(split)-1]
			choice = lower[ len('!bet '): -(len(amount)+1) ]
			amount = int(amount)
			print "Bet " + str(amount) + " " + choice
			currentChoice = self.checkUserInPool(user)
			if not(choice in self.betters):
				self.hb.message(user + ": " + choice + " is not an option in this bet!")
			elif(amount <= 0):
				self.hb.message(user + ": You must bet a positive amount!")
			elif(currentChoice != None):
				self.hb.message(user + ": You are already in the betting pool! You cannot change or leave now.")
			elif(self.money.checkBalance(user)["money"] < amount):
				self.hb.message(user + ": You don't have that many " + self.money.moneyString + "!")
			else:
				self.betters[choice][user] = amount
				self.money.pay(user,-amount)
				self.hb.message(user + ': You have bet ' + str(amount) + ' ' + self.money.moneyString + ' for "' + choice + '"')
				self.pool += amount
				self.hb.saveSettings()
			
		elif (lower.find('!startbet ') == 0):
			if(self.betRunning):
				self.hb.message(user + ": A bet is already running! Complete or cancel that first!")
				return
			
			qSplit = message.split('?')
			self.betQuestion = qSplit[0][len('!startbet '):].replace("I ", user + " ") + "?"
			self.betters = {}
			tempChoices = qSplit[1].split(',')
			if(len(qSplit) == 1 or qSplit[1].strip() == "" or len(tempChoices) == 1):
				self.hb.message(user + ": You must list more than 1 option!")
				return
			for c in tempChoices:
				if(c.strip().lower() in self.betters):
					self.hb.message(user + ": Duplicate option detected!")
					self.betters = {}
					self.betQuestion = ""
					return
				self.betters[c.strip().lower()] = {}
			self.betRunning = True
			self.betClosed = False
			
			self.hb.message('/me A bet begins for "' + self.betQuestion + '" The options are' + qSplit[1])
			self.hb.saveSettings()
			#parse question
			#parse options
			#populate betters dict
			#set running to true
			#print message
			#save bets
			
			#if unable to parse, print helpString
			#if bet already running, say so
			pass
		elif lower.find('!betwinner ') == 0:
			winner = lower[len('!betwinner '):]
			if not self.betRunning:
				self.hb.message(user + ': No bet is running!')
			if not (winner in self.betters):
				self.hb.message(user + ': "' + winner + '" is not a registered option.')
			else:
				
				if len(self.betters[winner]) == 0:
					self.hb.message('/me The winner option for the bet of "' + self.betQuestion + '" is ' + winner + ", but unfortunately no one bet for that! The " + self.money.moneyString + " vaporizes!")
				else:
					output = '/me The winner option for the bet of "' + self.betQuestion + '" is ' + winner + '. '
					for name in self.betters[winner]:
						self.pool -= self.betters[winner][name]
						self.money.pay(name, self.betters[winner][name])
					splitMoney = math.ceil(self.pool / len(self.betters[winner]))
					for name in self.betters[winner]:
						output += name + ", "
						self.money.pay(name, splitMoney)
					output = output[:-2] #remove comma
					output += " have won splitting the " + str(self.pool) + " " + self.money.moneyString
					self.hb.message(output)
				
				self.betters = {}
				self.betRunning = False
				self.betClosed = False
				self.betQuestion = ""
				self.pool = 0
				self.hb.saveSettings()
				if(self.bettingThread != None):
					self.bettingThread.cancel()
				self.bettingThread = None
				
			#parse winning option
			#if < 10 winners, print names and oreo pool
			#otherwise print number of winners and oreo pool
			#distribute winnings
			#clear betters dict
			#save dict
			
			#if no bet running, say so
			#if option not found, say so
			pass
		elif lower.find('!cancelbet') == 0:
			if not (self.betRunning):
				self.hb.message(user + ": No bet is running!")
			else:
				for choice in self.betters:
					for name in self.betters[choice]:
						self.money.pay(name, self.betters[choice][name])
				self.betters = {}
				self.betRunning = False
				self.betClosed = False
				self.betQuestion = ""
				self.pool = 0
				self.hb.saveSettings()
				if(self.bettingThread != None):
					self.bettingThread.cancel()
				self.bettingThread = None
				self.hb.message(user + ": Bet canceled!")
			#print "Bet has been canceled! All betters refunded"
			#clear bet array
			#save betters
			pass
		elif lower.find('!closebet') == 0:
			if not (self.betRunning):
				self.hb.message(user + ": No bet is running!")
			elif self.betClosed:
				self.hb.message(user + ": Bet is already closed!")
			if self.bettingThread != None:
				self.bettingThread.cancel()
				self.bettingThread = None
			split = lower.split(' ')
			if len(split) == 1:
				self.closeBetting(0)
			else:
				delay = int(split[1])
				self.closeBetting(delay)
			#if there is no bet running, say so
			#if bets are already closed, say so
			
			#if there is a numeric parameter, set that as closeTimeRemaining
				#close bet in closeTime
			#if there is not
			pass
		elif lower.find('!openbet') == 0:
			if not self.betRunning:
				self.hb.message(user + ": No bet currently running!")
			elif not self.betClosed:
				if self.bettingThread != None:
					self.bettingThread.cancel()
					self.hb.message(user + ": Bet closing has been canceled!")
				else:
					self.hb.message(user + ": The current bet isn't closed!")
			else:
				self.betClosed = False
				self.hb.message('/me Betting has been reopened for "' + self.betQuestion + '"')
			pass
		
	def checkUserInPool(self, user):
		user = user.lower()
		for option in self.betters:
			if(user in self.betters[option]):
				return option
		return None
	
	def closeBetting(self, delay):
		if delay == 0:
			self.doCloseBetting()
		else:
			self.hb.message('/me Get your last bets in! Betting for "' + self.betQuestion + '" will be closing in ' + str(delay) + ' seconds!')
			if(self.hb.stop == False):
				self.bettingThread = threading.Timer(delay,self.doCloseBetting)
				self.bettingThread.start()
		pass
		
	def doCloseBetting(self):
		self.betClosed = True
		self.bettingThread = None
		self.hb.message('/me Betting for "' + self.betQuestion + '" has closed! A winner will be named shortly. Probably.')
		pass
		
	def stop(self):
		if(self.bettingThread != None):
			self.bettingThread.cancel()
		pass