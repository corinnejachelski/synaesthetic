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
    user_id, display_name, image_url = spotify_api.get_user_profile(sp)
    session["user_id"] = user_id

    crud.create_user(user_id, display_name, image_url)

    user_artists = sp.current_user_top_artists(limit=50)
    crud.artists_to_db(user_artists, user_id)

    return render_template('circle-pack.html')

@app.route('/api/artists')
def get_user_top_artists():

    data = crud.optimize_genres(session["user_id"])

    return jsonify(data)

    # return render_template('circle-pack')

# @app.route('/api/user')
# def get_user_profile():
#     """Get user profile and create User in database"""

    
    

#     # user = spotify_api.get_user_profile(sp)
#     user = sp.me()
#     session["user_id"] = user["id"]
#     session["display_name"] = user["display_name"]

#     #data needed to instantiate a User in database
#     user_id = user["id"]
#     display_name = user["display_name"]
#     image_url = user["images"][0]["url"]

#     crud.create_user(user_id, display_name, image_url)

#     return redirect('/api/artists')


# @app.route('/api/artists')
# def get_user_top_artists():

#     sp = spotipy.Spotify(auth=session["access_token"], oauth_manager=OAUTH)

#     #API call to get user's top 50 artists
#     user_artists = sp.current_user_top_artists(limit=50)

#     user_id = session["user_id"]
#     crud.artists_to_db(user_artists, user_id)

#     return redirect('/json/artists')

# @app.route('/json/artists')
# def get_circle_pack_data():

#     data = crud.optimize_genres(session["user_id"])

#     return jsonify(data)


@app.route('/my-data')
def display_data():

    return render_template('circle-pack.html')


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
