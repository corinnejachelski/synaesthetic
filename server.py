from flask import Flask, redirect, request, render_template, session
#from jinja2 import StrictUndefined
import json

from pprint import pformat, pprint
import os
import requests
import sys
import spotipy
import spotipy.util as util


app = Flask(__name__)
app.secret_key = 'SECRETSECRETSECRET'

# This configuration option makes the Flask interactive debugger
# more useful (you should remove this line in production though)
#app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True

# This option will cause Jinja to throw UndefinedErrors if a value hasn't
# been defined (so it more closely mimics Python's behavior)
#app.jinja_env.undefined = StrictUndefined


# This option will cause Jinja to automatically reload templates if they've been
# changed. This is a resource-intensive operation though, so it should only be
# set while debugging.
#app.jinja_env.auto_reload = True

@app.route('/')
def display_homepage():

    return render_template('homepage.html')


@app.route('/my-data')
def display_data():

    return render_template('homepage.html')


# scope = "user-library-read"

# if len(sys.argv) > 1:
#     username = sys.argv[1]
# else:
#     print("Usage %s username" % (sys.argv[0],))

# token = util.prompt_for_user_token(username,scope)

# if token:
#     sp = spotipy.Spotify(auth=token)
#     results = sp.current_user_saved_tracks()
#     for item in results["items"]:
#         track = item["track"]
#         print(track["name"] + " - " + track["artists"][0]["name"])
# else:
#     print("Cant get token for", username)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
