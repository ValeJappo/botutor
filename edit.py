import requests
import os

if os.environ.get('BOTUSERNAME', 'Not Set') == 'Not Set':
    os.environ['BOTUSERNAME'] = str(input("Username: "))
if os.environ.get('BOTPASSWORD', 'Not Set') == 'Not Set':
    os.environ['BOTPASSWORD'] = str(input("Password: "))
    
print("Logging in as "+str(os.environ.get('BOTUSERNAME'))+" with password "+str(os.environ.get('BOTPASSWORD')))
S = requests.Session()
URL = "https://test.wikipedia.org/w/api.php"

# token
PARAMS0 = {
    'action':"query",
    'meta':"tokens",
    'type':"login",
    'format':"json"
}

R = S.get(url=URL, params=PARAMS0)
DATA = R.json()

LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

print(LOGIN_TOKEN)

# Login

PARAMS1 = {
    'action':"login",
    'lgname':str(os.environ.get('BOTUSERNAME')),
    'lgpassword':str(os.environ.get('BOTPASSWORD')),
    'lgtoken':LOGIN_TOKEN,
    'format':"json"
}

R = S.post(URL, data=PARAMS1)
DATA = R.json()

print(DATA)
