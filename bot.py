import requests
import os
import difflib
import json
from tinydb import TinyDB, Query
from configparser import ConfigParser

#Define global variables
messages={}

#Get bot's login credentials
config_object = ConfigParser()
config_object.read("config.conf")
info = config_object["INFO"]
username=str(info["username"])
password=str(info["password"])

#API setup
S = requests.Session()
URL = "https://"+str(info["site"])+".wikipedia.org/w/api.php"

#Check functions
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
	
def linkfile(add, user, ve):
	if add.lower().replace(" ", "").find("immagine=http") >= 0:
			msg(user, "LINKFILE_TMP")
	elif add.find("upload.wikimedia.org") >= 0:
		if ve:
			msg(user, "LINKFILE_VE")
		else:
			msg(user, "LINKFILE")

def linkcat(links, user, ve):
	for link in links:
		if link.find(":") < 0:
			if ve:
				msg(user, "LINKCAT_VE")
			else:
				msg(user, "LINKCAT")

def citaweb(add, user):
	if add.find("<ref>[http://") >= 0 or add.find("<ref>http://") >= 0:
		msg(user, "CITAWEB")	

def wrongref(add, user, ve):
	if add.find("[1]") >=0 and add.find("[2]") >= 0 and add.find("[[1]]") < 0 and add.find("[[2]]") < 0:
		if ve:
			msg(user, "WRONGREF_VE")
		else:
			msg(user, "WRONGREF")

def sectionlink(add, user):
	if add.replace(" ", "").find("==[[") >=0 and add.replace(" ", "").find("]]==") >=0:
		msg(user, "SECTIONLINK")

def sectionformat(add, user):
	if add.replace(" ", "").find("==''") >=0 and add.replace(" ", "").find("''==") >=0:
		msg(user, "SECTIONFORMAT")

def sezionistandard(add, user): #todo: fix
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

def extlink(add, user):
	edindex=add.replace(" ", "").lower().find("==collegamentiesterni==")
	if edindex==-1:
		edindex=len(add.replace(" ", ""))-1
	stindex1=0
	stindex2=0
	while add.replace(" ", "").lower().find("http://", stindex1, edindex)!=-1 or add.replace(" ", "").lower().find("https://", stindex2, edindex)!=-1:
		if add.replace(" ", "").lower().find("http://", stindex1, edindex)>1:
			if add.replace(" ", "")[add.replace(" ", "").lower().find("http://", stindex1, edindex)-1]!="=" and add.replace(" ", "")[add.replace(" ", "").lower().find("http://", stindex1, edindex)-1]!=">" and add.replace(" ", "")[add.replace(" ", "").lower().find("http://", stindex1, edindex)-2]!="=" and add.replace(" ", "")[add.replace(" ", "").lower().find("http://", stindex1, edindex)-1]!=">":
				msg(user, "EXTLINK")
				return None
			else:
				stindex1=add.replace(" ", "").lower().find("http://", stindex1, edindex)+1
		if add.replace(" ", "").lower().find("https://", stindex2, edindex)>1:
			if add.replace(" ", "")[add.replace(" ", "").lower().find("https://", stindex2, edindex)-1]!="=" and add.replace(" ", "")[add.replace(" ", "").lower().find("https://", stindex2, edindex)-1]!=">" and add.replace(" ", "")[add.replace(" ", "").lower().find("https://", stindex2, edindex)-2]!="=" and add.replace(" ", "")[add.replace(" ", "").lower().find("https://", stindex2, edindex)-1]!=">":
				msg(user, "EXTLINK")
				return None
			else:
				stindex2=add.replace(" ", "").lower().find("https://", stindex2, edindex)+1

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

def firma(add, rc):
	if (add.find(":"+rc['user']) == -1): #Not signed
		try:
			PARAMS={
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"revids": rc['old_revid'],
			"formatversion": "2",
			"rvprop": "user",
			"rvslots": "main"
			}
			R = S.get(url=URL, params=PARAMS)
			DATA = R.json()
			if DATA['query']['pages'][0]['revisions'][0]['user'] != rc['user']: #If previous edit is not by this user
				msg(rc['user'], "FIRMA")
		except KeyError:#New page
			pass

def ping(add, rc, isUserTalk):
	if isUserTalk and len(add)>20: #Is user talk or is signed
		try:
			PARAMS={
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"revids": rc['old_revid'],
			"formatversion": "2",
			"rvprop": "user",
			"rvslots": "main"
			}
			R = S.get(url=URL, params=PARAMS)
			DATA = R.json()
			isPreviousEditOk=DATA['query']['pages'][0]['revisions'][0]['user'] != rc['user'] #If previous edit is not by this user
		
		except KeyError:#New page
			isPreviousEditOk=True

		if isPreviousEditOk:
			if add.lower().replace("utente:", "user:").find("user:") == add.lower().replace("utente:", "user:").find("user:"+rc['user'].lower()) and add.lower().replace(" ","").replace("{{at|", "{{ping|").replace("{{replyto|", "{{ping|").find("{{ping|") == -1: #If nobody is mentioned
				if "discussiontools-visual" in rc['tags']:
					msg(rc['user'], "PING_VE")
				else:
					msg(rc['user'], "PING")

#Send message function
def msg(user, msgid):
	#read json
	db = TinyDB('users.json')
	User = Query()
	with open('messages.json', encoding="utf-8") as f:
		data = json.load(f)
		text=data[msgid]
	notwarned=True

	try: #bool=!the user has ever been warned with msgid
		notwarned=not db.search(User.name == str(user))[0][str(msgid.replace("_VE", ""))]
	except (IndexError, KeyError) as e: #User not included in the file
		notwarned=True

	if notwarned:
		print(msgid)
		#add user/msgid:true to json
		db.upsert({'name': str(user), str(msgid.replace("_VE", "")): True}, User.name == str(user))
		try: #add id to the messages for the user
			messages[user].append(text)
		except KeyError:
			messages[user]=[text]

#Login function
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
		print("Login error.")
		print(DATA1)
		raise SystemExit

	#Token CSRF
	PARAMS2 = {
		"action": "query",
		"meta": "tokens",
		"format": "json"
	}

	R = S.get(url=URL, params=PARAMS2)
	DATA2 = R.json()

	#Return token
	return DATA2['query']['tokens']['csrftoken']


#Analyze recent changes

#Recentchanges API
PARAMS3 ={
	"action": "query",
	"format": "json",
	"list": "recentchanges",
	"continue": "-||",
	"rcprop": "title|user|userid|timestamp|flags|tags|ids",
	"rctype": "edit|new",
	"rclimit": "max",
	"rcdir" : "newer",
	"rcnamespace": "0|1|2|3|5|7|9|11|13|14|15|14|101|103|829"
}

#Get last update's timestamp
try:
	PARAMS3["rcstart"]=str(config_object["DATA"]["timestamp"]) #Add to API's params
	lasttimestamp=str(config_object["DATA"]["timestamp"])
except (KeyError, NameError) as error: #There is no timestamp
	os.system("python3 update_timestamp.py")
	raise SystemExit

#API Request
R = S.get(url=URL, params=PARAMS3)
DATA3 = R.json()
RECENTCHANGES = DATA3['query']['recentchanges']

#For each edit
for rc in RECENTCHANGES:
	#Get user's infos
	PARAMS4={
		"action": "query",
		"format": "json",
		"list": "users",
		"usprop": "blockinfo|editcount|gender|groups",
		"ususers": rc['user']
	}
	R = S.get(url=URL, params=PARAMS4)
	DATA4 = R.json()
	us=DATA4['query']['users'][0]

	try:
		edcount=us['editcount'] #Get edits' number
		isbot="bot" in us['groups'] #Check if bot
	except KeyError: #Anonym users
		edcount=0
		isbot=False

	if rc['user']=="ValeJappo":	#DEBUG <-- todo: rimuovere
		edcount=0				#DEBUG

	#Check if the edit should be considered
	if (edcount < 100) and (rc['timestamp']!=lasttimestamp) and (not "mw-reverted" in rc["tags"]) and (not "mw-undo" in rc["tags"]) and (not "mw-manual-revert" in rc["tags"]) and (not isbot):
		#API revisions
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
		
		try:#Get edit's ores score
			score=float(DATA5['query']['pages'][0]['revisions'][1]['oresscores']['goodfaith']['true'])
		except IndexError: #New page
			score=float(DATA5['query']['pages'][0]['revisions'][0]['oresscores']['goodfaith']['true'])
		except: #page deleted
			print("Error")
			break

		if rc['user']=="ValeJappo":	#DEBUG <-- todo: rimuovere
			score=1					#DEBUG
		
		#Check if the edit should be considered
		if score >= 0.3:
			#Get the differences
			c1=DATA5['query']['pages'][0]['revisions'][0]['slots']['main']['content'] #Content after the edit
			try: 
				c2=DATA5['query']['pages'][0]['revisions'][1]['slots']['main']['content'] #Content before the edit
				#Get diff
				diff=difflib.ndiff(c1, c2)
				newpage=False
			except IndexError: #New page
				diff=c1 #diff = content
				newpage=True

			"""
			Diffs' format:

			Added character			+ c		(+_c)
			Removed character		- c		(-_c)
			Unchanged character		  c		(__c)


			New pages' format:

			Character				c		 (c)
			"""

			#Define variables
			add=""
			rem=""
			links=[]
			il=0
			b=0
			brackets=False
			#todo: ferma ascolto anche con #
			#Get diff's added, removed and linked text
			for l in diff: #For each character
				#Record link
				if brackets and l.replace('+ ', '').replace('  ', '') != "]" and l.replace('+ ', '').replace(' ', '') != "|" and not l.startswith('- '):
					if len(l)>1: #Length is > 1 if it is formatted by the diff (+/-/_ _ char)
						l=l[2:] #Remove first two characters
					try: #Add character to current link
						links[il]=links[il]+l
					except IndexError: #New link (first character)
						links.append(l)
				
				#Detect closed bracket
				if l.replace('+ ', '').replace(' ', '') == "]" and b==0 and brackets:
					b=-1

				#Detect second closed bracket	
				if b==-1:
					b=0 #Initialize brackets counter
					#Stop recording link
					if (l.replace('+ ', '').replace(' ', '') == "]" and brackets) or (l.replace(" ", "").replace("+", "") == "|" and brackets):
						il=il+1
						brackets=False
				
				#Detect pipe
				if brackets:
					b=0 #Initialize brackets counter
					#Stop recording link
					if l.replace("  ", "").replace("+ ", "") == "|":
						il=il+1
						brackets=False

				if l.startswith('+ ') or len(l)==1: #is added or new page
					#Add to add the added text
					add=add+l.replace('+ ', '')

					#Detect bracket
					if l.replace('+ ', '') == "[" and b==0 and not brackets:
						b=+1

					#Detect second bracket
					elif b==1 and not brackets:
						b=0 #Initialize brackets counter
						#Start recording link
						if l.replace('+ ', '') == "[": 
							brackets=True	

				if l.startswith('- '): #is removed
					#Add to rem the removed text
					rem=rem+l.replace('- ', '')

			#Print collected data (debug)
			print(str(us['name'])+" - "+"{{diff|"+str(rc['revid'])+"}}") 
			print("ADDED:")
			print(add)
			print("REMOVED:")
			print(rem)
			print("LINKS:")
			print(links)
					
			#Call check functions
			if rc["ns"]%2==0: #Not talks
				if not (rc["ns"]==3 and DATA5['query']['pages'][0]['title'].replace("User:", "").replace("Utente:", "") == rc['user']): #User but not userpage
					if rc['ns']==0 or rc['ns']==2:
						disambigua(links, rc['user'])
						linkfile(add, rc['user'], 'visualeditor' in rc['tags'])
						citaweb(add, rc['user'])
						wrongref(add, rc['user'], 'visualeditor' in rc['tags'])
						sectionlink(add, rc['user'])
						extlink(add, rc['user'])
					elif rc['ns']==14: #Category
						linkcat(links, rc['user'], 'visualeditor' in rc['tags'])
					if newpage: #New page
						sezionistandard(add, rc['user'])
						traduzioneerrata(add, rc['user'])
						if "contenttranslation" in rc['tags'] and rc["ns"]==0: #Content translation
							tradottoda(DATA5['query']['pages'][0]['title'], rc['user'])

			else: #Talks
				firma(add, rc)
				ping(add, rc, DATA5['query']['pages'][0]['title'].replace("User talk:", "").replace("Discussioni utente:", "") == rc['user'])

			#divisor (debug)
			print("-"*10)

#Write messages
for user in messages:
	txt="\n\n== Aiuto ==\n\nCiao {{subst:ROOTPAGENAME}}, ti scrivo in quanto ho notato che hai effettuato degli errori comuni ai nuovi utenti, permettimi di spiegarti il problema nei dettagli!"
	
	#Check if page exists
	PARAMS_CHECK={
	"action": "query",
	"format": "json",
	"prop": "",
	"titles": "User talk:"+user,
	"formatversion": "latest"
	}
	R = S.get(url=URL, params=PARAMS_CHECK)
	DATA = R.json()
	try:
		txt="{{subst:Benvenuto}}\n"+txt
	except KeyError:
		pass
	#Edit
	for text in messages[user]:
		txt=txt+"\n\n"+text
	if user=="ValeJappo" and str(info["site"])=="test":#DEBUG <--- todo: rimuovere
		PARAMS_EDIT = {
			"action": "edit",
			"title": "User talk:"+user,
			"token": crsf_login(),
			"format": "json",
			"summary": "Consiglio",
			"appendtext": txt+"\n\n--[[User:BOTutor|BOTutor]] (<small>messaggio automatico: [[User talk:BOTutor|segnala un problema]] · [[Aiuto:Sportello informazioni|chiedi aiuto]]</small>) ~~~~~"
		}
		R = S.post(URL, data=PARAMS_EDIT)
#Set current timestamp as last update's timestamp
os.system("python update_timestamp.py")