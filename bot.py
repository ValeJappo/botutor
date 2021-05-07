import requests
import os
import difflib
import json
from tinydb import TinyDB, Query
from configparser import ConfigParser
from pywikibot.comms.eventstreams import EventStreams

#Define global variables
messages=[]

currentRevID=0#Testing purposes
revids={}

#Get bot's login credentials
config_object = ConfigParser()
config_object.read("config.conf")
info = config_object["INFO"]
username=str(info["username"])
password=str(info["password"])

#API setup
S = requests.Session()
URL = "https://"+str(info["site"])+".wikipedia.org/w/api.php"

#Rules
def disambigua(links, user):
	for link in links:
		try:
			PARAMS={
				"action": "query",
				"format": "json",
				"prop": "templates",
				"titles": link["link"].replace("/wiki/", ""),
				"formatversion": "latest",
				"tltemplates": "Template:Disambigua"
			}
			R = S.get(url=URL, params=PARAMS)
			DATA = R.json()
			if DATA['query']['pages'][0]['templates'][0]['title']=="Template:Disambigua" and not link["external"]:
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
		if link["link"].find(":") < 0 and not link["external"]:
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

def sezionistandard(add, user):
	sections=[]
	if (add.replace(" ", "").lower().find("==note==")) > 0:
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

def extlink(links, revid, user):
	PARAMS={
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"revids": str(revid),
		"formatversion": "2",
		"rvprop": "content",
		"rvslots": "*"
	}
	R = S.get(url=URL, params=PARAMS)
	DATA = R.json()
	content=DATA["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
	for link in links:
		if link["external"]:
			if content.lower().replace(" ", "").find(link["link"].lower().replace(" ", "")) < content.lower().replace(" ", "").find("==collegamentiesterni==") and (content.find("</ref", content.find(link["link"])) >= content.find("<ref", content.find(link["link"], content.find("<references")-1)))  and (content.find("}}", content.find(link["link"])) >= content.find("{{", content.find(link["link"]))) and content.find(link["link"]) != -1:
				msg(user, "EXTLINK")

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
	if add.replace(" ", "").lower().find("==riferimenti==") > 0 or add.replace(" ", "").lower().find("==linkesterni==") > 0:
		msg(user, "TRADUZIONEERRATA")

def firma(add, rc):
	if add.find(":"+rc['user']) == -1 and len(add)>20: #Not signed
		try:
			PARAMS={
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"revids": rc['revision']["old"],
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

def ping(add, rc, isUserTalk, tags):
	if isUserTalk and len(add)>20: #Is user talk
		try:
			PARAMS={
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"revids": rc['revision']["old"],
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
				if "discussiontools-visual" in tags:
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
		global messages
		try: #add id to the messages queue
			messages.append(text)
		except KeyError:
			messages=[text]

		#Testing purposes
		try:
			revids[user].append(currentRevID)
		except KeyError:
			revids[user]=[currentRevID]

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

namespaces = [0,1,2,3,5,7,9,11,13,14,15,14,101,103,829]
stream = EventStreams(streams=['recentchange', 'page-links-change'])
for rc in stream:
	streamlink=False
	try:
		if rc["server_name"] != str(info["site"])+'.wikipedia.org' or (rc["type"] != "edit" and rc["type"] != "new"):
			continue
	except KeyError:
		if rc["meta"]["domain"] != str(info["site"])+'.wikipedia.org':
			continue
		streamlink=True
	
	if streamlink:
		rc["patrolled"]=False
		rc["namespace"]=rc["page_namespace"]
		rc["user"]=rc["performer"]["user_text"]
		rc["revision"]={"new":rc["rev_id"]}
		try:
			test=rc["added_links"]
		except KeyError:
			continue

	if rc['patrolled'] or rc['namespace'] not in namespaces:
		continue

	print(rc["user"])
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
	
	#API revisions
	PARAMS5={
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"formatversion": "latest",
		"rvprop": "content|oresscores|sha1|tags",
		"rvslots": "*"
	}
	try:
		PARAMS5["revids"]=str(rc['revision']['new'])+"|"+str(rc['revision']['old'])
	except KeyError:
		PARAMS5["revids"]=str(rc['revision']['new'])

	R = S.get(url=URL, params=PARAMS5)
	DATA5 = R.json()
	currentRevID=rc['revision']['new'] #Testing purposes
	try:#Get edit's ores score
		score=float(DATA5['query']['pages'][0]['revisions'][1]['oresscores']['goodfaith']['true'])
		tags=DATA5['query']['pages'][0]['revisions'][1]['tags']
	except IndexError: #New page
		try: 
			score=float(DATA5['query']['pages'][0]['revisions'][0]['oresscores']['goodfaith']['true'])
			tags=DATA5['query']['pages'][0]['revisions'][0]['tags']
		except TypeError: #Something went wrong
			if DATA5['query']['pages'][0]['revisions'][0]['oresscores'] == []:
				score=1
				tags=DATA5['query']['pages'][0]['revisions'][0]['tags']
	except TypeError: #Something went wrong
		if DATA5['query']['pages'][0]['revisions'][0]['oresscores'] == []:
			score=1
			tags=DATA5['query']['pages'][0]['revisions'][1]['tags']
	except: #page deleted
		print("Error")
		continue
	
	#Check if the edit should be considered
	if (edcount >= 100) or ("mw-reverted" in tags) or ("mw-undo" in tags) or ("mw-manual-revert" in tags) or isbot or score < 0.3:
		continue

	if not streamlink:
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

		#Get diff's added, removed and linked text
		for l in diff: #For each character
			if l.startswith('+ ') or len(l)==1: #is added or new page
				#Add to add the added text
				add=add+l.replace('+ ', '')

			if l.startswith('- '): #is removed
				#Add to rem the removed text
				rem=rem+l.replace('- ', '')

		#Print collected data (log)
		print(str(us['name'])+" - "+"{{diff|"+str(rc['revision']['new'])+"}}") 
		print("ADDED:")
		print(add)
		print("REMOVED:")
		print(rem)
				
		#Call check functions
		if rc["namespace"]%2==0: #Not talks
			if not (rc["namespace"]==3 and DATA5['query']['pages'][0]['title'].replace("User:", "").replace("Utente:", "") == rc['user']): #User but not userpage
				if rc['namespace']==0 or rc['namespace']==2:
					linkfile(add, rc['user'], 'visualeditor' in tags)
					citaweb(add, rc['user'])
					wrongref(add, rc['user'], 'visualeditor' in tags)
					sectionlink(add, rc['user'])

				if newpage: #New page
					sezionistandard(add, rc['user'])
					traduzioneerrata(add, rc['user'])
					if "contenttranslation" in tags and rc["namespace"]==0: #Content translation
						tradottoda(DATA5['query']['pages'][0]['title'], rc['user'])

		else: #Talks
			firma(add, rc)
			ping(add, rc, DATA5['query']['pages'][0]['title'].replace("User talk:", "").replace("Discussioni utente:", "") == rc['user'], tags)
	else: # If streamlinks
		#Call check functions
		if rc['namespace']==0 or rc['namespace']==2:
			disambigua(rc["added_links"], rc['user'])
			extlink(rc["added_links"], rc["revision"]["new"], rc['user'])

		elif rc['namespace']==14: #Category
				linkcat(rc["added_links"], rc['user'], 'visualeditor' in tags)
				extlink(rc["added_links"],rc["revision"]["new"], rc['user'])
		

	#Divisor (log)
	print("-"*10)

	#Write messages
	txt="\n\n== Aiuto ==\n\n"+"(Utente: "+rc["user"]+"; RevID: "+str(rc["revision"]["new"])+")"+"Ciao {{subst:ROOTPAGENAME}}, questo è un messaggio automatizzato; ti scrivo in quanto ho notato che hai effettuato degli errori comuni ai nuovi utenti, permettimi di spiegarti il problema nei dettagli!"
	#                          ^ Testing purposes

	#Check if page exists
	PARAMS_CHECK={
	"action": "query",
	"format": "json",
	"prop": "",
	"titles": "User talk:"+rc["user"],
	"formatversion": "2"
	}
	R = S.get(url=URL, params=PARAMS_CHECK)
	DATA = R.json()
	try:
		if DATA["query"]["pages"][0]["missing"] == True:
			txt="{{subst:Benvenuto}}\n"+txt
	except KeyError:
		pass
	#Edit
	warn=False
	for text in messages:
		txt=txt+"\n\n"+text
		warn=True
	if warn:
		PARAMS_EDIT = {
			"action": "edit",
			"title": "User:BOTutor/Prove",#Testing purposes# "User talk:"+user,
			"token": crsf_login(),
			"format": "json",
			"summary": "Consiglio",
			"appendtext": txt+"\n\n--[[User:BOTutor|BOTutor]] (<small>messaggio automatico: [[User talk:BOTutor|segnala un problema]] · [[Aiuto:Sportello informazioni|chiedi aiuto]]</small>) ~~~~~"
		}
		R = S.post(URL, data=PARAMS_EDIT)
		messages=[]