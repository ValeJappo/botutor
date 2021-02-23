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

def disambigua(links, user):
	for link in links:
		PARAMS={
			"action": "parse",
			"format": "json",
			"page": link,
			"prop": "wikitext",
			"formatversion": "2"
		}
		R = S.get(url=URL, params=PARAMS)
		DATA = R.json()
		print(DATA)
		if DATA['parse']['wikitext'].find("{{Disambigua}}") >= 0:
			print("DISAMBIGUA")
	

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

	for us in USERS:
		try:
			edcount=us['editcount']
		except KeyError: #Anonym users
			edcount=0
		if edcount < 100 and rc['timestamp']!=lasttimestamp: #todo: verifica che non sia verificato rc["patrolled"]=="" / "unpatrolled (serve patrol/patrolmark); #filtra namespace da ids
			PARAMS5={
				"action": "query",
				"format": "json",
				"prop": "revisions",
				"revids": str(rc['revid'])+"|"+str(rc['old_revid']),
				"formatversion": "latest",
				"rvprop": "content|oresscores|sha1",
				"rvslots": "*"
			}
			R = S.get(url=URL, params=PARAMS5)
			DATA5 = R.json()
			print(DATA5)
			if True:#float(DATA5['query']['pages'][0]['revisions'][1]['oresscores']['goodfaith']['true']) >= float(DATA5['query']['pages'][0]['revisions'][1]['oresscores']['goodfaith']['false']):
				c1=DATA5['query']['pages'][0]['revisions'][0]['slots']['main']['content']
				try:
					c2=DATA5['query']['pages'][0]['revisions'][1]['slots']['main']['content']
					diff=difflib.ndiff(c1, c2)
					newpage=False
				except IndexError: #New page
					diff=c1
					newpage=True
				add=""
				rem=""
				links=[]
				il=0;
				b=0
				brackets=False
				
				for l in diff:#todo: se si divide in due un link ([[Giappone]] --> [[Gia]][[ppone]]), solo il secondo viene considerato
					if brackets and l.replace('+ ', '').replace(' ', '') != "]" and not l.startswith('- '):
						try:
							links[il]=links[il]+l.replace('+ ', '').replace(' ', '').replace('[', '')
						except IndexError:
							links.append(l.replace('+ ', '').replace(' ', '').replace('[', ''))
					
					if l.replace('+ ', '').replace(' ', '') == "]" and b==0 and brackets:
							b=-1
						
					if (l.replace('+ ', '').replace(' ', '') == "]" and b==-1 and brackets) or (l.replace('+ ', '').replace(' ', '') == "|" and brackets):
						b=0
						il=+1;
						brackets=False
							
					if not newpage:
						if l.startswith('+ '):
							add=add+l.replace('+ ', '')
							if l.replace('+ ', '') == "[" and b==0:
								b=+1
							if l.replace('+ ', '') == "[" and b==1:
								b=0
								brackets=True	

						if l.startswith('- '):
							rem=rem+l.replace('- ', '')
					else:
						add=add+l
						if l=="[" and b==0:
							b=+1
						if l=="[" and b==1:
							b=0
							brackets=True

				print(str(us['name'])) 
				print(add)
				print(rem)
				for link in links:
					if link!="":
						print(link)
						
				#controlli
				disambigua(links, rc['user'])
				
				lasttimestamp=rc['timestamp']
				config_object["DATA"]={
					"timestamp": lasttimestamp
				}
				with open('config.conf', 'w') as conf:
					config_object.write(conf)
			else:
				print("NO - "+str(us['name']))
		else:
			print("NO - "+str(us['name'])) 
