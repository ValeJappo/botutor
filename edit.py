import requests
import os
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.conf")
userinfo = config_object["INFO"]
username=str(userinfo["username"]))
username=str(userinfo["password"]))
print("Logging in as "+username+" with password "+password)
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
print(DATA1)
#Token CSRF
PARAMS2 = {
    "action": "query",
    "meta": "tokens",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS2)
DATA2 = R.json()

CSRF_TOKEN = DATA2['query']['tokens']['csrftoken']

#Edit
PARAMS3 = {
    "action": "edit",
    "title": "Test",
    "token": CSRF_TOKEN,
    "format": "json",
    "appendtext": "Test"
}

R = S.post(URL, data=PARAMS3)
DATA3 = R.json()

print(DATA3)
