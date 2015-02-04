from urllib2 import urlopen
import json
from random import randint

i = 0
count = 1
followers = []
user = 'cheese05'

attempts = 0
while True:
	print "Attempt: " + str(attempts)
	attempts += 1
	
	response = urlopen('https://api.twitch.tv/kraken/channels/' + user + '/follows?direction=DESC&limit=100&offset=' + str(i))
	data = json.loads(response.read())
	count = data['_total']
	
	for follower in data['follows']:
		name = follower['user']['name']
		followers.append(name)
	
	if i > count:
		break;
	i += 100;

print 'Count Recieved: ' + str(len(followers))
print 'Random: ' + followers[randint(0,len(followers)-1)]