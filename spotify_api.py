"""Utility functions for Spotify API and server"""

from flask import Flask, redirect, request, render_template, session
from model import connect_to_db, db
import server
import spotipy

#sp refers to Spotipy client Module for Spotify Web API
# sp = spotipy.Spotify(auth=session["access_token"], oauth_manager=OAUTH)

def get_user_profile(sp):
    """Get detailed profile information about the current user"""

    user_info = sp.current_user()
    print(user_info)

    #data needed to instantiate a User in database
    user_id = user_info["id"]
    display_name = user_info["display_name"]
    image_url = user_info["images"][0]["url"]

    return (user_id, display_name, image_url)



