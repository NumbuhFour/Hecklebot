import socket
import threading
import datetime
from urllib2 import urlopen
import json
from random import randint
import time
from urllib2 import HTTPError
from urllib2 import URLError

from commands.koth import Koth
from commands.help import Help

class Hecklebot:
	bot_owner = 'Numbuhfour'
	streamer = 'misteratombomb'
	nick = 'Hecklebot'
	channel = '#misteratombomb'
	server = 'irc.twitch.tv'
	password = 'rawr';
	
	heckleFileName = 'heckles.txt'
	logFileName = 'log.txt'
	infoFileName = 'info.txt'
	kothFileName = 'kothPraises.txt'
	chatLogFileName = 'chatlog.txt'
	
	greetNewFollower = True
	greetedFollowers = []
	followerWelcomeMessage = 'Welcome, {}, to the hoard of hecklers!'

	koth = "numbuhfour"
	kothEnabled = True
	kothDelay = 15

	queue = 13

	heckleTimer = 60*40 #How often to auto heckle

	conf = []

	oauthFile = ""
	
	commands = []
	
	def __init__(self):
		self.oauthFile = open('oauth.txt','r');
		self.password = self.oauthFile.read();
		self.oauthFile.close();
		
		self.loadSettings()
		self.logfile = open(self.logFileName,'a')
		
		self.heckleFile = open(self.heckleFileName, 'r+')
		self.heckles = self.heckleFile.read().split('\n')
		self.heckleFile.close()

		self.kothFile = open(self.kothFileName, 'r+')
		self.kothPraises = self.kothFile.read().split('\n')
		self.kothFile.close()

		self.ops = []
		self.viewers = []
		self.infocmds = []
		self.kothTrack = {} #tracking last koth

		self.stop = False

		self.log("Connecting...")

		self.irc = socket.socket()
		self.irc.connect((self.server,6667))

		self.irc.send('PASS ' + self.password + '\r\n')
		self.irc.send('USER ' + self.nick + ' 0 * : ' + self.bot_owner + '\r\n')
		self.irc.send('NICK ' + self.nick + '\r\n')
		self.irc.send('JOIN ' + self.channel + '\r\n')

		self.log("Connected.")

		self.isStreaming = True
		
		self.loadInfo()
		self.initCommands()
	
	def initCommands(self):
		self.commands.append(Help(self))
	
	def start(self):
		self.queuetimer()
		self.followerCheckTimer()
		self.heckleTimerCountdown = 0
		self.autoHeckle()

		try:
			self.run(self.conf)
		except KeyboardInterrupt:
			self.stop = True

		self.log("Quitting.")
			
		self.stop = True
		self.logfile.close()
		self.heckleFile.close()
		self.kothFile.close()
		
	
	def loadSettings(self):
		f = open('heckle.config','r')
		
		self.conf = json.loads(f.read());
		self.streamer = self.conf['bot']['streamer']
		self.bot_owner = self.conf['bot']['owner']
		self.nick = self.conf['bot']['nick']
		self.channel = '#' + self.streamer
		self.server = self.conf['bot']['server']
		
		self.heckleFileName = self.conf['files']['heckles']
		self.logFileName = self.conf['files']['log']
		self.infoFileName = self.conf['files']['info']
		self.chatLogFileName = self.conf['files']['chatlog']
		
		self.greetNewFollower = self.conf['greet']['greetNewFollower']
		self.followerWelcomeMessage = self.conf['greet']['followerWelcomeMessage']
		
		self.koth = self.conf['koth']['king']
		self.kothEnabled = self.conf['koth']['enabled']
		self.kothDelay = self.conf['koth']['kothDelay']
		self.kothFileName = self.conf['koth']['fileName']
		
		self.heckleTimer = self.conf['heckleTimer']
	
	def saveSettings(self):
		self.conf = { 'bot':{ 'owner':self.bot_owner, 'streamer':self.streamer, 'nick':self.nick, 'server':self.server }, 'files':{ 'heckles':self.heckleFileName, 'log':self.logFileName, 'info':self.infoFileName, 'chatlog':self.chatLogFileName }, 'greet':{ 'greetNewFollower':self.greetNewFollower, 'followerWelcomeMessage':self.followerWelcomeMessage }, 'heckleTimer':self.heckleTimer, 'koth':{'king':self.koth,'enabled':self.kothEnabled, 'kothDelay':self.kothDelay, 'fileName':self.kothFileName} }
		
		with open('heckle.config', 'w') as outfile: 
			json.dump(conf,outfile)
			


	def log(self,msg):
		time = datetime.datetime.now().strftime("[%m/%d/%Y %H:%M:%S]: ")
		self.logfile.write(time + msg + "\n")
		print time+msg
		

	def loadInfo(self):
		f = open(self.infoFileName, 'r')
		self.infocmds = json.loads(f.read());
		f.close();
		print('loading Info ' + str(self.infocmds))

	def saveInfo(self):
		with open(self.infoFileName, 'w') as outfile: 
			json.dump(self.infocmds,outfile)
			outfile.close()
		

	def writeToChatLog(self,msg):
		chatfile = open(self.chatLogFileName,'a')
		time = datetime.datetime.now().strftime("[%m/%d/%Y %H:%M:%S]: ")
		chatfile.write(time + msg + "<br />")
		chatfile.close()

	def fetchJSON(self, url):
		try:
			res = urlopen(url)
			data = json.loads(res.read())
			return data
		except HTTPError as e:
			log("HTTPError on fetch: "+ str(e) + " URL:" + str(url))
			return None
		except URLError as e:
			log("URLError on fetch: "+ str(e) + " URL:" + str(url))
			return None
		return None

	def message(self, msg): #function for sending messages to the IRC chat
		self.queue = self.queue + 1
		print self.queue
		if self.queue < 20: #ensures does not send >20 msgs per 30 seconds.
			tosend = 'PRIVMSG ' + self.channel + ' :' + msg + '\r\n'
			self.irc.send(tosend)
			self.log("SENDING: " + tosend)
			self.writeToChatLog(self.nick + ": " + msg)
		else:
			self.log("Queue overflow. [" + msg + "] ignored.")

	def checkStreamOnline(self):
		data = self.fetchJSON('https://api.twitch.tv/kraken/streams/' + self.streamer)
		if data == None:
			if self.isStreaming == True:
				self.writeToChatLog("**STREAM END**")
			self.isStreaming = False
			return False
		if data['stream']:
			if self.isStreaming == False:
				self.writeToChatLog("**STREAM BEGIN**")
			self.isStreaming = True
			return True
		else:
			self.isStreaming = False
			return False
		
	def getFollowers(self):
		i = 0
		count = 1
		getfollowers = []
		attempts = 0
		while True:
			self.log("Follower Fetch Attempt: " + str(attempts))
			attempts += 1
			
			data = self.fetchJSON('https://api.twitch.tv/kraken/channels/' + self.streamer + '/follows?direction=DESC&limit=100&offset=' + str(i))
			if data==None:
				return None
			
			count = data['_total']
			
			for follower in data['follows']:
				name = follower['user']['display_name'].strip()
				getfollowers.append(name)
			
			if i > count:
				break;
			i += 100;
			time.sleep(2)

		self.log('Follower Recieved Count: ' + str(len(getfollowers)))
		return getfollowers
		
	def getSubscribers(self):
		i = 0
		count = 1
		getsubscribers = []
		attempts = 0
		while True:
			self.log("Subscriber Fetch Attempt: " + str(attempts))
			attempts += 1
			
			data = self.fetchJSON('https://api.twitch.tv/kraken/channels/' + self.streamer + '/subscriptions?direction=DESC&limit=100&offset=' + str(i))
			if data == None:
				return None
			count = data['_total']
			
			for sub in data['subscriptions']:
				name = sub['user']['display_name'].strip()
				getsubscribers.append(name)
			
			if i > count:
				break;
			i += 100;
			time.sleep(2)

		self.log('Subscriber Recieved Count: ' + str(len(getsubscribers)))
		return getsubscribers
		
	def queuetimer(self): #function for resetting the queue every 30 seconds and reloading log
		
		self.logfile.close()
		self.logfile = open(self.logFileName,'a')
		
		self.queue = 0
		if self.stop == False:
			threading.Timer(10,self.queuetimer).start()

	def followerCheckTimer(self): #function for checking for a new follower every 2 seconds
		if self.stop == False:
			threading.Timer(10,self.followerCheckTimer).start()
		else:
			return
		if self.checkStreamOnline() == True:
			if self.greetNewFollower == True:
				if len(self.greetedFollowers) == 0:
					self.greetedFollowers = getFollowers()
					print('Greeted followers list refreshed. ' + str(len(self.greetedFollowers)))
				else:
					data = self.fetchJSON('https://api.twitch.tv/kraken/channels/' + self.streamer + '/follows?direction=DESC&limit=15&offset=0')
					if data == None:
						return
					fols = data['follows']
					for user in fols:
						name = user['user']['display_name'].strip()
						if (name in self.greetedFollowers) == False:
							message(self.followerWelcomeMessage.replace("@user@",name))
							self.greetedFollowers.append(name)

	def sendHeckle(self, user):
		heckle = self.heckles[randint(0,len(self.heckles)-1)]
		self.message(user + ": " + heckle)
		
	def addHeckle(self,heckle):
		self.log("Adding heckle: " + heckle)
		self.heckles.append(heckle)
		self.heckleFile = open(self.heckleFileName,'r+')
		self.heckleFile.seek(0,2) #go to end
		self.heckleFile.write("\n" + heckle)
		
		self.heckleFile.close() #refreshing list
		self.heckleFile = open(self.heckleFileName, 'r+')
		self.heckles = self.heckleFile.read().split('\n')
		self.heckleFile.close() #refreshing list
		
	def addKothPraise(self, praise):
		self.log("Adding praise: " + praise)
		
		self.kothPraises.append(praise)
		self.kothFile= open(self.kothFileName,'r+')
		self.kothFile.seek(0,2) #go to end
		self.kothFile.write("\n" + praise)
		
		self.kothFile.close() #refreshing list
		self.kothFile = open(self.kothFileName, 'r+')
		self.kothPraises = self.kothFile.read().split('\n')
		self.kothFile.close() #refreshing list
		
	def refreshHeckles(self):
		self.log("Heckle list refreshed")
		self.heckleFile = open(self.heckleFileName, 'r+')
		self.heckles = self.heckleFile.read().split('\n')
		self.heckleFile.close() #refreshing list
		
		self.kothFile = open(self.kothFileName, 'r+')
		self.kothPraises = self.kothFile.read().split('\n')
		self.kothFile.close() #refreshing list

	def autoHeckle(self): #auto heckles
		if self.stop == False:
			threading.Timer(10, self.autoHeckle).start()
		else:
			return
			
		self.heckleTimerCountdown -= 10
		if(self.heckleTimerCountdown <= 0):
			if self.checkStreamOnline() == True:
				self.sendHeckle(self.streamer)
			self.heckleTimerCountdown = self.heckleTimer

	def isOp(self, user):
		return user in self.ops or user.lower() == self.bot_owner.lower() or user.lower() == self.streamer.lower()
		
	def addViewer(self, user):
		self.writeToChatLog("**JOIN** " + user + " has joined.")
		if ~(user in self.viewers) and user != 'hecklebot':
			print("[off]: ADD USER " + user)
			self.viewers.append(user)
		
	def remViewer(self, user):
		writeToChatLog("**PART** " + user + " has left.")
		if (user in self.viewers):
			print("[off]: REM USER " + user)
			self.viewers.remove(user)

			
	def praiseKing(self, user):
		praise = self.kothPraises[randint(0,len(self.kothPraises)-1)]
		return praise.replace("@user@", user)

	def checkKing(self, user):
		if self.isStreaming == False:
			self.message(user + ": The hill is protected while the stream is offline!")
			return
		
		userTime = 0
		if user in self.kothTrack:
			userTime = self.kothTrack[user]
		
		curTime = round(time.time())
		if (curTime-userTime) > self.kothDelay:
			if user == self.koth.lower(self): #Already king
				self.message(user + ": " + self.praiseKing(koth))
				return
			
			roll = randint(1,12)
			if roll >= 10: #Victory
				message(user + ": You rolled a " + str(roll) + ", claiming victory over " + self.koth + ". " + self.praiseKing(user))
				self.koth = user
				self.saveSettings()
			else: #Failure
				self.message(user + ": You rolled a " + str(roll) + ", failing to win. " + self.praiseKing(koth))
		self.kothTrack[user] = curTime

		
	def takeMessage(self, user, msg, conf):
		self.writeToChatLog(user + ": " + msg)
		
		lower = msg.lower()
		
		self.log("Test cmd len " + str(len(self.commands)))
		for cmd in self.commands:
			if cmd.checkMessage(msg,user) == True :
				self.log("CMD WORK")
				cmd.onMessage(msg,user)
				return
		
		if lower.find('!heckleme') != -1 or lower.find('!heckelme') != -1 or lower.find('!hecklebot') != -1: #Heckle time!
			self.sendHeckle(user)
			#return
		
		elif self.kothEnabled == True and (lower.find('!koth') != -1 or lower.find('!kingofthehill') != -1 or lower.find('!kofth') != -1):
			self.checkKing(user)
			
		elif lower.find('!') == 0:
			#print('Cockmonkeys')
			for key in self.infocmds:
				#print('Checking command ' + key)
				if lower.find('!' + key) == 0:
					self.message(user + ': ' + self.infocmds[key].replace("@user@",user))
					#return
					
		#print "RAWR "+ lower + " || " + str(lower.find('!addheckle')) + "|" + str(isOp(user))
		#print ops
		
		if self.isOp(user): #OP only commands
			if lower.find('!heslp') == 0: 
				self.message(user + ': !addHeckle [heckle]: Add a heckle ######### ' + '!refreshHeckles: Refreshes heckles from file ######### ' + '!giveaway [viewers] [followers] [subscribers]: Pick a person for the giveaway ######### ' + '!greetFollower: Toggle welcoming new followers ######### ' + '!setFollowerWelcome [message with @user@ for name]: Sets welcome message for new followers ######### ' + '!setHeckleTimer [minutes]: Sets delay for the auto-heckle ######### ' + '!addInfo [cmd] [message]: Adds a FAQ message to auto-respond to ######### ' + '!removeInfo [cmd]: Removes a FAQ message ######### ' + '!toggleKOTH : Toggles king of the hill ######### ' + '!addPraise [praise]: Adds a praise to the king! User @user@ for name ######### ' + '!setKOTHDelay [seconds]: Sets seconds between koth rolls')
				#return
			
			if lower.find('!addheckle ') == 0: #Adding a heckle!
				heckle = msg[11:].strip() #cut the !addheckle
				#print "DERP|" + heckle + "|" + str(len(heckle))
				if len(heckle) > 0:
					self.message(user + ": Adding heckle [" + heckle + "]")
					self.addHeckle(heckle)
				#return
						
			if lower.find('!refreshheckles') == 0:
				self.message(user + ": Heckle file refreshed!")
				rself.efreshHeckles()
				#return
				
			if lower.find('!giveaway ') == 0:
				pool = []
				if lower.find('followers') != -1:
					fol = self.getFollowers()
					if fol == None:
						self.message(user + ": Error fetching followers. Try again in a bit.")
						return
					pool += fol
				if lower.find('viewers') != -1:
					pool += self.viewers
				if lower.find('subscribers') != -1:
					sub = self.getSubscribers()
					if sub == None:
						self.message(user + ": Error fetching followers. Try again in a bit.")
						return
					pool += sub
				pool = list(set(pool)) #remove duplicates
				print pool
				self.message("{0}: And the winner is...... {1}!".format(user, pool[randint(0,len(pool)-1)]))
				#return
				
			if lower.find('!greetfollower') == 0:
				#message(user + ': I WILL ALWAYS GREET FOLLOWERS YOU CANT CHANGE THAT BECAUSE FUCK PYTHON')
				if self.greetNewFollower == False: #fucking pythons fucking scope bullshit fuck
					self.message(user + ': Greeting new followers')
					self.greetNewFollower = True;
				else:
					self.message(user + ': Not greeting new followers')
					self.greetNewFollower = False;
				self.saveSettings()
				#return
				
			if lower.find('!setfollowerwelcome ') == 0:
				welcome = msg[20:] #cut the !setfollowerwelcome
				#followerWelcomeMessage = welcome.replace('NAME', '{}')
				self.message(user + ': Follower welcome message changed to [' + self.followerWelcomeMessage.replace("@user@", user) + ']')
				self.saveSettings()
				#return
				
			if lower.find('!setheckletimer ') == 0:
				count = int(msg[16:])
				self.heckleTimer = count*60
				self.heckleTimerCountdown = self.heckleTimer
				message(user + ': Auto-heckle timer set to ' + str(count) + ' minutes.')
				self.saveSettings()
				#return
			
			if lower.find('!addinfo ') == 0:
				split = msg.split(' ')
				cmd = split[1]
				inf = msg[msg.find(cmd)+len(cmd)+1:]
				cmd = cmd.lower()
				self.infocmds[cmd] = inf
				self.message(user + ": Now responding to !" + cmd + " with [" + inf + "]")
				self.saveInfo()
				
			if lower.find('!removeinfo ') == 0:
				split = msg.split(' ')
				cmd = split[1].lower().strip()
				del self.infocmds[cmd]
				self.saveInfo()
				self.message(user + ": No longer responding to !" + cmd)
			
			if lower.find('!togglekoth') == 0:
				if self.kothEnabled == False: #fucking pythons fucking scope bullshit fuck
					self.message(user + ': King of the hill enabled')
					self.kothEnabled = True;
				else:
					self.message(user + ': King of the hill disabled')
					self.kothEnabled = False;
				self.saveSettings()
				
			if lower.find('!addpraise ') == 0:
				add = msg[11:]
				if len(add) > 0:
					self.message(user + ": Adding praise [" + add.replace("@user@",user) + "]")
					self.addKothPraise(add)
					
			if lower.find('!setkothdelay ') == 0:
				delay = int(msg[14:])
				
				self.kothDelay = delay;
				self.message(user + ': KOTH delay set to ' + str(delay) + ' seconds.')
				self.saveSettings()
				
				

	def handleMode(self, data):
		c = data.split(":jtv MODE " + self.channel + " ")[1]
		act = c.split(' ')[0].strip()
		user = c.split(' ')[1].strip()
		if act == '+o' and ~self.isOp(user) :
			self.log("Opping " + user)
			self.ops.append(user)
		elif act == '-o' and self.isOp(user):
			log("Deopping " + user)
			self.ops.remove(user)

	def run(self, conf):
		while True:
			incoming = self.irc.recv(1204)
			for data in incoming.split('\n'):
				if len(data.strip()) == 0:
					continue
				self.log(data)
				

				if data.find('PRIVMSG') != -1:
					message = data.split(':')[2]
					user = data.split(':')[1]
					user = user.split('!')[0]
					self.takeMessage(user, message, conf)
				
				elif data.find('PING') != -1:
					self.log('PONG')
					self.irc.send(incoming.replace('PING','PONG')) #Responds to pings from server
				
				elif data.find('MODE') != -1: #Someone is  being opped or deopped
					try:
						self.handleMode(data)
					except ValueError:
						self.message(user + ": Invalid input")
					
				elif data.find('PART') != -1: #Someone leaves
					user = data.split(':')[1]
					user = user.split('!')[0]
					self.remViewer(user)
				elif data.find('JOIN') != -1: #Someone joins
					user = data.split(':')[1]
					user = user.split('!')[0]
					self.addViewer(user)
							
				elif data.find('353') != -1: #User listing:
					list = data.split(':')[2]
					for name in list.split(' '):
						self.addViewer(name.strip()) #Get username

hb = Hecklebot()
hb.start()

'''
try:
	main(conf)
except KeyboardInterrupt:
	stop = True

log("Quitting.")
	
stop = True
logfile.close()
heckleFile.close()
kothFile.close()'''


'''
	TODO
	add an addInfo command for adding random informational commands
	optimize api checks (namely stream-online)
'''
