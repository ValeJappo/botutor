import requests
import os
import difflib
import json
from tinydb import TinyDB, Query
from configparser import ConfigParser

i=0
messages={}
config_object = ConfigParser()
config_object.read("config.conf")
info = config_object["INFO"]
username=str(info["username"])
password=str(info["password"])

S = requests.Session()
URL = "https://"+str(info["site"])+".wikipedia.org/w/api.php"

def disambigua(links, user):
	for link in links:
		try:
			PARAMS={
				"action": "query",
				"format": "json",
				"prop": "templates",
				"titles": link,
				"formatversion": "latest",
				"tltemplates": "Template:Disambigua"
			}
			R = S.get(url=URL, params=PARAMS)
			DATA = R.json()
			if DATA['query']['pages'][0]['templates'][0]['title']=="Template:Disambigua":
				msg(user, "DISAMBIGUA")
		except KeyError:#Page do not exist
			pass			
	
def linkfile(add, user):
	if add.find("upload.wikimedia.org") >= 0:
		msg(user, "LINKFILE")

def linkcat(links, user):
	for link in links:
		if link.find(":") < 0:
			msg(user, "LINKCAT")

def citaweb(add, user):
	if add.find("<ref>[http") >= 0 or add.find("<ref>http") >= 0:
		msg(user, "CITAWEB")	

def wrongref(add, user):
	if add.find("[1]") >=0 and add.find("[2]") >= 0 and add.find("[[1]]") < 0 and add.find("[[2]]") < 0:
		msg(user, "WRONGREF")

def sectionlink(add, user):
	if add.replace(" ", "").find("==[[") >=0 and add.replace(" ", "").find("]]==") >=0:
		msg(user, "SECTIONLINK")

def sectionformat(add, user):
	if add.replace(" ", "").find("==''") >=0 and add.replace(" ", "").find("''==") >=0:
		msg(user, "SECTIONFORMAT")

def sezionistandard(add, user):
	sections=[]
	if (add.replace(" ", "").lower().find("==note==")) > 0:
		"""
		s=0
		si=0
		section=False
		for l in add:
			if l=="=" and s==0 and not section:
				s=1
			if l=="=" and s==1 and not section:
				s=0
				section=True

			if section and l!="=":
				try 
			if section and l=="=":
				s=-1

			if s==-1 and l=="=":
				section=False
				si=si+1
			elif s==-1:
				s=0
		"""
		sections.append(add.replace(" ", "").lower().find("==note=="))
	if (add.replace(" ", "").lower().find("==bibliografia==")) > 0:
		sections.append(add.replace(" ", "").lower().find("==bibliografia=="))
	if (add.replace(" ", "").lower().find("==vocicorrelate==")) > 0:
		sections.append(add.replace(" ", "").lower().find("==vocicorrelate=="))
	if (add.replace(" ", "").lower().find("==altriprogetti==")) > 0:
		sections.append(add.replace(" ", "").lower().find("==altriprogetti=="))
	if (add.replace(" ", "").lower().find("==collegamentiesterni==")) > 0:
		sections.append(add.replace(" ", "").lower().find("==collegamentiesterni=="))

	i=0
	for section in sections:
		if i==0:
			i=i+1
		elif section < sections[i]:
			msg(user, "SEZIONISTANDARD")
			i=i+1

def tradottoda(title, user):
	try:
		PARAMS={
			"action": "query",
			"format": "json",
			"prop": "templates",
			"titles": title,
			"formatversion": "latest",
			"tltemplates": "Template:Tradotto da"
		}
		R = S.get(url=URL, params=PARAMS)
		DATA = R.json()
		if DATA['query']['pages'][0]['templates'][0]['title']=="Template:Disambigua":
			msg(user, "TRADOTTODA")
	except KeyError:#Page do not exist
		msg(user, "TRADOTTODA")

def traduzioneerrata(add, user):
	if (add.replace(" ", "").lower().find("==riferimenti==")) > 0:
		msg(user, "TRADUZIONEERRATA")

def msg(user, msgid):
	db = TinyDB('users.json')
	User = Query()
	with open('messages.json') as f:
		data = json.load(f)
		text=data[msgid]
	notwarned=True
	try:
		notwarned=not db.search(User.name == str(user))[0][str(msgid)]
	except (IndexError, KeyError) as e:
		notwarned=True
	if notwarned:
		print(msgid)
		db.upsert({'name': str(user), str(msgid): True}, User.name == str(user))
		try:
			messages[user].append(text)
		except KeyError:
			messages[user]=[text]

def crsf_login():
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
		print("Logged in as "+username)
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

	return DATA2['query']['tokens']['csrftoken']

#Analyze recent changes

PARAMS3 ={
	"action": "query",
	"format": "json",
	"list": "recentchanges",
	"continue": "-||",
	"rcprop": "title|user|userid|timestamp|flags|tags|ids",
	"rctype": "edit|new",
	"rclimit": "max",
	"rcdir" : "newer",
	"rcnamespace": "0|1|2|3|6|14"
}

try:
	PARAMS3["rcstart"]=str(config_object["DATA"]["timestamp"])
	lasttimestamp=str(config_object["DATA"]["timestamp"])
except (KeyError, NameError) as error:
	os.system("python3 update_timestamp.py")
	raise SystemExit

R = S.get(url=URL, params=PARAMS3)
DATA3 = R.json()
RECENTCHANGES = DATA3['query']['recentchanges']
for rc in RECENTCHANGES:
	i=i+1
	print(i)
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

		try:
			isbot=rc['bot']==""
		except KeyError:
			isbot=False

		if rc['user']=="ValeJappo":	#DEBUG <-- todo: rimuovere
			edcount=0				#DEBUG

		if edcount < 100 and rc['timestamp']!=lasttimestamp and not "mw-reverted" in rc["tags"] and not "mw-undo" in rc["tags"] and not "mw-manual-revert" in rc["tags"] and not isbot:
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
			#input("Premi un tasto per continuare")#DEBUG-SLOW MODE
			try:
				score=float(DATA5['query']['pages'][0]['revisions'][1]['oresscores']['goodfaith']['true'])
			except IndexError: #New page
				score=float(DATA5['query']['pages'][0]['revisions'][0]['oresscores']['goodfaith']['true'])
			except: #page deleted
				print("Errore")
				break

			if rc['user']=="ValeJappo":	#DEBUG <-- todo: rimuovere
				score=1					#DEBUG
			if score >= 0.3:
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
				il=0
				b=0
				brackets=False
				
				for l in diff:#todo: se si divide in due un link ([[Giappone]] --> [[Gia]][[ppone]]), solo il secondo viene considerato
					if brackets and l.replace('+ ', '').replace('  ', '') != "]" and l.replace('+ ', '').replace(' ', '') != "|" and not l.startswith('- '):
						if len(l)>1:
							l=l[2:]
						try:
							links[il]=links[il]+l
						except IndexError:
							links.append(l)
					
					if l.replace('+ ', '').replace(' ', '') == "]" and b==0 and brackets:
						b=-1
						
					if b==-1:
						b=0
						if (l.replace('+ ', '').replace(' ', '') == "]" and brackets) or (l.replace(" ", "").replace("+", "") == "|" and brackets):
							il=il+1
							brackets=False

					if b==0 and brackets:
						if l.replace(" ", "").replace("+", "") == "|":
							il=il+1
							brackets=False

					if not newpage:
						if l.startswith('+ '):
							add=add+l.replace('+ ', '')
							if l.replace('+ ', '') == "[" and b==0 and not brackets:
								b=+1
							elif b==1 and not brackets:
								b=0
								if l.replace('+ ', '') == "[": 
									brackets=True	

						if l.startswith('- '):
							rem=rem+l.replace('- ', '')
					else:
						add=add+l
						if l.replace(" ", "").replace("+", "")=="[" and b==0 and not brackets:
							b=+1
						elif b==1:
							b=0
							if l.replace(" ", "").replace("+", "")=="[":
								brackets=True
				print(str(us['name'])) 
				print("AGGIUNTO:")
				print(add)
				print("RIMOSSO:")
				print(rem)
				print("COLLEGAMENTI:")
				print(links)
						
				#controlli <-----------------------------------------------------------
				if rc["ns"]%2==0:
					if not (rc["ns"]==3 and DATA5['query']['pages'][0]['title'].replace("User:", "").replace("Utente:", "") == rc['user']):
						disambigua(links, rc['user'])
						linkfile(add, rc['user'])
						citaweb(add, rc['user'])
						wrongref(add, rc['user'])
						sectionlink(add, rc['user'])
						if rc['ns']==14: #categoria
							linkcat(links, rc['user'])
						if newpage:
							sezionistandard(add, rc['user'])
							traduzioneerrata(add, rc['user'])
							if "contenttranslation" in rc['tags']:
								tradottoda(DATA5['query']['pages'][0]['title'], rc['user'])

				else:#discussioni
					if DATA5['query']['pages'][0]['title'].replace("User talk:", "").replace("Discussioni utente:", "") == rc['user']:
						print("TALK")
				#fine ----------------------------------------------------------------
				
			else:
				print("NO - "+str(us['name']))
		else:
			print("NO - "+str(us['name']))
		print("-"*10)
#aggiungi messaggi
for user in messages:
	txt="\n\n== Aiuto ==\n\nCiao {{subst:ROOTPAGENAME}}, ti scrivo in quanto ho notato che hai effettuato degli errori comuni ai nuovi utenti, permettimi di spiegarti il problema nei dettagli!"
	
	#todo: controlla benvenuto; api edit

	for text in messages[user]:
		txt=txt+"\n\n"+text

	#Edit
	if user=="ValeJappo":#DEBUG <--- todo: rimuovere
		PARAMS_EDIT = {
			"action": "edit",
			"title": "User talk:"+user,
			"token": crsf_login(),
			"format": "json",
			"appendtext": txt+"\n\n--~~~~"
		}
		R = S.post(URL, data=PARAMS_EDIT)

os.system("python3 update_timestamp.py")
