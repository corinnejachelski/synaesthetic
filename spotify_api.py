"""Utility functions for Spotify API and server"""

from flask import Flask, redirect, request, render_template, session
from model import connect_to_db, db
import server
import crud
import spotipy


def user_profile(token):
    """Get detailed profile information about the current user,
    save to db"""

    #Spotipy client Module for Spotify Web API
    sp = spotipy.Spotify(auth=token)

    #call method for getting user profile
    user_info = sp.current_user()

    #data needed to instantiate a User in database
    user_id = user_info["id"]
    display_name = user_info["display_name"]
    image_url = user_info["images"][0]["url"]

    #add user to db
    crud.create_user(user_id, display_name, image_url)

    return (user_id, display_name)


def user_artists(token, user_id):
    """Calls Spotify API for a user's top 50 artists"""

    sp = spotipy.Spotify(auth=token)

    #get current user's top 50 artists
    user_artists = sp.current_user_top_artists(limit=50)

    #add artists and genres to db
    crud.artists_to_db(user_artists, user_id)

    return "Success"

def user_tracks(token, user_id):
    """Calls Spotify API for a user's top 50 tracks"""

    sp = spotipy.Spotify(auth=token)

    #get current user's top 50 artists
    user_tracks = sp.current_user_top_tracks(limit=50)

    #add tracks to db
    crud.tracks_to_db(user_tracks, user_id)

    return user_tracks

def audio_features(token, user_id):
    """Calls Spotify API for audio features based on list of ids of user tracks, 
    adds to audio table in db"""

    sp = spotipy.Spotify(auth=token)

    #gets audio features for user's top 50 tracks
    audio = sp.audio_features(crud.get_user_tracks_list(user_id))
    
    # creates Audio objects and adds to db
    crud.create_audio_features(audio)

    return "Success"


def get_related_artists(token, user_id):
    """Call Spotify API to get related artists for each artist in a user's list,
    format and return data for vis.js network chart"""

    #get Artist objects
    user_artist_list = crud.get_user_artists(user_id)

    #get list of artist ids
    artist_ids = crud.get_user_artist_ids(user_id)
    
    #append all user artists (search artists) for nodes list for network chart
    nodes = []

    #connection lines between related nodes
    #append related artists if related artist also in artist_ids list
    edges = []

    sp = spotipy.Spotify(auth=token)

    for search_artist in user_artist_list:
        search_artist_id = search_artist.artist_id
        sa_image_url = search_artist.image_url 
        sa_artist_name = search_artist.artist_name
        #create node for each artist
        nodes.append({"id":search_artist_id, "shape": "circularImage", "image": sa_image_url, "label": sa_artist_name})
        #call API for related artists for current artist in iteration
        related_artists = sp.artist_related_artists(search_artist_id)

        #parse API response
        for rel_artist in related_artists["artists"]:
            rel_artist_id = rel_artist["id"]
            rel_artist_name = rel_artist["name"]
            
            #create edge if related artist is also in user artists
            if rel_artist_id in artist_ids:
                edges.append({"from": search_artist_id, "to": rel_artist_id})

    return (nodes, edges)

