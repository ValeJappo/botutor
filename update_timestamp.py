import requests
import os
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.conf")
info = config_object["INFO"]
S = requests.Session()
URL = "https://"+str(info["site"])+".wikipedia.org/w/api.php"

#Analyze recent changes

PARAMS3 ={
	"action": "query",
	"format": "json",
	"list": "recentchanges",
	"continue": "-||",
	"rcprop": "title|user|userid|timestamp",
	"rctype": "edit|new",
	"rcdir": "older",
	"rclimit": 1,
	"rctoponly": 1	
}

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
	if DATA4['batchcomplete']=="":
		print("Data saved. Stop execution.")
	else:
		print(DATA4)
		print("Error while saving.")
	lasttimestamp=rc['timestamp']
	config_object["DATA"]={
		"timestamp": lasttimestamp
	}
	with open('config.conf', 'w') as conf:
		config_object.write(conf)