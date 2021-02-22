import requests
import os
import difflib
from configparser import ConfigParser

S = requests.Session()
URL = "https://test.wikipedia.org/w/api.php"

config_object = ConfigParser()
config_object.read("config.conf")
userinfo = config_object["INFO"]
username=str(userinfo["username"])
password=str(userinfo["password"])

def getchanges(idn, ido):
	PARAMS={
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"revids": str(idn)+"|"+str(ido),
		"formatversion": "latest",
		"rvprop": "content|oresscores|sha1",
		"rvslots": "*"
	}
	R = S.get(url=URL, params=PARAMS)
	DATA = R.json()
	c1=DATA['quey']['pages'][0]['revisions'][0]['content']
	c2=DATA['quey']['pages'][1]['revisions'][0]['content']
	diff=difflib.ndiff(c1, c2)
	for l in diff:
		if l.startswith('+ '):
			print(l)
		
def messaggio(utente, testo):
	#controllare benvenuto
	#api edit
	print('msg')
		
def placeholder(ns):
	print("Namespace "+str(ns))


# Token login
PARAMS0 = {
	'action':"query",
	'meta':"tokens",
	'type':"login",
	'format':"json"
}

R = S.get(url=URL, params=PARAMS0)
DATA0 = R.json()

LOGIN_TOKEN = DATA0['query']['tokens']['logintoken']

# Login

PARAMS1 = {
	'action': "clientlogin",
	'username': username,
	'password': password,
	'loginreturnurl': 'http://127.0.0.1:5000/',
	'logintoken': LOGIN_TOKEN,
	'format': "json"
}

R = S.post(URL, data=PARAMS1)
DATA1 = R.json()
if DATA1["clientlogin"]["status"]=="PASS":
	print("Logged in as "+username);
else:
	print("Login error."+DATA1)
	raise SystemExit

#Token CSRF
PARAMS2 = {
	"action": "query",
	"meta": "tokens",
	"format": "json"
}

R = S.get(url=URL, params=PARAMS2)
DATA2 = R.json()

CSRF_TOKEN = DATA2['query']['tokens']['csrftoken']


#Analyze recent changes

PARAMS3 ={
	"action": "query",
	"format": "json",
	"list": "recentchanges",
	"continue": "-||",
	"rcprop": "title|user|userid|timestamp|flags|ids", #patrolled <- serve patrol/patrolmarks
	"rctype": "edit|new",
	"rclimit": "max",
	"rcdir" : "newer",
	"rcnamespace": "0|1|2|3|6|14", #todo: +6, 14 (file, cat) per verifiche.
	"rctoponly": 1	
}

try:
	PARAMS3["rcstart"]=str(config_object["DATA"]["timestamp"])
	lasttimestamp=str(config_object["DATA"]["timestamp"])
except (KeyError, NameError) as error:
	os.startfile("update_timestamp.py")
	raise SystemExit

R = S.get(url=URL, params=PARAMS3)
DATA3 = R.json()
print(DATA3)
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
	USERS=DATA4['query']['users']
	print(DATA4)
for us in USERS:
	try:
		edcount=us['editcount']
	except KeyError: #Anonym users
		edcount=0
	getchanges(us['revid'], (us['old_revid']))
	if edcount < 100 and rc['timestamp']!=lasttimestamp: #todo: verifica che non sia verificato rc["patrolled"]=="" / "unpatrolled (serve patrol/patrolmark); #filtra namespace da ids
		print(str(us['name'])) 
		if rc["ns"] == 0:
			placeholder(0)
		if rc["ns"] == 1:
			placeholder(1)
		if rc["ns"] == 2:
			placeholder(2)
		if rc["ns"] == 3:
			placeholder(3)
		if rc["ns"] == 6:
			placeholder(6)
		if rc["ns"] == 14:
			placeholder(14)
		lasttimestamp=rc['timestamp']
		config_object["DATA"]={
			"timestamp": lasttimestamp
		}
		with open('config.conf', 'w') as conf:
			config_object.write(conf)
	else:
		print("NO - "+str(us['name'])) 
