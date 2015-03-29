from command import Command
import json
from random import randint
class LinkStreamer(Command):
	links = {}
	fileName = "streamerlinks.txt"
	def __init__(self, hb):
		self.hb = hb
		self.publicHelpString = "!addMyStream [Blurb]: Add your username to hecklebot's linking repertoire ######## !removeMyStream: Removes your stream from hecklebot's linking repertoire";
		pass
		
	def writeConf(self, conf):
		conf["linkstreamer"] = { "fileName":self.fileName };
	
	def readFromConf(self, conf):
		self.fileName = conf['info']['linkstreamer'];
		self.loadInfo()
		pass
		
	def checkMessage(self, message, user):
		'''message = message.strip().lower()
		if message.find('!addinfo') == 0 or message.find('!removeinfo') == 0: #Admin command
			return True
		if message.find('!') != -1:
			for key in self.cmds:
				if message.find('!' + key.lower()) != -1:
					return True;
		'''
		return False
		
	def onMessage(self, message, user):
		message = message.strip()
		lower = message.lower()
		'''if lower.find('!addinfo') == 0 or lower.find('!removeinfo') == 0: #Admin command
			if self.hb.isOp(user) == True:
				if lower.find('!addinfo ') == 0:
					split = message.split(' ')
					cmd = split[1]
					inf = message[message.find(cmd)+len(cmd)+1:]
					cmd = cmd.lower()
					self.cmds[cmd] = inf
					self.hb.message(user + ": Now responding to !" + cmd + " with [" + inf + "]")
					self.saveInfo()
				if lower.find('!removeinfo ') == 0:
					split = message.split(' ')
					cmd = split[1].lower().strip()
					del self.cmds[cmd]
					self.saveInfo()
					self.hb.message(user + ": No longer responding to !" + cmd)
				
		elif lower.find('!') != -1:
			for key in self.cmds:
				if lower.find('!' + key.lower()) != -1:
					self.hb.message(user + ': ' + self.cmds[key].replace("@user@",user))
		'''
	def loadInfo(self):
		f = open(self.fileName, 'r')
		self.links = json.loads(f.read());
		f.close();
		print('loading Info ' + str(self.cmds))

	def saveInfo(self):
		with open(self.fileName, 'w') as outfile: 
			json.dump(self.links,outfile)
			outfile.close()
	
	def findStream(self):
		list = self.links.copy()
		online = False
		streamer = ""
		message = ""
		
		for(i in range(0, min(len(list['names']),10)):
			index = randint(0,len(list['names'])-1)
			streamer = list['names'][index]
			message = list['messages'][index]
			if(self.hb.checkOtherOnline(streamer)):
				online = True
				break
		
		if streamer != "":
			if(online == True):
				send = "It looks like the streams over, but " + streamer + " is streaming! Go check it out http://twitch.tv/" + streamer
				if message != "":
					send = send + ' : "' + message '"'
				self.hb.message(send)
			else :
				send = "It looks like the streams over, but why not check out " + streamer + "? http://twitch.tv/" + streamer + "/profile"
				if message != "":
					send = send + ' : "' + message '"'
				self.hb.message(send)
				pass
			pass
		
			
			'''
			-!addStream to add a link to hecklebot's list of streamers
			-!imbored to popout a random link to someone elses stream
			-Pop out a link to another stream on stream end
			-Fix stream-end detection to not think its ended everytime you crash
			
			pretty sure i can check if a streamer exists
'''