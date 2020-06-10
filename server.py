from flask import Flask, jsonify, redirect, request, render_template, session
#from jinja2 import StrictUndefined
import json

from pprint import pformat, pprint
import os
import requests
import sys
import spotipy
#API helper functions
import spotify_api
import crud
from model import connect_to_db


# Client keys
SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI='http://localhost:5000/callback'
SCOPE='user-top-read'
# scope = 'user-top-read user-library-read playlist-read-public user-follow-read'
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

    print(session)
    
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

    #get current user's profile info
    user_id, display_name, image_url = spotify_api.get_user_profile(sp)
    #save user to session to pass as argument across functions
    session["user_id"] = user_id

    #add user to db
    crud.create_user(user_id, display_name, image_url)
    print(user_id, display_name, image_url)

    #get current user's top 50 artists
    user_artists = sp.current_user_top_artists(limit=50)
    print(user_artists)
    #add artists and genres to db
    crud.artists_to_db(user_artists, user_id)

    return render_template('my-data.html') # , display_name=display_name

@app.route('/api/artists')
def get_user_top_artists():

    data = crud.optimize_genres(session["user_id"])

    return jsonify(data)

    return render_template('circle-pack')


@app.route('/testing')
def display_data():

    return render_template('nonzoom-circle-pack.html')


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
