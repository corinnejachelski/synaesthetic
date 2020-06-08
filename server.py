from flask import Flask, redirect, request, render_template, session
#from jinja2 import StrictUndefined
import json

from pprint import pformat, pprint
import os
import requests
import sys
import spotipy
import spotipy.util as util
# scope = 'user-top-read user-library-read playlist-read-public user-follow-read'

# Client keys
SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI='http://localhost:5000/callback'
SCOPE='user-top-read'
#username of account associated with Spotify Developer dashboard
USERNAME=os.environ['USERNAME']

#Implements Authorization Code Flow for Spotify’s OAuth implementation.
OAUTH = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                    client_secret=SPOTIPY_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_REDIRECT_URI,
                                    scope=SCOPE,
                                    username=USERNAME)



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
    """Authorizes Spotify user login"""

    auth_url = OAUTH.get_authorize_url()

    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Spotify redirect URI"""

    code = request.args.get("code")
    token = OAUTH.get_access_token(code)
    session["access_token"] = token["access_token"]
    session["refresh_token"] = token["refresh_token"]

    #Spotipy client Module for Spotify Web API
    sp = spotipy.Spotify(auth=session["access_token"], oauth_manager=OAUTH)

    #Get current user's top 50 artists
    # user_artists = sp.current_user_top_artists(limit=50)

    # print(user_artists)

    #Get detailed profile information about the current user
    user_info = sp.me()
    print(user_info)
    display_name = user_info["display_name"]
    session["user_id"] = user_info["id"]
    image_url = user_info["images"][0]["url"]
    print(session)

    return render_template('circle-pack.html')


@app.route('/my-data')
def display_data():

    return render_template('circle-pack.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
