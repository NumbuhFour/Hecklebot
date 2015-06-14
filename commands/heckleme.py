from command import Command
import threading
from random import randint
class Heckleme(Command):
	heckleFileName = 'heckles.txt'
	heckleTimer = 60*40 #How often to auto heckle
	
	heckles = []
	
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "*!addHeckle [heckle]: Add a heckle ### *!refreshHeckles: Refreshes heckles from file ### !setHeckleTimer [minutes]: Sets delay for the auto-heckle";
		self.publicHelpString = "!heckleme: Treats your masochistic desires"
		self.heckleTimerCountdown = 0
		
	def start(self):
		self.autoHeckle()
		
	def writeConf(self, conf):
		conf["heckle"] = {'heckles':self.heckleFileName,'heckleTimer':self.heckleTimer}
	
	def readFromConf(self, conf):
		self.heckleFileName = conf['heckle']['heckles']
		self.heckleTimer = conf['heckle']['heckleTimer']
		
		self.loadHeckles()
		
	def loadHeckles(self):
		self.heckleFile = open(self.heckleFileName, 'r')
		input = self.heckleFile.read()
		self.heckles = input.split('\n')
		self.heckleFile.close()
	
	def saveHeckles(self):
		self.heckleFile = open(self.heckleFileName,'w')
		for i in range(0, len(self.heckles)):
			toWrite = self.heckles[i]
			if i != (len(self.heckles)-1):
				toWrite += "\n"
			self.heckleFile.write(toWrite)
		self.heckleFile.close()
	
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!heckleme') != -1 or lower.find('!heckelme') != -1 or lower.find('!hecklebot') != -1: #Heckle time!
			return True
		elif self.hb.isOp(user):
			if lower.find('!addheckle ') == 0: #Adding a heckle!
				return True
						
			if lower.find('!refreshheckles') == 0:
				return True
				
			if lower.find('!setheckletimer ') == 0:
				return True
				
		return False
		
	def onMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!heckleme') != -1 or lower.find('!heckelme') != -1 or lower.find('!hecklebot') != -1: #Heckle time!
			self.sendHeckle(user)
			
		if self.hb.isOp(user):
			if lower.find('!addheckle ') == 0: #Adding a heckle!
				heckle = message[11:].strip() #cut the !addheckle
				#print "DERP|" + heckle + "|" + str(len(heckle))
				if len(heckle) > 0:
					self.hb.message(user + ": Adding heckle [" + heckle + "]")
					self.addHeckle(heckle)
				#return
						
			if lower.find('!refreshheckles') == 0:
				self.hb.message(user + ": Heckle file refreshed!")
				self.loadHeckles()
				#return
				
			if lower.find('!setheckletimer ') == 0:
				try: 
					count = int(message[16:])
					self.heckleTimer = count*60
					self.heckleTimerCountdown = self.heckleTimer
					self.hb.message(user + ': Auto-heckle timer set to ' + str(count) + ' minutes.')
					self.hb.saveSettings()
				except ValueError:
					self.hb.message(user + ": Error.")
					pass
				#return
		
	
	def sendHeckle(self, user):
		heckle = self.heckles[randint(0,len(self.heckles)-1)]
		self.hb.message(user + ": " + heckle)
		
	def addHeckle(self,heckle):
		self.hb.log("Adding heckle: " + heckle)
		self.loadHeckles()
		self.heckles.append(heckle)
		self.saveHeckles()

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