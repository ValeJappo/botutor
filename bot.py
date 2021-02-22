import requests
import os
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.conf")
userinfo = config_object["INFO"]
username=str(userinfo["username"])
password=str(userinfo["password"])

S = requests.Session()
URL = "https://test.wikipedia.org/w/api.php"

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

print(LOGIN_TOKEN)

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
        if us['editcount'] < 100 and rc['timestamp']!=lasttimestamp:
            print(str(us['name'])) 
            lasttimestamp=rc['timestamp']
            config_object["DATA"]={
		    "timestamp": lasttimestamp
	    }
            with open('config.conf', 'w') as conf:
              config_object.write(conf)
        else:
            print("NO - "+str(us['name'])) 
