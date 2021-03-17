import json
from github_webhook import Webhook
import os
from flask import Flask
from flask import render_template
from flask_mwoauth import MWOAuth
from configparser import ConfigParser
import feedparser
import toolforge
from tinydb import TinyDB, Query
from flask import Markup


url= "https://it.wikipedia.org/w/api.php?hidebots=1&hidecategorization=1&hideWikibase=1&urlversion=1&days=30&limit=50&action=feedrecentchanges&feedformat=atom"
feed = feedparser.parse(url)


app = Flask(__name__)
webhook = Webhook(app)
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

@webhook.hook()
def on_push(data):
    os.system("cd $HOME && git pull origin master")

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

@app.route("/segui")
def segui():
    user=None
    if repr(mwoauth.get_current_user(True))!="None":
        user=repr(mwoauth.get_current_user(True)).replace("'", "")

        return render_template('segui.html', user=user)

@app.route("/segui/<target>")
def seguitarget(target=None):
    user=None
    if repr(mwoauth.get_current_user(True))!="None":
        user=repr(mwoauth.get_current_user(True)).replace("'", "")
        

        return render_template('segui-action.html', user=user, target=target)


@app.route("/test_query")
def test_query():
    crsf=mwoauth.request({
		"action": "query",
		"meta": "tokens",
		"format": "json"
	})
    token=json.loads(crsf)['query']['tokens']['csrftoken']
    data = mwoauth.request({
			"action": "edit",
			"title": "User:"+repr(mwoauth.get_current_user(True)).replace("'", "")+"/Sandbox",
            "summary": "Test oauth",
			"token": str(token),
			"format": "json",
			"appendtext": "test"
		})
    return data
@app.route("/test")
def test():
    user=None
    if repr(mwoauth.get_current_user(True))!="None":
        user=repr(mwoauth.get_current_user(True)).replace("'", "")
        
    return render_template('home.html', user="Testing-User")

@app.route("/data/<file>")
def data(file=None):
    if(file.find(".json") and repr(mwoauth.get_current_user(True)).replace("'", "")!="None"):
        try:
            return render_template(file)
        except:
            return "{'error': 'invalid request.'}"
    else:
        return "{'error': 'invalid request.'}"


@app.route("/action/segui/<string:user>/<string:tag>")
def segui_route(user=None, tag=None):
    oauth_user=str(repr(mwoauth.get_current_user(True))).replace("'", "")
    if(oauth_user!="None" or True):
        db = TinyDB('segui.json')
        User = Query()
        try:
            u_tag=db.search(Query()['name'] == user)[0][tag]
        except (IndexError, KeyError) as e:
            u_tag=[]
        if tag != "rimuovi":
            if not oauth_user in u_tag:
                u_tag.append(oauth_user)
                db.upsert({'name': str(user), str(tag): u_tag}, User.name == user)
                return '{"status": "success"}'
            else:
                return '{"status": "duplicate"}'
        else:
            for item in db.search(Query()['name'] == user)[0]:
                try:
                    try:
                        db.search(Query()['name'] == user)[0][item].remove(oauth_user)
                        db.upsert({'name': user, item: u_tag}, User.name == user)
                    except AttributeError:
                        pass
                except ValueError:
                    pass
            return '{"status": "success"}'
        return '{"status": "error"}'
    else:
        return '{"status": "login"}'
        
if __name__ == "__main__":
    app.run(debug=True, threaded=True)