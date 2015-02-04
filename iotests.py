import os
import datetime

heckles = []

def refreshHeckles():
	global heckles
	f.seek(0,0);
	heckles = f.read().split('\n')
	
def printLastHeckle():
	global heckles
	print heckles[len(heckles)-1]

f = open('heckles.txt', 'r+')
refreshHeckles()
printLastHeckle()
'''
print os.listdir("./commands")
os.system("python ./commands/" + os.listdir("./commands")[0])
'''
print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
