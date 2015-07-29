import MySQLdb as mysql

class SQLInterface:
	createConfigTableQuery = "CREATE TABLE `{0}_config` ( `module` tinytext COLLATE utf8_bin NOT NULL, `conf_key` tinytext COLLATE utf8_bin NOT NULL, `value` text COLLATE utf8_bin NOT NULL, PRIMARY KEY (`module`(8),`conf_key`(8))) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin"
	createUserTableQuery = "CREATE TABLE `{0}_users` ( `data_key` tinytext CHARACTER SET utf8 COLLATE utf8_bin NOT NULL, `username` tinytext CHARACTER SET utf8 COLLATE utf8_bin NOT NULL, `value` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1"
	
	writeConfigQuery = "INSERT INTO {0}_config (module, conf_key, value) VALUES ('{1}', '{2}','{3}') ON DUPLICATE KEY UPDATE value = VALUES(value)"

	def __init__(self, hb):
		self.hb = hb
		self.connect()
		
	def connect(self):
		try:
			self.hb.log("Connecting to DB...")
			self.con = mysql.connect('localhost', 'rowbot', 'BajaBlast', 'rowbot');
			self.hb.log("Connected to DB")
		except mysql.Error, e:
			print("Error %d: %s" % (e.args[0], e.args[1]))
		finally:
			if self.con:
				self.con.close()
	
	# Checks the database for the streamer's config table
	# as well as its user table and creates them if necessary
	def checkStreamerConfig(self):
		if not self.checkTableExists(self.hb.streamer + "_config"):
			q = self.createConfigTableQuery.format(self.hb.streamer)
			cur = self.con.cursor()
			cur.execute(q)
		if not self.checkTableExists(self.hb.streamer + "_users"):
			q = self.createUserTableQuery.format(self.hb.streamer)
			cur = self.con.cursor()
			cur.execute(q)
		pass
	
	def checkTableExists(self, table):
		q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'dbname' AND table_name = '{0}'".format(table)
		
		with self.con as con:
			cur = con.cursor()
			cur.execute(q)
			return cur.rowcount > 0
		return False
	
	# Write to config
	def writeToConfig(self, module, key, value):
		q = self.writeConfigQuery.format(self.hb.streamer, module, key, value)
		with self.con as con:
			cur = con.cursor()
			cur.execute(q)
		pass
	
	# Read from config. If module or key does not exist,
	# make a new one from the given default value
	def readFromConfig(self, module, key, defaultValue):
		q = "SELECT value FROM {0}_config WHERE module = '{1}' AND conf_key = '{2}'".format(self.hb.streamer, module, key)
		with self.con as con:
			cur = con.cursor()
			cur.execute(q)
			if(cur.rowcount > 0):
				return cur.fetchone()[0]
			else:
				q = "INSERT INTO {0}_config(module,conf_key,value) VALUES('{1}', '{2}', '{3}')".format(self.hb.streamer, module,key,defaultValue)
				cur.execute(q)
				return defaultValue
		return defaultValue
	
	# Read data from user table 
	def readKeyForUser(self, key, user, defaultValue):
		q = "SELECT value FROM {0}_users WHERE data_key = '{1}' AND username = '{2}'".format(self.hb.streamer, key, user)
		with self.con as con:
			cur = con.cursor()
			cur.execute(q)
			if(cur.rowcount > 0):
				return cur.fetchone()[0]
			else:
				q = "INSERT INTO {0}_users(data_key,username,value) VALUES('{1}', '{2}', '{3}')".format(self.hb.streamer, key,user,defaultValue)
				cur.execute(q)
				return defaultValue
		return defaultValue
	
	###### Module Specific functions ######