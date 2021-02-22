import requests
import os
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.conf")

S = requests.Session()
URL = "https://test.wikipedia.org/w/api.php"

#Analyze recent changes

PARAMS3 ={
	"action": "query",
	"format": "json",
	"list": "recentchanges",
	"continue": "-||",
	"rcnamespace": "0|2",
	"rcprop": "title|user|userid|timestamp",
	"rctype": "edit|new",
	"rctoponly": 1	
}

try:
	PARAMS3["rcstart"]=str(config_object["DATA"]["timestamp"])
	lasttimestamp=str(config_object["DATA"]["timestamp"])
	PARAMS3["rclimit"]="max"
	PARAMS3["rcdir"]="newer"
except (KeyError, NameError) as error:
	lasttimestamp=0
	PARAMS3["rclimit"]=1
	PARAMS3["rcdir"]="older"

R = S.get(url=URL, params=PARAMS3)
DATA3 = R.json()

RECENTCHANGES = DATA3['query']['recentchanges']
for rc in RECENTCHANGES:
	PARAMS4={
		"action": "query",
		"format": "json",
		"list": "users",
		"usprop": "blockinfo|editcount|gender",
		"ususers": rc['user']
	}
	R = S.get(url=URL, params=PARAMS4)
	DATA4 = R.json()
	print(DATA4)
	USERS=DATA4['query']['users']
for us in USERS:
	print(us)
	try:
		edcount=us['editcount']
	except KeyError: #Anonym users
		edcount=0
	if edcount < 100 and rc['timestamp']!=lasttimestamp:
		print(str(us['name'])) 
		lasttimestamp=rc['timestamp']
		config_object["DATA"]={
			"timestamp": lasttimestamp
		}
		with open('config.conf', 'w') as conf:
			config_object.write(conf)
	else:
		print("NO - "+str(us['name'])) 
