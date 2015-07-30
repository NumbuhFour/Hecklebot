
from sqlInterface import SQLInterface
import json

class Doop:
	streamer = "altaswolf"
	sqli = None
	def __init__(self):
		self.sqlpass = "BajaBlast"
		self.sqli = SQLInterface(self)
	
	def log(self,msg):
		print msg
		
	def start(self):
		"""f = open("money.txt",'r')
		self.bank = json.loads(f.read());
		f.close()
		
		query = "INSERT INTO {0}_users (username, data_key, value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE value = VALUES(value)".format(self.streamer)
		i = 0
		
		paramList = []
		for userLow in self.bank:
			entry = self.bank[userLow]
			user = self.sqli.con.escape_string(userLow)
			paramList.append( (user, 'money', str(entry["money"]) ) )
			paramList.append( (user, 'karma', str(entry["karma"]) ) )
		
		print("QUERY : " + query)
		self.sqli.cur.executemany(query, paramList)
		self.sqli.con.commit()
		print(paramList)
		print(self.sqli.con.escape_string('DROP TABLE doop'))"""
		test = self.sqli.readAllUsersForKey('money')
		print(test)

doop = Doop()
doop.start()