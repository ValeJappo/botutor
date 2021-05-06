import requests
import json

S = requests.Session()
URL = "https://it.wikipedia.org/w/api.php"

PARAMS={
	"action": "parse",
	"format": "json",
	"page": "User:BOTutor/Messaggi",
	"prop": "wikitext",
	"formatversion": "2"
}
R = S.get(url=URL, params=PARAMS)
DATA = R.json()
with open('messages.json', "w") as myfile:
    myfile.write(DATA["parse"]["wikitext"])
