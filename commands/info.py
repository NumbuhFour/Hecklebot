from command import Command
import json
class Info(Command):
	cmds = {}
	fileName = "info.txt"
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "*!addInfo [cmd] [message]: Add a FAQ message to auto-respond to ######## *!removeInfo [cmd]: Removes a FAQ message";
		pass
		
	def writeConf(self, conf):
		conf["info"] = { "fileName":self.fileName };
	
	def readFromConf(self, conf):
		self.fileName = conf['info']['fileName'];
		self.loadInfo()
		pass
		
	def checkMessage(self, message, user):
		message = message.strip().lower()
		isOp = self.hb.isOp(user)
		if message.find('!addinfo') == 0 or message.find('!removeinfo') == 0: #Admin command
			return True
		if message.find('!refreshinfo') == 0 and isOp:
			return True
		if message.find('!') != -1:
			for key in self.cmds:
				if message.find('!' + key.lower()) != -1:
					return True;
		return False
		
	def onMessage(self, message, user):
		message = message.strip()
		lower = message.lower()
		if lower.find('!refreshinfo') == 0:
			self.hb.message(user + ": FAQ refreshed!")
			self.loadInfo()
		if lower.find('!addinfo') == 0 or lower.find('!removeinfo') == 0: #Admin command
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
		
	def loadInfo(self):
		f = open(self.fileName, 'r')
		self.cmds = json.loads(f.read());
		f.close();
		print('loading Info ' + str(self.cmds))

	def saveInfo(self):
		with open(self.fileName, 'w') as outfile: 
			json.dump(self.cmds,outfile)
			outfile.close()
			
			'''
			
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
				self.message(user + ": No longer responding to !" + cmd)'''