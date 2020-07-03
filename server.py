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
    #remove cached token before login
    if os.path.exists(".cache-Corinne Jachelski"):
        os.remove(".cache-Corinne Jachelski")

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

    #get current user's profile info
    user_id, display_name, image_url = spotify_api.user_profile(session["access_token"])
    #save user to session to pass as argument across functions
    session["user_id"] = user_id
    session["display_name"] = display_name
    session["image_url"] = image_url

    #call API for user's top 50 artists
    spotify_api.user_artists(session["access_token"], session["user_id"], "medium_term")

    #call API for user's top 50 tracks
    user_tracks = spotify_api.user_tracks(session["access_token"], session["user_id"])

    #call API for audio features of user tracks
    spotify_api.audio_features(session["access_token"], session["user_id"])

    # return render_template('nonzoom-circle-pack.html', display_name=display_name)
    return redirect('/data')


@app.route('/data')
def display_data():
    """Main user dashboard page with all charts and stats"""
    if session == {}:
        return redirect('/')
    else:
        max_genre, max_genre_artists, genre_count = crud.get_genre_data(session["user_id"], "medium_term")
        
        num_artists = crud.get_num_artists(session["user_id"], "medium_term")

        max_feature, audio_stats = crud.audio_stats(session["user_id"])

        response = spotify_api.get_user_playlists(session["access_token"], session["user_id"])

        if response == "token error":
            return redirect('/')
        else:
           playlist_names = response

        return render_template('my-data.html',
                                display_name=session["display_name"],
                                image_url=session["image_url"],
                                max_genre=max_genre,
                                max_genre_artists=max_genre_artists, 
                                genre_count=genre_count, 
                                num_artists=num_artists,
                                max_feature=max_feature,
                                audio_stats=audio_stats,
                                playlist_names=playlist_names)


@app.route('/api/artists')
def get_user_top_artists():
    """Returns formatted data for circle pack of user's top artists and genres"""

    data = crud.circle_pack_json(session["user_id"], "medium_term")

    return jsonify(data)


@app.route('/api/artists/time-range', methods=['POST'])
def get_top_artists_by_time_range():
    """Change API call to get artists based on a user-selected time range"""

    time_range = request.form.get("time_range")

    #check if user's data does not exist for requested time-range and call API
    if crud.check_user_api_type(session["user_id"], time_range) == []:
        spotify_api.user_artists(session["access_token"], session["user_id"], time_range)

    data = crud.circle_pack_json(session["user_id"], time_range)

    return jsonify(data)


@app.route('/api/playlist', methods=['POST'])
def user_playlist_to_circle_pack():
    """Re-render circle pack chart based on user-selected playlist"""

    playlist_name = request.form.get("playlist")

    playlist_id = crud.get_playlist_id_by_name(session["user_id"], playlist_name)

    if crud.get_playlist_artists_by_id(playlist_id) == None:
        artists = spotify_api.playlist_artists_to_db(session["access_token"], session["user_id"], playlist_id)
    
    data = crud.circle_pack_json(session["user_id"], playlist_id)

    return jsonify(data)


@app.route('/api/audio')
def get_audio_features():
    """Returns data to render initial radar chart of user audio features"""

    avg = crud.avg_audio_features(session["user_id"])
    track_name, artist_name, random_song = crud.get_random_song_audio(session["user_id"])

    return jsonify(avg=avg, random_song=random_song, track_name=track_name, artist_name=artist_name)


@app.route('/api/random-song')
def get_random_song():
    """Random song button"""

    track_name, artist_name, random_song = crud.get_random_song_audio(session["user_id"])

    return jsonify(random_song=random_song, track_name=track_name, artist_name=artist_name)


@app.route('/api/genres')
def get_all_genres():
    """Returns data for table of all user genres with list of all artists"""

    genres = crud.get_genres_by_user_artists(session["user_id"], "medium_term")

    return genres


@app.route('/api/related-artists')
def get_related_artists():
    """Returns data for viz.js network chart of related artists"""

    nodes, edges = spotify_api.get_related_artists(session["access_token"], session["user_id"], "medium_term")

    return jsonify(nodes=nodes, edges=edges)


@app.route('/api/related-artists-all')
def all_related_artists():
    """Returns nodes and edges data for network chart of a user's related artists"""

    nodes, edges = spotify_api.get_related_artists(session["access_token"], session["user_id"], None)

    return jsonify(nodes=nodes, edges=edges)


@app.route('/related-artists-all')
def display_page_all_relartists():
    """Display page for network chart of non-filtered user artists"""

    return render_template('related-artists-all.html')


@app.route('/api/nested-genres')
def nested_genres_circle_pack():
    """Returns data for zoomable circle pack of nested genres/sub-genres"""

    data = crud.circle_pack_genres(session["user_id"])

    return jsonify(data)


@app.route('/about')
def about_page():
    """Display page about project and creator"""

    return render_template('about.html')



if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
