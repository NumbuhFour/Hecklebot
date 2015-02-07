import socket
import threading
import datetime
from urllib2 import urlopen
import json
from random import randint
import time
from urllib2 import HTTPError

bot_owner = 'Numbuhfour'
streamer = 'misteratombomb'
nick = 'Hecklebot'
channel = '#misteratombomb'
server = 'irc.twitch.tv'
password = 'oauth:igsxawqpsklid3ecclq7gmfgzrl9u4'

heckleFileName = 'heckles.txt'
logFileName = 'log.txt'
infoFileName = 'info.txt'
kothFileName = 'kothPraises.txt'

greetNewFollower = True
greetedFollowers = []
followerWelcomeMessage = 'Welcome, {}, to the hoard of hecklers!'

koth = "numbuhfour"
kothEnabled = True
kothDelay = 15

queue = 13

heckleTimer = 60*40 #How often to auto heckle

conf = []

def loadSettings():
	f = open('heckle.config','r')
	global conf
	global streamer
	global bot_owner
	global nick
	global channel
	global server
	global password
	global heckleFileName
	global logFileName
	global infoFileName
	global greetNewFollower
	global followerWelcomeMessage
	global koth
	global kothEnabled
	global kothDelay
	global kothFileName
	global heckleTimer
	
	conf = json.loads(f.read());
	streamer = conf['bot']['streamer']
	bot_owner = conf['bot']['owner']
	nick = conf['bot']['nick']
	channel = '#' + streamer
	server = conf['bot']['server']
	password = conf['bot']['password']
	
	heckleFileName = conf['files']['heckles']
	logFileName = conf['files']['log']
	infoFileName = conf['files']['info']
	
	greetNewFollower = conf['greet']['greetNewFollower']
	followerWelcomeMessage = conf['greet']['followerWelcomeMessage']
	
	koth = conf['koth']['king']
	kothEnabled = conf['koth']['enabled']
	kothDelay = conf['koth']['kothDelay']
	kothFileName = conf['koth']['fileName']
	
	heckleTimer = conf['heckleTimer']
	
def saveSettings():
	conf = { 'bot':{ 'owner':bot_owner, 'streamer':streamer, 'nick':nick, 'server':server, 'password':password }, 'files':{ 'heckles':heckleFileName, 'log':logFileName, 'info':infoFileName }, 'greet':{ 'greetNewFollower':greetNewFollower, 'followerWelcomeMessage':followerWelcomeMessage }, 'heckleTimer':heckleTimer, 'koth':{'king':koth,'enabled':kothEnabled, 'kothDelay':kothDelay, 'fileName':kothFileName} }
	
	with open('heckle.config', 'w') as outfile: 
		json.dump(conf,outfile)
		
loadSettings()


logfile = open(logFileName,'a')
def log(msg):
	time = datetime.datetime.now().strftime("[%m/%d/%Y %H:%M:%S]: ")
	logfile.write(time + msg + "\n")
	print time+msg
	
heckleFile = open(heckleFileName, 'r+')
heckles = heckleFile.read().split('\n')
heckleFile.close()

kothFile = open(kothFileName, 'r+')
kothPraises = kothFile.read().split('\n')
kothFile.close()

ops = []
viewers = []
infocmds = []
kothTrack = {} #tracking last koth

stop = False

log("Connecting...")

irc = socket.socket()
irc.connect((server,6667))

irc.send('PASS ' + password + '\r\n')
irc.send('USER ' + nick + ' 0 * : ' + bot_owner + '\r\n')
irc.send('NICK ' + nick + '\r\n')
irc.send('JOIN ' + channel + '\r\n')

log("Connected.")

isStreaming = True

def loadInfo():
	global infocmds
	f = open(infoFileName, 'r')
	infocmds = json.loads(f.read());
	f.close();
	print('loading Info ' + str(infocmds))

def saveInfo():
	global infocmds
	with open(infoFileName, 'w') as outfile: 
		json.dump(infocmds,outfile)
		outfile.close()
	
loadInfo()

def fetchJSON(url):
	try:
		res = urlopen(url)
		data = json.loads(res.read())
		return data
	except HTTPError as e:
		log("HTTPError on fetch: "+ str(e))
		return None
	except URLError as e:
		log("URLError on fetch: "+ str(e))
		return None
	return None

def message(msg): #function for sending messages to the IRC chat
	global queue
	queue = queue + 1
	print queue
	if queue < 20: #ensures does not send >20 msgs per 30 seconds.
		tosend = 'PRIVMSG ' + channel + ' :' + msg + '\r\n'
		irc.send(tosend)
		log("SENDING: " + tosend)
	else:
		log("Queue overflow. [" + msg + "] ignored.")

def checkStreamOnline():
	data = fetchJSON('https://api.twitch.tv/kraken/streams/' + streamer)
	if data == None:
		isStreaming = False
		return False
	if data['stream']:
		isStreaming = True
		return True
	else:
		isStreaming = False
		return False
	
def getFollowers():
	i = 0
	count = 1
	getfollowers = []
	attempts = 0
	while True:
		log("Follower Fetch Attempt: " + str(attempts))
		attempts += 1
		
		data = fetchJSON('https://api.twitch.tv/kraken/channels/' + streamer + '/follows?direction=DESC&limit=100&offset=' + str(i))
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

	log('Follower Recieved Count: ' + str(len(getfollowers)))
	return getfollowers
	
def getSubscribers():
	i = 0
	count = 1
	getsubscribers = []
	attempts = 0
	while True:
		log("Subscriber Fetch Attempt: " + str(attempts))
		attempts += 1
		
		data = fetchJSON('https://api.twitch.tv/kraken/channels/' + streamer + '/subscriptions?direction=DESC&limit=100&offset=' + str(i))
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

	log('Subscriber Recieved Count: ' + str(len(getsubscribers)))
	return getsubscribers
	
def queuetimer(): #function for resetting the queue every 30 seconds and reloading log
	global logfile
	
	logfile.close()
	logfile = open(logFileName,'a')
	
	global queue
	queue = 0
	if stop == False:
		threading.Timer(10,queuetimer).start()
queuetimer()

def followerCheckTimer(): #function for checking for a new follower every 2 seconds
	if stop == False:
		threading.Timer(10,followerCheckTimer).start()
	else:
		return
	global greetNewFollower
	global greetedFollowers
	if checkStreamOnline() == True:
		if greetNewFollower == True:
			if len(greetedFollowers) == 0:
				greetedFollowers = getFollowers()
				print('Greeted followers list refreshed. ' + str(len(greetedFollowers)))
			else:
				data = fetchJSON('https://api.twitch.tv/kraken/channels/' + streamer + '/follows?direction=DESC&limit=15&offset=0')
				if data == None:
					return
				fols = data['follows']
				for user in fols:
					name = user['user']['display_name'].strip()
					if (name in greetedFollowers) == False:
						message(followerWelcomeMessage.replace("@user@",name))
						greetedFollowers.append(name)
followerCheckTimer()

def sendHeckle(user):
	global heckles
	heckle = heckles[randint(0,len(heckles)-1)]
	message(user + ": " + heckle)
	
def addHeckle(heckle):
	log("Adding heckle: " + heckle)
	global heckles
	global heckleFile
	heckles.append(heckle)
	heckleFile = open(heckleFileName,'r+')
	heckleFile.seek(0,2) #go to end
	heckleFile.write("\n" + heckle)
	
	heckleFile.close() #refreshing list
	heckleFile = open(heckleFileName, 'r+')
	heckles = heckleFile.read().split('\n')
	heckleFile.close() #refreshing list
	
def addKothPraise(praise):
	log("Adding praise: " + praise)
	global kothPraises
	global kothFile
	kothPraises.append(praise)
	kothFile= open(kothFileName,'r+')
	kothFile.seek(0,2) #go to end
	kothFile.write("\n" + praise)
	
	kothFile.close() #refreshing list
	kothFile = open(kothFileName, 'r+')
	kothPraises = kothFile.read().split('\n')
	kothFile.close() #refreshing list
	
def refreshHeckles():
	log("Heckle list refreshed")
	heckleFile = open(heckleFileName, 'r+')
	heckles = heckleFile.read().split('\n')
	heckleFile.close() #refreshing list
	
	kothFile = open(kothFileName, 'r+')
	kothPraises = kothFile.read().split('\n')
	kothFile.close() #refreshing list

heckleTimerCountdown = 0
def autoHeckle(): #auto heckles
	if stop == False:
		threading.Timer(10, autoHeckle).start()
	else:
		return
	global heckleTimerCountdown
	global heckleTimer
	heckleTimerCountdown -= 10
	if(heckleTimerCountdown <= 0):
		if checkStreamOnline() == True:
			sendHeckle(streamer)
		heckleTimerCountdown = heckleTimer
autoHeckle()

def isOp(user):
	return user in ops or user.lower() == bot_owner.lower() or user.lower() == streamer.lower()
	
def addViewer(user):
	global viewers
	if ~(user in viewers) and user != 'hecklebot':
		print("[off]: ADD USER " + user)
		viewers.append(user)
	
def remViewer(user):
	global viewers
	if (user in viewers):
		print("[off]: REM USER " + user)
		viewers.remove(user)

		
def praiseKing(user):
	global kothPraises
	praise = kothPraises[randint(0,len(kothPraises)-1)]
	return praise.replace("@user@", user)

def checkKing(user):
	global isStreaming
	if isStreaming == False:
		message(user + ": The hill is protected while the stream is offline!")
		return

	global koth
	global kothDelay
	global kothTrack
	
	userTime = 0
	if user in kothTrack:
		userTime = kothTrack[user]
	
	curTime = round(time.time())
	if (curTime-userTime) > kothDelay:
		if user == koth.lower(): #Already king
			message(user + ": " + praiseKing(koth))
			return
		
		roll = randint(0,12)
		if roll >= 10: #Victory
			message(user + ": You rolled a " + str(roll) + ", claiming vitory over " + koth + ". " + praiseKing(user))
			koth = user
			saveSettings()
		else: #Failure
			message(user + ": You rolled a " + str(roll) + ", failing to win. " + praiseKing(koth))
	kothTrack[user] = curTime

	
def takeMessage(user, msg, conf):
	global kothEnabled
	
	lower = msg.lower()
	if lower.find('!heckleme') != -1 or lower.find('!heckelme') != -1: #Heckle time!
		sendHeckle(user)
		#return
	
	elif kothEnabled == True and (lower.find('!koth') == 0 or lower.find('!kingofthehill') == 0 or lower.find('!kofth') == 0):
		checkKing(user)
		
	elif lower.find('!') == 0:
		#print('Cockmonkeys')
		for key in infocmds:
			#print('Checking command ' + key)
			if lower.find('!' + key) == 0:
				message(user + ': ' + infocmds[key].replace("@user@",user))
				#return
				
	#print "RAWR "+ lower + " || " + str(lower.find('!addheckle')) + "|" + str(isOp(user))
	#print ops
	
	if isOp(user): #OP only commands
		if lower.find('!help') == 0: 
			message(user + ': !addHeckle [heckle]: Add a heckle ######### ' + '!refreshHeckles: Refreshes heckles from file ######### ' + '!giveaway [viewers] [followers] [subscribers]: Pick a person for the giveaway ######### ' + '!greetFollower: Toggle welcoming new followers ######### ' + '!setFollowerWelcome [message with @user@ for name]: Sets welcome message for new followers ######### ' + '!setHeckleTimer [minutes]: Sets delay for the auto-heckle ######### ' + '!addInfo [cmd] [message]: Adds a FAQ message to auto-respond to ######### ' + '!removeInfo [cmd]: Removes a FAQ message ######### ' + '!toggleKOTH : Toggles king of the hill ######### ' + '!addPraise [praise]: Adds a praise to the king! User @user@ for name ######### ' + '!setKOTHDelay [seconds]: Sets seconds between koth rolls')
			#return
		
		if lower.find('!addheckle ') == 0: #Adding a heckle!
			heckle = msg[11:].strip() #cut the !addheckle
			#print "DERP|" + heckle + "|" + str(len(heckle))
			if len(heckle) > 0:
				message(user + ": Adding heckle [" + heckle + "]")
				addHeckle(heckle)
			#return
					
		if lower.find('!refreshheckles') == 0:
			message(user + ": Heckle file refreshed!")
			refreshHeckles()
			#return
			
		if lower.find('!giveaway ') == 0:
			pool = []
			if lower.find('followers') != -1:
				fol = getFollowers()
				if fol == None:
					message(user + ": Error fetching followers. Try again in a bit.")
					return
				pool += fol
			if lower.find('viewers') != -1:
				pool += viewers
			if lower.find('subscribers') != -1:
				sub = getSubscribers()
				if sub == None:
					message(user + ": Error fetching followers. Try again in a bit.")
					return
				pool += sub
			pool = list(set(pool)) #remove duplicates
			print pool
			message("{0}: And the winner is...... {1}!".format(user, pool[randint(0,len(pool)-1)]))
			#return
			
		if lower.find('!greetfollower') == 0:
			#message(user + ': I WILL ALWAYS GREET FOLLOWERS YOU CANT CHANGE THAT BECAUSE FUCK PYTHON')
			global greetNewFollower
			if greetNewFollower == False: #fucking pythons fucking scope bullshit fuck
				message(user + ': Greeting new followers')
				greetNewFollower = True;
			else:
				message(user + ': Not greeting new followers')
				greetNewFollower = False;
			saveSettings()
			#return
			
		if lower.find('!setfollowerwelcome ') == 0:
			welcome = msg[20:] #cut the !setfollowerwelcome
			#followerWelcomeMessage = welcome.replace('NAME', '{}')
			message(user + ': Follower welcome message changed to [' + followerWelcomeMessage.replace("@user@", user) + ']')
			saveSettings()
			#return
			
		if lower.find('!setheckletimer ') == 0:
			global heckleTimer
			global heckleTimerCountdown
			count = int(msg[16:])
			heckleTimer = count*60
			heckleTimerCountdown = heckleTimer
			message(user + ': Auto-heckle timer set to ' + str(count) + ' minutes.')
			saveSettings()
			#return
		
		if lower.find('!addinfo ') == 0:
			split = msg.split(' ')
			cmd = split[1]
			inf = msg[msg.find(cmd)+len(cmd)+1:]
			cmd = cmd.lower()
			infocmds[cmd] = inf
			message(user + ": Now responding to !" + cmd + " with [" + inf + "]")
			saveInfo()
			
		if lower.find('!removeinfo ') == 0:
			split = msg.split(' ')
			cmd = split[1].lower().strip()
			del infocmds[cmd]
			saveInfo()
			message(user + ": No longer responding to !" + cmd)
		
		if lower.find('!togglekoth') == 0:
			if kothEnabled == False: #fucking pythons fucking scope bullshit fuck
				message(user + ': King of the hill enabled')
				kothEnabled = True;
			else:
				message(user + ': King of the hill disabled')
				kothEnabled = False;
			saveSettings()
			
		if lower.find('!addpraise ') == 0:
			add = msg[11:]
			if len(add) > 0:
				message(user + ": Adding praise [" + add.replace("@user@",user) + "]")
				addKothPraise(add)
				
		if lower.find('!setkothdelay ') == 0:
			delay = int(msg[14:])
			global kothDelay
			kothDelay = delay;
			message(user + ': KOTH delay set to ' + str(delay) + ' seconds.')
			saveSettings()
			
			

def handleMode(data):
	c = data.split(":jtv MODE " + channel + " ")[1]
	act = c.split(' ')[0].strip()
	user = c.split(' ')[1].strip()
	if act == '+o' and ~isOp(user) :
		log("Opping " + user)
		ops.append(user)
	elif act == '-o' and isOp(user):
		log("Deopping " + user)
		ops.remove(user)

def main(conf):
	while True:
		incoming = irc.recv(1204)
		for data in incoming.split('\n'):
			if len(data.strip()) == 0:
				continue
			log(data)
			

			if data.find('PRIVMSG') != -1:
				message = data.split(':')[2]
				user = data.split(':')[1]
				user = user.split('!')[0]
				takeMessage(user, message, conf)
			
			elif data.find('PING') != -1:
				log('PONG')
				irc.send(incoming.replace('PING','PONG')) #Responds to pings from server
			
			elif data.find('MODE') != -1: #Someone is  being opped or deopped
				try:
					handleMode(data)
				except ValueError:
					message(user + ": Invalid input")
				
			elif data.find('PART') != -1: #Someone leaves
				user = data.split(':')[1]
				user = user.split('!')[0]
				remViewer(user)
			elif data.find('JOIN') != -1: #Someone joins
				user = data.split(':')[1]
				user = user.split('!')[0]
				addViewer(user)
						
			elif data.find('353') != -1: #User listing:
				list = data.split(':')[2]
				for name in list.split(' '):
					addViewer(name.strip()) #Get username
			
		

try:
	main(conf)
except KeyboardInterrupt:
	stop = True

log("Quitting.")
	
stop = True
logfile.close()
heckleFile.close()
kothFile.close()


'''
	TODO
	add an addInfo command for adding random informational commands
	optimize api checks (namely stream-online)
'''