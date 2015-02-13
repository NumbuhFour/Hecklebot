import socket
import threading
import datetime
from urllib2 import urlopen
import json
from random import randint
'''
bot_owner = 'Numbuhfour'
streamer = 'misteratombomb'
nick = 'Hecklebot'
channel = '#misteratombomb'
server = 'irc.twitch.tv'
password = 'oauth:igsxawqpsklid3ecclq7gmfgzrl9u4'

heckleFileName = 'heckles.txt'
logFileName = 'log.txt'

greetNewFollower = True
greetedFollowers = []
followerWelcomeMessage = 'Welcome, {}, to the hoard of hecklers!'

def checkStreamOnline():
	try:
		res = urlopen('https://api.twitch.tv/kraken/streams/' + streamer)
		data = json.loads(res.read())
		print 'Rawr ' + str(data['stream'])
		if data['stream']:
			return True
		else:
			return False
		
	except HTTPError:
		log("HTTPError on stream check")
		return False
	return False
	
print str(checkStreamOnline())
'''
rawr = {'kingofthenorth':'NumbuhFour is the king of everything!'}
with open("/var/www/hecklebot/chatlog.txt", 'w') as outfile: 
	json.dump(rawr,outfile)
	
for key in rawr:
	print 'Bitch [' + key + ']'