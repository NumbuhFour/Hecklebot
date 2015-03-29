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
from commands.info import Info
from commands.heckleme import Heckleme
from commands.greetFollowers import GreetFollowers
from commands.giveaway import Giveaway
from commands.money import Money
from commands.loyalty import Loyalty
from commands.followViewers import FollowViewers

true = True
false = False

class Hecklebot:
	bot_owner = 'Numbuhfour'
	streamer = 'misteratombomb'
	nick = 'Hecklebot'
	channel = '#misteratombomb'
	server = 'irc.twitch.tv'
	password = 'rawr';
	
	logFileName = 'log.txt'
	chatLogFileName = 'chatlog.txt'

	queue = 13

	conf = []

	oauthFile = ""
	
	commands = []
	
	stop = False
	
	def __init__(self):
		self.oauthFile = open('oauth.txt','r');
		self.password = self.oauthFile.read();
		self.oauthFile.close();
		
		self.initCommands()
		
		self.loadSettings()
		self.logfile = open(self.logFileName,'a')

		self.ops = []
		self.viewers = []

		self.stop = False

		self.log("Connecting...")

		self.irc = socket.socket()
		self.irc.connect((self.server,6667))

		self.irc.send('PASS oauth:' + self.password + '\r\n')
		self.irc.send('USER ' + self.nick + ' 0 * : ' + self.bot_owner + '\r\n')
		self.irc.send('NICK ' + self.nick + '\r\n')
		self.irc.send('JOIN ' + self.channel + '\r\n')

		self.log("Connected.")

		self.isStreaming = True
	
	def initCommands(self):
		self.money = Money(self)
		
		self.commands.append(Help(self))
		self.commands.append(Heckleme(self))
		self.commands.append(Koth(self))
		self.commands.append(GreetFollowers(self))
		self.commands.append(Giveaway(self))
		self.commands.append(self.money)
		self.commands.append(Loyalty(self))
		self.commands.append(FollowViewers(self))
		
		self.commands.append(Info(self)) #perhaps last will prevent it from overriding actual commands?
	
	def start(self):
		self.queuetimer()
		for c in self.commands:
			c.start() #Start threads (if applicable)

		try:
			self.run(self.conf)
		except KeyboardInterrupt:
			self.stop = True

		self.log("Quitting.")
			
		self.stop = True
		self.logfile.close()
		
	
	def loadSettings(self):
		f = open('heckle.config','r')
		
		self.conf = json.loads(f.read());
		self.streamer = self.conf['bot']['streamer']
		self.bot_owner = self.conf['bot']['owner']
		self.nick = self.conf['bot']['nick']
		self.channel = '#' + self.streamer.lower()
		self.server = self.conf['bot']['server']
		
		self.logFileName = self.conf['files']['log']
		self.chatLogFileName = self.conf['files']['chatlog']
		
		
		for c in self.commands:
			c.readFromConf(self.conf)
	
	def saveSettings(self):
		self.conf = { 'bot':{ 'owner':self.bot_owner, 'streamer':self.streamer, 'nick':self.nick, 'server':self.server }, 'files':{ 'log':self.logFileName, 'chatlog':self.chatLogFileName } }
		
		for c in self.commands:
			c.writeConf(self.conf)
		
		with open('heckle.config', 'w') as outfile: 
			json.dump(self.conf,outfile)
			


	def log(self,msg):
		time = datetime.datetime.now().strftime("[%m/%d/%Y %H:%M:%S]: ")
		self.logfile.write(time + msg + "\n")
		print time+msg
		

		

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
			self.log("HTTPError on fetch: "+ str(e) + " URL:" + str(url))
			return None
		except URLError as e:
			self.log("URLError on fetch: "+ str(e) + " URL:" + str(url))
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
				for c in self.commands:
					c.onStreamEnd()
			self.isStreaming = False
			return False
		if data['stream']:
			if self.isStreaming == False:
				self.writeToChatLog("**STREAM BEGIN**")
				for c in self.commands:
					c.onStreamBegin()
			self.isStreaming = True
			return True
		else:
			if self.isStreaming == True:
				self.writeToChatLog("**STREAM END**")
				for c in self.commands:
					c.onStreamEnd()
			self.isStreaming = False
			return False
		
	def checkOtherOnline(self, streamer):
		data = self.fetchJSON('https://api.twitch.tv/kraken/streams/' + streamer)
		if data == None:
			return False
		if data['stream']:
			return True
		else:
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

	def isOp(self, user):
		return user in self.ops or user.lower() == self.bot_owner.lower() or user.lower() == self.streamer.lower()
		
	def addViewer(self, user):
		self.writeToChatLog("**JOIN** " + user + " has joined.")
		if ~(user in self.viewers) and user != 'hecklebot':
			print("[off]: ADD USER " + user)
			self.viewers.append(user)
			for c in self.commands:
				c.onJoin(user)
		
	def remViewer(self, user):
		self.writeToChatLog("**PART** " + user + " has left.")
		if (user in self.viewers):
			print("[off]: REM USER " + user)
			self.viewers.remove(user)
			for c in self.commands:
				c.onPart(user)
	
	def isOnline(self,user):
		if (user in self.viewers): 
			return True
		return False
	
	def takeMessage(self, user, msg, conf):
		self.writeToChatLog(user + ": " + msg)
		
		lower = msg.lower()
		
		for cmd in self.commands:
			if cmd.checkMessage(msg,user) == True :
				cmd.onMessage(msg,user)
				return
				
				

	def handleMode(self, data):
		c = data.split(":jtv MODE " + self.channel + " ")[1]
		act = c.split(' ')[0].strip()
		user = c.split(' ')[1].strip()
		if act == '+o' and ~self.isOp(user) :
			self.log("Opping " + user)
			self.ops.append(user)
		elif act == '-o' and self.isOp(user):
			self.log("Deopping " + user)
			self.ops.remove(user)

	def run(self, conf):
		while True:
			incoming = self.irc.recv(1204)
			print incoming
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
