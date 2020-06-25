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
    if user_info["images"] == []:
        image_url = ""
    else:
        image_url = user_info["images"][0]["url"]

    #add user to db
    crud.create_user(user_id, display_name, image_url)

    return (user_id, display_name, image_url)


def user_artists(token, user_id, time_range):
    """Calls Spotify API for a user's top 50 artists"""

    sp = spotipy.Spotify(auth=token)

    #get current user's top 50 artists
    user_artists = sp.current_user_top_artists(limit=50, time_range=time_range)

    #add artists and genres to db
    crud.artists_to_db(user_artists, user_id, time_range)

    return "Success"


def user_tracks(token, user_id):
    """Calls Spotify API for a user's top 50 tracks"""

    sp = spotipy.Spotify(auth=token)

    #get current user's top 50 artists
    user_tracks = sp.current_user_top_tracks(limit=50)

    #parse response add tracks to db
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

    #get list of artist ids, use set for faster search
    artist_ids_set = set(crud.get_user_artist_ids(user_id))

    #append all user artists (search artists) to nodes list for network chart
    nodes = []

    #connection lines between related nodes
    #append related artists if related artist also in artist_ids list
    edges = []

    sp = spotipy.Spotify(auth=token)

    for search_artist in user_artist_list:
        search_artist_id = search_artist.artist_id
        sa_image_url = search_artist.image_url 
        sa_artist_name = search_artist.artist_name
        #add new line between spaces for label/chart readability
        label_name = sa_artist_name.replace(" ", "\n")
        #create node for each artist
        nodes.append({"id":search_artist_id, "shape": "circularImage", "image": sa_image_url, "label": label_name})
        #call API for related artists for current artist in iteration
        related_artists = sp.artist_related_artists(search_artist_id)

        #parse API response
        for rel_artist in related_artists["artists"]:
            rel_artist_id = rel_artist["id"]
            
            #create edge if related artist is also in user artists
            if rel_artist_id in artist_ids_set:
                edges.append({"from": search_artist_id, "to": rel_artist_id})

    return (nodes, edges)


def get_user_playlists(token, user_id):
    """Call Spotify API for user's playlists and add them to user_playlists table in db"""
    sp = spotipy.Spotify(auth=token)

    playlists = sp.current_user_playlists(limit=50)

    #create empty set for playlist names to pass to front end for users to select playlist by name
    playlist_names = set()

    #parse API response
    if playlists["total"] == 0:
        playlist_names.add("No playlists to analyze")
    else:
        for playlist in playlists["items"]:
            #check if user is owner of playlist
            if playlist["owner"]["id"] == user_id:
                playlist_name = playlist["name"]
                playlist_id = playlist["id"]
                total_tracks = playlist["tracks"]["total"]

                playlist_names.add(playlist_name)

                #add playlist to user_playlist table
                if crud.get_playlist_by_id(playlist_id) == None:
                    crud.create_user_playlist(playlist_id, user_id, playlist_name, total_tracks)

    return playlist_names


def playlist_artists_to_db(token, user_id, playlist_id):
    """Get artists from a user's playlist and add to database"""
    sp = spotipy.Spotify(auth=token)

    #call API to get tracks for the user's playlist, return only artist ids
    playlist_response = sp.user_playlist_tracks(user=user_id, playlist_id=playlist_id, fields="items(track(artists(id)))", limit=100)

    #parse response for clean list of ids
    playlist_artist_ids = []
    for artist in playlist_response["items"]:
        if len(artist["track"]["artists"]) == 1:
            playlist_artist_ids.append(artist["track"]["artists"][0]["id"])

        #some tracks have multiple artists
        else:
            for subartist in artist["track"]["artists"]:
                count = 0
                playlist_artist_ids.append(artist["track"]["artists"][count]["id"])
                count +=1

    #call API to get artist genres and all info to create Artist object
    #sp.artists() takes max of 50 artists
    if len(playlist_artist_ids) > 50:
        num_calls = len(playlist_artist_ids)/50
        called = 0
        list_slice = 49

        while called < num_calls:
            artists = sp.artists(playlist_artist_ids[:list_slice])
            list_slice +=50
            called +=1
            crud.artists_to_db(artists, user_id, playlist_id)

    else:
        artists = sp.artists(playlist_artist_ids)
        crud.artists_to_db(artists, user_id, playlist_id)

    print("\n\n\n\n\n\n\n\n artists written to db")

    #playlist_id is the api_type in this case so that UserArtists can be filtered based on playlist
    #crud.artists_to_db(artists, user_id, playlist_id)

    return artists