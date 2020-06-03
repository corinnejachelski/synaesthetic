"""Populate database from API responses"""

import os
import json
from pprint import pprint
from random import choice
import model, crud, server

os.system('dropdb synaesthetic')
os.system('createdb synaesthetic')

model.connect_to_db(server.app)
model.db.create_all()

# get user's top 50 artists and store as Artist objects
#this will change to be the API response instead of file
with open('top_artists.json') as f:
    data = json.load(f)

#will change to get_user_info() from API response
user_id = "test" 
display_name = "test"
image_url = "test"

db_user = crud.create_user(user_id, display_name, image_url)

#parse artists in response
for artist in data['items']:
    artist_id = artist['id']
    artist_name = artist['name']
    popularity = artist['popularity']

    #check if artist is in artists table
    if crud.get_artist_by_id(artist_id) == None:
        db_artist = crud.create_artist(artist_id, artist_name, popularity)

    #add each artist to user_artists table
    db_user_artist = crud.create_user_artist(user_id, artist_id)


    #parse genres from list
    for genre in artist['genres']:
        genre = genre

        #check if genre is in genres table
        if crud.get_genre_by_name(genre) == None:
            db_genre = crud.create_genre(genre)

        genre_id = crud.get_genre_id_by_name(genre)  

        #need auto-increment genre_id as FK to create artist_genre    
        #add each artist's genres to artist_genres table
        db_artist_genre = crud.create_artist_genres(artist_id, genre_id)

    


#seed genres table

# 'genres' : artist['genres']}

# print(artist_info.keys())

#for key in artist_info.keys() --> API call for multiple artist's related artists

##############################################################################
# get user's top 50 tracks from API and parse to python dict

# with open('top_tracks.json') as f:
#     data = json.load(f)

# track_info = {}
# track_ids = []

# for track in data['items']:
#     key = track['id']
#     track_ids.append(key)
#     track_info[key] = {'track_name': track['name'], 
#                        'artist_id': track['artists'][0]['id']}

# for key in track_info.keys():
#     print(key +",")

# print(len(track_info))
# print(track_info)
# print(choice(track_ids))
# print(track_info.keys())
# print(type(track_info.keys()))

#for key in track_info.keys() --> API call for audio features for multiple tracks

#is it better to have a nested dict or list of dict objects?####################
