from command import Command
import threading

import pickle
import rrenaud_gibberish.gib_detect_train
class Gibberish(Command):
	strikes = {}
	maxStrikes = 3
	threads = []
	disabled = False
	
	def __init__(self, hb):
		self.hb = hb
		model_data = pickle.load(open('gib_model.pki', 'rb'))
		self.model_mat = model_data['mat']
		self.threshold = model_data['thresh']
		#self.publicHelpString = "!: Print help";
		pass
		
	def checkString(self,message):
		return self.getGibProbability(message) > self.threshold
	def getGibProbability(self,message):
		return rrenaud_gibberish.gib_detect_train.avg_transition_prob(message, self.model_mat)
	
	def writeConf(self, conf):
		pass
	
	def readFromConf(self, conf):
		pass
	
	def checkAndAct(self, message, user):
		print("Checking message")
		probability = self.getGibProbability(message)
		print("Message [" + message + "] " + str(probability) + " " + str(self.threshold))
		if(probability < self.threshold):
			print "Gibberish strike on " + user + ". Strikes: " + str(self.strikes[user]) + " Probability: " + str(probability) + " Message: " + message
			
			self.strikes[user] = self.strikes[user] + 1
			if(self.strikes[user] >= self.maxStrikes):
				self.hb.message("/ban " + user)
				self.hb.message(user + " has been banned for mis-use of gibberish.")
		elif(self.strikes[user] > 0):
			self.strikes[user] -= 1
		pass
	
	def checkMessage(self, message, user):
		message = message.strip().lower()
		if(self.hb.isOp(user) and message == "!enable gibberish"):
			self.disabled = False
			self.hb.message(user + ": Gibberish detection enabled");
			return True
		if(self.hb.isOp(user) and message == "!disable gibberish"):
			self.disabled = True
			self.hb.message(user + ": Gibberish detection disabled");
			return True
		
		if(self.disabled):
			return False
		
		if (not user in self.strikes):
			self.strikes[user] = 0
		
		t = threading.Thread(target=self.checkAndAct, args = (message, user))
		t.daemon = True; # Does not keep process running
		t.start();
		self.threads.append(t);
		
		return False
		
	def onMessage(self, message, user):
		pass
		
	def stop(self):
		pass