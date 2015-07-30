import socket
import threading
import thread
import datetime
from urllib2 import urlopen
import json
from random import randint
import time
from urllib2 import HTTPError
from urllib2 import URLError
import traceback
import sys

from sqlInterface import SQLInterface

from commands.koth import Koth
from commands.help import Help
from commands.info import Info
from commands.heckleme import Heckleme
from commands.greetFollowers import GreetFollowers
from commands.giveaway import Giveaway
from commands.money import Money
from commands.loyalty import Loyalty
from commands.followViewers import FollowViewers
from commands.evalCmd import EvalCMD
from commands.betting import Betting
from commands.gibberish import Gibberish

true = True
false = False

class Hecklebot:
	bot_owner = 'Numbuhfour'
	streamer = 'altaswolf'
	nick = 'AltasROWBot'
	channel = '#altaswolf'
	server = 'irc.twitch.tv'
	password = 'rawr';
	sqlpass = 'doop';
	
	logFileName = 'log.log'
	chatLogFileName = 'altaschatlog.txt'

	queue = 13

	conf = []

	oauthFile = ""
	
	commands = []
	disabledCommands = []
	
	stop = False
	
	doLog = False
	
	running = True
	
	threads = [None, None]
	
	debug = False
	
	sqli = None
	
	def __init__(self):
		oauthFile = open('oauth.txt','r');
		self.password = oauthFile.read();
		oauthFile.close();
		sqlfile = open('sql.txt','r');
		self.sqlpass = sqlfile.read();
		sqlfile.close();
		
		self.sqli = SQLInterface(self)
		self.sqli.checkStreamerConfig()
		
		self.initCommands()
		
		self.loadSettings()
		self.logfile = open(self.logFileName,'a')

		self.ops = []
		self.viewers = []

		self.stop = False

		if len(sys.argv) > 1 and sys.argv[1] == "debug":
			print "########## DEBUGGING ACTIVATED ##########"
			self.debug = True
			self.channel = "#" + self.bot_owner.lower()
		
		self.log("Connecting...")

		self.irc = socket.socket()
		self.irc.connect((self.server,6667))

		self.irc.send('PASS oauth:' + self.password + '\r\n')
		self.password = "doop"
		self.irc.send('USER ' + self.nick + ' 0 * : ' + self.bot_owner + '\r\n')
		self.irc.send('NICK ' + self.nick + '\r\n')
		self.irc.send('CAP REQ :twitch.tv/commands\r\n')
		self.irc.send('JOIN ' + self.channel + '\r\n')
		self.irc.send('JOIN #' + self.nick.lower() + '\r\n')

		self.log("Connected.")

		self.isStreaming = True
	
	def initCommands(self):
		self.info = Info(self)
		self.money = Money(self)
		self.commands.append(Help(self))
		self.commands.append(self.money)
		self.commands.append(Giveaway(self))
		self.commands.append(Betting(self))
		self.commands.append(EvalCMD(self))
		
		self.commands.append(self.info) #perhaps last will prevent it from overriding actual commands?
		self.commands.append(Gibberish(self))
	
	def start(self):
		self.queuetimer()
		for c in self.commands:
			c.start() #Start threads (if applicable)
			
		self.checkStreamTimer()

		thread.start_new_thread(self.readTerminal, ())
		
		self.checkViewers()
		try:
			self.run(self.conf)
		except KeyboardInterrupt:
			self.doStop()

		#self.log("Quitting.")
			
		self.stop = True
		self.logfile.close()
		
	def doStop(self):
		self.log("Stopping...")
		self.stop = True
		for c in self.commands:
			c.stop() #stop threads (if applicable)
		for th in self.threads:
			th.cancel()
		self.irc.shutdown(socket.SHUT_RDWR)
		self.irc.close()
		self.sqli.close()
	
	def loadSettings(self):
		# Bot config data will stay in file as
		# sql config depends on that data
		# specifically streamer
		f = open('heckle.config','r')
		
		self.conf = json.loads(f.read());
		self.streamer = self.conf['bot']['streamer']
		self.bot_owner = self.conf['bot']['owner']
		self.nick = self.conf['bot']['nick']
		self.channel = '#' + self.streamer.lower()
		self.server = self.conf['bot']['server']
		self.doLog = self.conf['bot']['log']
		
		self.logFileName = self.conf['files']['log']
		self.chatLogFileName = self.conf['files']['chatlog']
		
		for c in self.commands:
			c.readFromConf(self.sqli)
	
	def saveSettings(self):
		self.conf = { 'bot':{"log":self.doLog, 'owner':self.bot_owner, 'streamer':self.streamer, 'nick':self.nick, 'server':self.server }, 'files':{ 'log':self.logFileName, 'chatlog':self.chatLogFileName } }
		
		for c in self.commands:
			c.writeConf(self.sqli)
		
		with open('heckle.config', 'w') as outfile: 
			json.dump(self.conf,outfile)
			


	def log(self,msg):
		if(self.doLog):
			time = datetime.datetime.now().strftime("[%m/%d/%Y %H:%M:%S]: ")
			self.logfile.write(time + msg + "\n")
			print time+msg
		

		

	def writeToChatLog(self,msg):
		if(self.doLog):
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
		except Error as e:
			self.log("Unkown error: " + str(e) + " URL:" + str(url))
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

	def whisper(self,msg, target):
		tosend = 'PRIVMSG #jtv :/w ' + target + ' ' + msg + '\r\n'
		self.irc.send(tosend)
		self.log("WHISPERING: " + tosend)
		self.writeToChatLog('[whisper@' + target + '] ' + self.nick + ": " + msg)
		
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
			self.threads[0] = threading.Timer(10,self.queuetimer)
			self.threads[0].start()

	def checkStreamTimer(self):
		self.checkStreamOnline()
		if self.stop == False:
			self.threads[1] = threading.Timer(10, self.checkStreamTimer)
			self.threads[1].start()
		
	def isOp(self, user):
		self.checkViewers()
		return self.quickIsOp(user)
	
	def quickIsOp(self, user):
		return user in self.ops or user.lower() == self.bot_owner.lower() or user.lower() == self.nick.lower() or user.lower() == self.streamer.lower()
		
	def checkViewers(self):
		data = self.fetchJSON('https://tmi.twitch.tv/group/user/' + self.streamer + '/chatters')
		self.ops = []
		for name in data['chatters']['moderators']:
			if (isinstance(name,basestring)):
				self.ops.append(name)
				
		lastViewers = self.viewers
		self.viewers = []
		for name in data['chatters']['moderators']:
			if (isinstance(name,basestring)):
				self.viewers.append(name)
		for name in data['chatters']['staff']:
			if (isinstance(name,basestring)):
				self.viewers.append(name)
		for name in data['chatters']['admins']:
			if (isinstance(name,basestring)):
				self.viewers.append(name)
		for name in data['chatters']['global_mods']:
			if (isinstance(name,basestring)):
				self.viewers.append(name)
		for name in data['chatters']['viewers']:
			if (isinstance(name,basestring)):
				self.viewers.append(name)
		
		for name in lastViewers:
			if not(name in self.viewers):
				self.remViewer(name)
		for name in self.viewers:
			if not(name in lastViewers):
				self.addViewer(name)
	
	def addViewer(self, user):
		self.writeToChatLog("**JOIN** " + user + " has joined.")
		#if ~(user in self.viewers) and user != 'hecklebot':
		print("[off]: ADD USER " + user)
		#self.viewers.append(user)
		for c in self.commands:
			c.onJoin(user)
		
	def remViewer(self, user):
		self.writeToChatLog("**PART** " + user + " has left.")
		#if (user in self.viewers):
		print("[off]: REM USER " + user)
		#self.viewers.remove(user)
		for c in self.commands:
			c.onPart(user)
	
	def isOnline(self,user):
		self.checkViewers()
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
		while self.running:
			incoming = self.irc.recv(1204)
			print incoming
			for data in incoming.split('\n'):
				try:
					if len(data.strip()) == 0:
						continue
					if data.find('PONG') != -1:
						self.log(data)
					

					if data.find('PRIVMSG') != -1:
						message = data[data[2:].find(':')+3:] # Everything after the second :
						user = data.split(':')[1]
						user = user.split('!')[0]
						if(data.find('#' + self.nick.lower()) != -1 and user != 'numbuhfour'): 
							continue
						self.takeMessage(user, message, conf)
					elif data.find('WHISPER') != -1:
						print("WHISPER")
					elif data.find('PING') != -1:
						# self.log('PONG')
						self.irc.send(incoming.replace('PING','PONG')) #Responds to pings from server
						
					elif data.find('#' + self.nick.lower()) != -1:
						continue
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
				except:
					traceback.print_exc()
	def readTerminal(self):
		while(self.running):
			input = raw_input()
			if(input == "save"):
				self.saveSettings()
				self.log("Settings saved")
			elif(input == "exit"):
				self.running = False
				self.doStop()
				for th in self.threads :
					th.cancel()
			elif(input == "reload"):
				self.loadSettings()
				self.log("Settings reloaded")
			elif(input.find("say") == 0):
				self.message(input[4:])
			elif(input.find("whisper") == 0):
				split = input.split(" ")
				target = split[1]
				message = input[(len(target)+len("whisper")+2):]
				self.whisper(message,target)
			elif(input == "isonline"):
				print "Was " + str(self.isStreaming)
				print "Is now " + str(self.checkStreamOnline())
			elif(input.find("payall") == 0):
				split = input.split(" ")
				num = 1
				if(len(split) > 1):
					num = int(split[1])
				print("Paying everyone " + str(num))
				self.checkViewers()
				for viewer in self.viewers:
					self.money.pay(viewer,num)
			elif input.find("enable ") == 0:
				split = input.lower().split(' ')
				for i in range(1, len(split)):
					cmdName = split[i]
					found = False
					for cmd in self.disabledCommands:
						if(cmd.getName().lower() == cmdName):
							print "Enabling " + cmdName
							self.commands.append(cmd)
							self.disabledCommands.remove(cmd)
							found = True
							break
					if not found:
						print "Unable to enable " + cmdName
			elif input.find("disable ") == 0:
				split = input.lower().split(' ')
				for i in range(1, len(split)):
					cmdName = split[i]
					found = False
					for cmd in self.commands:
						if(cmd.getName().lower() == cmdName):
							print "Disabling " + cmdName
							self.disabledCommands.append(cmd)
							self.commands.remove(cmd)
							found = True
							break
					if not found:
						print "Unable to disable " + cmdName
			else:
				for cmd in self.commands:
					if cmd.onTerminalCommand(input) == True :
						break

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
