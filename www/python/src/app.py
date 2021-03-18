import json
from github_webhook import Webhook
import os
from flask import Flask
from flask import render_template
from flask_mwoauth import MWOAuth
from configparser import ConfigParser
import toolforge
from tinydb import TinyDB, Query
from flask import Markup

app = Flask(__name__)
webhook = Webhook(app)

# Get keys
config_object = ConfigParser()
config_object.read("keys.conf")
keys = config_object["KEYS"]

# Secret application key
app.secret_key = keys["app_secret"]

# OAuth
mwoauth = MWOAuth(base_url='https://it.wikipedia.org/w',clean_url='https://it.wikipedia.org/wiki',consumer_key=keys["consumer_key"],consumer_secret=keys["consumer_secret"])   
app.register_blueprint(mwoauth.bp)

# Get OAuth user
def getUser():
    if repr(mwoauth.get_current_user(True))!="None":
        return repr(mwoauth.get_current_user(True)).replace("'", "")
    else:
        return None


# Push github changes
@webhook.hook()
def on_push(data):
    os.system("cd $HOME && git pull origin master")

# Main
@app.route("/")
def index():
    return render_template('home.html', user=getUser())

@app.route("/action/segui/<string:user>/<string:tag>")
def segui(user=None, tag=None):
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

# Tests
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

# Debug
if __name__ == "__main__":
    app.run(debug=True, threaded=True)