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
#this will change to be the API response
with open('top_artists.json') as f:
    data = json.load(f)

for artist in data['items']:
    artist_id = artist['id']
    artist_name = artist['name']
    popularity = artist['popularity']

    db_artist = crud.create_artist(artist_id, artist_name, popularity)



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
