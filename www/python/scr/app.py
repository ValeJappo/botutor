import json
import os
from flask import Flask
from flask import render_template
from flask_mwoauth import MWOAuth
from configparser import ConfigParser
import feedparser
from flask import Markup


url= "https://it.wikipedia.org/w/api.php?hidebots=1&hidecategorization=1&hideWikibase=1&urlversion=1&days=30&limit=50&action=feedrecentchanges&feedformat=atom"
feed = feedparser.parse(url)


app = Flask(__name__)

# Generate a random secret application key
#
# NOTE: this key changes every invocation. In an actual application, the key
# should not change! Otherwise you might get a different secret key for
# different requests, which means you can't read data stored in cookies,
# which in turn breaks OAuth.
#
# So, for an actual application, use app.secret_key = "some long secret key"
# (which you could generate using os.urandom(24))
#
app.secret_key = os.urandom(24)

print("""
NOTE: The callback URL you entered when proposing an OAuth consumer
probably did not match the URL under which you are running this development
server. Your redirect back will therefore fail -- please adapt the URL in
your address bar to http://localhost:5000/oauth-callback?oauth_verifier=...etc
""")
config_object = ConfigParser()
config_object.read("keys.conf")
keys = config_object["KEYS"]
print(keys["consumer_key"])
mwoauth = MWOAuth(base_url='https://test.wikipedia.org/w',clean_url='https://test.wikipedia.org/wiki',consumer_key=keys["consumer_key"],consumer_secret=keys["consumer_secret"])   
app.register_blueprint(mwoauth.bp)


@app.route("/")
def index():
    user=None
    if repr(mwoauth.get_current_user(True))!="None":
        user=repr(mwoauth.get_current_user(True)).replace("'", "")
    return render_template('home.html', user=user)

@app.route("/modifiche")
def modifiche():
    user=None
    if repr(mwoauth.get_current_user(True))!="None":
        user=repr(mwoauth.get_current_user(True)).replace("'", "")
    return render_template('modifiche.html', user=user, feed=feed)

@app.route("/test_query")
def test_query():
    username = mwoauth.get_current_user(True)
    crsf=mwoauth.request({
		"action": "query",
		"meta": "tokens",
		"format": "json"
	})
    token=json.loads(crsf)['query']['tokens']['csrftoken']
    data = mwoauth.request({
			"action": "edit",
			"title": "Test",
            "summary": "Test oauth",
			"token": str(token),
			"format": "json",
			"appendtext": "test"
		})
    return data

if __name__ == "__main__":
    app.run(debug=True, threaded=True)