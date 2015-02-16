from command import Command
import threading
class GreetFollowers(Command):
	greetedFollowers = []
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "*!greetFollower: Toggle welcoming new followers ######## *!setFollowerWelcome [message with @user@ for name]: Sets welcome message for new followers";
		pass
		
	def start(self):
		self.followerCheckTimer()
		
	def writeConf(self, conf):
		conf['greet'] = { 'greetNewFollower':self.greetNewFollower, 'followerWelcomeMessage':self.followerWelcomeMessage }
		pass
	
	def readFromConf(self, conf):
		self.greetNewFollower = conf['greet']['greetNewFollower']
		self.followerWelcomeMessage = conf['greet']['followerWelcomeMessage']
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if self.hb.isOp(user):
			if lower.find('!greetfollower') == 0:
				return True
				
			if lower.find('!setfollowerwelcome ') == 0:
				return True
		
	def onMessage(self, message, user):
		lower = message.strip().lower()
		if self.hb.isOp(user):
			if lower.find('!greetfollower') == 0:
				#message(user + ': I WILL ALWAYS GREET FOLLOWERS YOU CANT CHANGE THAT BECAUSE FUCK PYTHON')
				if self.greetNewFollower == False: #fucking pythons fucking scope bullshit fuck
					self.hb.message(user + ': Greeting new followers')
					self.greetNewFollower = True;
				else:
					self.hb.message(user + ': Not greeting new followers')
					self.greetNewFollower = False;
				self.hb.saveSettings()
				#return
				
			if lower.find('!setfollowerwelcome ') == 0:
				welcome = message[20:] #cut the !setfollowerwelcome
				#followerWelcomeMessage = welcome.replace('NAME', '{}')
				self.hb.message(user + ': Follower welcome message changed to [' + self.followerWelcomeMessage.replace("@user@", user) + ']')
				self.hb.saveSettings()
				#return

	def followerCheckTimer(self): #function for checking for a new follower every 2 seconds
		if self.hb.stop == False:
			threading.Timer(10,self.followerCheckTimer).start()
		else:
			return
		if self.hb.checkStreamOnline() == True:
			if self.greetNewFollower == True:
				if len(self.greetedFollowers) == 0:
					self.greetedFollowers = self.hb.getFollowers()
					print('Greeted followers list refreshed. ' + str(len(self.greetedFollowers)))
				else:
					data = self.hb.fetchJSON('https://api.twitch.tv/kraken/channels/' + self.hb.streamer + '/follows?direction=DESC&limit=15&offset=0')
					if data == None:
						return
					fols = data['follows']
					for user in fols:
						name = user['user']['display_name'].strip()
						if (name in self.greetedFollowers) == False:
							self.hb.message(self.followerWelcomeMessage.replace("@user@",name))
							self.greetedFollowers.append(name)