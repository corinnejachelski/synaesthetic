from flask import Flask, redirect, request, render_template, session
#from jinja2 import StrictUndefined
import json

from pprint import pformat, pprint
import os
import requests
import sys
import spotipy
import spotipy.util as util
import auth

# scope = 'user-top-read user-library-read playlist-read-public user-follow-read'

# Client keys
SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI='http://localhost:5000/callback'
SCOPE = 'user-library-read'

username = "Corinne Jachelski"



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


@app.route('/login')
def login():
    oauth = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                    client_secret=SPOTIPY_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_REDIRECT_URI,
                                    scope=SCOPE,
                                    username=username)

    # token = oauth.get_access_token(username)

    auth_url = oauth.get_authorize_url()
    #returns a server error OSError: [Errno 98] Address already in use
    # res = oauth.get_auth_response()
    #returns a server error OSError: [Errno 98] Address already in use
    # code = oauth.get_authorization_code()

    # token = oauth.get_cached_token()
    # token = oauth.get_access_token(code)

    print("\n\n\n\n\n\n\n\n\n\n\n")
    print(auth_url)
    # print("\n\n\n\n\n\n\n\n\n\n\n")
    # print(f"code: {code}")
    # print("\n\n\n\n\n\n\n\n\n\n\n")
    # print(f"token: {token}")
    # print(dir(oauth))
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """"GET /callback?code=AQAb6q2K_.... HTTP/1.1" 200 -
    code shows up in callack route request
    oauth object does not exist in this route"""

    code = oauth.get_authorization_code()
    print("\n\n\n\n\n\n\n\n\n\n\n")
    print(code)

    return render_template('circle-pack.html')

@app.route('/my-data')
def display_data():

    return render_template('circle-pack.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
