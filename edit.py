import requests

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
    'lgname':"BOTutor",
    'lgpassword':PASSWORD,
    'lgtoken':LOGIN_TOKEN,
    'format':"json"
}

R = S.post(URL, data=PARAMS1)
DATA = R.json()

print(DATA)
