from command import Command
import json
import requests
class FollowViewers(Command):
	#follows whoever views the stream
	#fileName = "streamPaymentTracker.txt"
	def __init__(self, hb):
		self.hb = hb
		#self.helpString = "*!setMoneyPerStream [amount]: Sets amount received for viewing a stream ######## *!resetStreamTracking: Resets stream tracking for monies distribution"
		pass
	
	def onJoin(self, user):
		r = requests.put('https://api.twitch.tv/kraken/users/' + self.hb.nick + '/follows/channels/' + user + '?oauth_token=' + self.hb.password);
		pass
		