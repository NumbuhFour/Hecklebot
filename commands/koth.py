from command import Command
from random import randint
import time
class Koth(Command):
	koth = "numbuhfour"
	kothEnabled = True
	kothDelay = 2400
	kothFileName = "praises.txt"
	kothPraises = []
	kothTrack = {}
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "*!toggleKOTH: Toggles king of the hill ####### *!addPraise [praise]: Add a praise to the king! Use @user@ for name ######## *!setKOTHDelay [seconds]: Sets seconds between koth rolls";
		self.publicHelpString = "!koth: Roll to take the kingdom! 10 or more to win"
		pass
		
	def loadPraises(self):
		self.kothFile = open(self.kothFileName, 'r+')
		self.kothPraises = self.kothFile.read().split('\n')
		self.kothFile.close()
	
	def writeConf(self, conf):
		conf['koth'] = {}
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
		
		self.loadPraises()
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		
		if (lower.find('!koth') != -1 or lower.find('!kingofthehill') != -1 or lower.find('!kofth') != -1):
			return True
		if lower.find('!togglekoth') == 0:
			return True
			
		if lower.find('!addpraise ') == 0:
			return True
				
		if lower.find('!setkothdelay ') == 0:
			return True
		
	def onMessage(self, msg, user):
		lower = msg.strip().lower()
		if (lower.find('!koth') != -1 or lower.find('!kingofthehill') != -1 or lower.find('!kofth') != -1):
			if self.kothEnabled == True:
				self.checkKing(user)
			else:
				self.hb.message(user + ": The kingdom of the hill is currently under divine protection (disabled)")
		if self.hb.isOp(user):
			if lower.find('!togglekoth') == 0:
				if self.kothEnabled == False: #fucking pythons fucking scope bullshit fuck
					self.hb.message(user + ': King of the hill enabled')
					self.kothEnabled = True;
				else:
					self.hb.message(user + ': King of the hill disabled')
					self.kothEnabled = False;
				self.hb.saveSettings()
				
			if lower.find('!addpraise ') == 0:
				add = msg[11:]
				if len(add) > 0:
					self.hb.message(user + ": Adding praise [" + add.replace("@user@",user) + "]")
					self.addKothPraise(add)
					
			if lower.find('!setkothdelay ') == 0:
				try: 
					delay = int(msg[14:])
					
					self.kothDelay = delay;
					self.hb.message(user + ': KOTH delay set to ' + str(delay) + ' seconds.')
					self.hb.saveSettings()
				except ValueError:
					self.hb.message(user + ": Error.")
					pass

			
	def praiseKing(self, user):
		praise = self.kothPraises[randint(0,len(self.kothPraises)-1)]
		return praise.replace("@user@", user)

	def checkKing(self, user):
		if self.hb.isStreaming == False:
			self.hb.message(user + ": The hill is protected while the stream is offline!")
			return
		
		userTime = 0
		if user in self.kothTrack:
			userTime = self.kothTrack[user]
		
		curTime = round(time.time()) 
		if (curTime-userTime) > self.kothDelay:
			if user == self.koth.lower(): #Already king
				self.hb.message(user + ": " + self.praiseKing(self.koth))
				return
			
			roll = randint(1,6) + randint(1,6)
			if roll >= 10: #Victory
				self.hb.message(user + ": You rolled a " + str(roll) + ", claiming victory over " + self.koth + ". " + self.praiseKing(user))
				self.koth = user
				self.hb.saveSettings()
			else: #Failure
				self.hb.message(user + ": You rolled a " + str(roll) + ", failing to win. " + self.praiseKing(self.koth))
				
			self.kothTrack[user] = curTime
		else:
			self.hb.message(user + ": Your troops are still regrouping! They need " + str(self.kothDelay - (curTime - userTime)) + " more seconds!")
		
	def addKothPraise(self, praise):
		self.hb.log("Adding praise: " + praise)
		self.loadPraises()
		
		self.kothPraises.append(praise)
		self.kothFile= open(self.kothFileName,'r+')
		self.kothFile.seek(0,2) #go to end
		self.kothFile.write("\n" + praise)
		self.kothFile.close() #refreshing list