"""CRUD operations"""

from model import (db, User, UserArtist, UserTrack, Artist, RelatedArtist, 
Genre, ArtistGenre, Track, Audio, connect_to_db)
from math import sqrt
from random import choice
################################################################################
#Artist and Genre related functions
################################################################################
#seed database helper functions
def create_user(user_id, display_name, image_url):
    """Create and return new User"""

    user = User(user_id=user_id, 
                display_name= display_name, 
                image_url=image_url)

    if User.query.get(user_id):
        print("User already exists")
    else:
        db.session.add(user)
        db.session.commit()

    return user


def create_user_artist(user_id, artist_id):
    """Create and return a new UserArtist"""

    user_artist = UserArtist(user_id=user_id, artist_id=artist_id)

    db.session.add(user_artist)
    db.session.commit()

    return user_artist


def create_artist(artist_id, artist_name, popularity, image_url):
    """Create and return a new Artist"""

    artist = Artist(artist_id=artist_id, 
                    artist_name=artist_name, 
                    popularity=popularity,
                    image_url=image_url)

    db.session.add(artist)
    db.session.commit()

    return artist


def create_genre(genre):
    genre = Genre(genre=genre)

    db.session.add(genre)
    db.session.commit()

    return genre


def create_artist_genres(artist_id, genre_id):

    artist_genres = ArtistGenre(artist_id=artist_id,
                                genre_id=genre_id)

    db.session.add(artist_genres)
    db.session.commit()

    return artist_genres

#query helper functions
def get_artist_by_id(artist_id):
    """Query artists table and return object"""

    return Artist.query.get(artist_id)


# def check_user_artists(user_id, artist_id):
#     """Check if an artist is in a user's tracks"""

#     return UserArtist.query.filter_by(user_id=user_id).first() and UserArtist.query.filter_by(artist_id=artist_id).first()    


# def check_artist_genres(artist_id, genre_id):
#     """Check if a track is in user_tracks"""

#     return ArtistGenre.query.filter_by(artist_id=artist_id).first() and ArtistGenre.query.filter_by(genre_id=genre_id).first()    


def get_genre_by_name(genre):

    return Genre.query.filter_by(genre=genre).first()


def get_genre_id_by_name(genre):

    return db.session.query(Genre.genre_id).filter_by(genre=genre).first()


def get_genres_by_user_artists(user_id):
    """returns {'art pop': ['Grimes', 'Lady Lamb'], 
    'electropop': ['Grimes', 'Big Wild'], 
    'indietronica': ['Grimes', 'Big Wild'],..}
    includes repeating artists in genres"""

    #join tables to access relationships
    #user_join returns a User object
    user_join = User.query.options( 
             db.joinedload('artists') # attribute for user 
               .joinedload('genres')  # attribute from artist
            ).get(user_id)  

    user_genres = {}                                                                                                                 

    for artist in user_join.artists: 
        for genre in artist.genres: 
             user_genres[genre.genre] = user_genres.get(genre.genre, []) + [artist.artist_name]

    return user_genres


def count_user_artists_by_genre(user_id):
    """returns {'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""

    user_genres = get_genres_by_user_artists(user_id)

    count_artists = {}
    for genre in user_genres:
        count_artists[genre] = count_artists.get(genre, 0) + len(user_genres[genre])

    return count_artists 


def get_genre_data(user_id):
    """Get a user's most popular genre (highest artist count) and genre stats"""

    genres = count_user_artists_by_genre(user_id)

    #genre name
    max_genre = max(genres, key=genres.get)
    #count of artists in max genre
    max_genre_artists = max(genres.values())
    #total number of genres
    genre_count = len(genres)
    print(genre_count)

    return (max_genre, max_genre_artists, genre_count)


def get_num_artists(user_id):
    """Gets count of user artists (50 are not always returned)"""
    user = User.query.get(user_id)

    num_artists = len(user.artists)

    return num_artists


def get_user_artists(user_id):
    """Returns Artist objects for user"""

    user = User.query.get(user_id)

    return (user.artists)


def get_user_artist_ids(user_id):
    """Returns list of artist ids by user artists"""

    user = User.query.get(user_id)

    artist_ids = []
    for artist in user.artists:
        artist_ids.append(artist.artist_id)

    return artist_ids


# def count_genres_by_user_artists(user_id):
#     """returns {'Leon Bridges': 2, 'Lady Lamb': 5, 'Tash Sultana': 1, 'Big Wild': 5, 
#     'Sylvan Esso': 6,...}"""

#     user_join = User.query.options( 
#              db.joinedload('artists') # attribute for user 
#                .joinedload('genres')  # attribute from artist
#             ).get(user_id)  # test is the user id ()   

#     artist_genres = {}
#     for artist in user_join.artists:
#         artist_genres[artist.artist_name] = artist_genres.get(artist.artist_name, 0) + len(artist.genres)

#     return artist_genres

# def get_repeating_artists(user_id):
#     """return list of artists that have multiple genres"""

#     artist_genres = count_genres_by_user_artists(user_id)

#     repeating_artists = []
#     for artist in artist_genres:
#         if artist_genres[artist] > 1:
#             repeating_artists.append(artist)

#     return repeating_artists


def optimize_genres(user_id):
    """Returns a list of artists by genre with artists in their genre with the 
    highest count of artists by user

    >>>optimize_genres("test")
    >>>{'shamanic': ['Beautiful Chorus', 'Rising Appalachia', 'Ayla Nereo'], 
    'brain waves': ['Alpha Brain Waves'], 'electropop': ['Grimes', 'Sylvan Esso', 
    'Overcoats', 'Purity Ring', 'Charlotte Day Wilson'],...}"""

    user_join = User.query.options( 
             db.joinedload('artists') # attribute for user 
               .joinedload('genres')  # attribute from artist
            ).get(user_id)   

    #count of artists in each genre
    """{'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""
    artist_genres = count_user_artists_by_genre(user_id) 

    final_dict = {}

    for artist in user_join.artists:
        max_genre = "" #genre name
        genre_count = 0 #count of artists in that genre
        for genre in artist.genres:
            if artist_genres[genre.genre] == 0:
                final_dict["No Genre"] = final_dict.get("No Genre", []) + [{"name":artist.artist_name, "value": artist.popularity*100}]
            #iterates through each artist's genres to find genre with highest
            #number of associated artists
            elif artist_genres[genre.genre] >= genre_count:
                genre_count = artist_genres[genre.genre]
                max_genre = genre.genre
        
        final_dict[max_genre] = final_dict.get(max_genre, []) + [{"name": artist.artist_name, "value": artist.popularity*100}]

    return final_dict


def circle_pack_json(user_id):
    """Returns formatted input for D3 Circle Pack"""
    # user_join = User.query.options( 
    #          db.joinedload('artists') # attribute for user 
    #            .joinedload('genres')  # attribute from artist
    #         ).get(user_id)  

    #count of artists in each genre
    """{'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""
    artist_genres = optimize_genres(user_id) 


    #     >>>{'shamanic': ['Beautiful Chorus', 'Rising Appalachia', 'Ayla Nereo'], 
    # 'brain waves': ['Alpha Brain Waves'], 'electropop': ['Grimes', 'Sylvan Esso', 
    # 'Overcoats', 'Purity Ring', 'Charlotte Day Wilson'],...}"""

    data = {"name" : "genres", "children": [] }

    for genre, artists in artist_genres.items():
        genre_object = {"name": genre, "children": artists}
        data["children"].append(genre_object)

    return data


################################################################################
#Track and Audio Feature related functions
################################################################################

def create_track(track_id, track_name, artist_name):
    """Create and return a new Track"""

    track = Track(track_id=track_id,
                track_name=track_name,
                artist_name=artist_name)

    db.session.add(track)
    db.session.commit()

    return track


def create_user_track(user_id, track_id):
    """Create and return a new UserTrack"""

    user_track = UserTrack(user_id=user_id, track_id=track_id)

    db.session.add(user_track)
    db.session.commit()

    return user_track


def get_track_by_id(track_id):
    """Query tracks table and return object"""

    return Track.query.get(track_id)


def check_audio(track_id):
    """Query audio table and return object"""

    return Audio.query.filter_by(track_id=track_id).first()


def get_user_tracks_list(user_id):
    """Get user tracks list to pass into API call for audio features"""

    user = User.query.get(user_id)

    track_list = []
    for track in user.tracks:
        track_list.append(track.track_id)

    return track_list


def check_user_tracks(user_id, track_id):
    """Check if a track is in user_tracks"""

    return db.session.query(UserTrack).filter((UserTrack.user_id==user_id), (UserTrack.track_id==track_id)).first()


def avg_audio_features(user_id):
    """Returns list of average audio features for user's top 50 tracks"""

    # user_join = User.query.options( 
    #      db.joinedload('tracks')
    #        .joinedload('audio')  
    #     ).get(user_id)

    audio = []

    # #data being used in radar chart, pass variables in order of expected labels
    avg_dance = db.session.query(db.func.avg(Audio.danceability)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_energy = db.session.query(db.func.avg(Audio.energy)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_speech = db.session.query(db.func.avg(Audio.speechiness)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_acoustic = db.session.query(db.func.avg(Audio.acousticness)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_instrumental = db.session.query(db.func.avg(Audio.instrumentalness)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_liveness = db.session.query(db.func.avg(Audio.liveness)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()
    avg_valence = db.session.query(db.func.avg(Audio.valence)).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Audio.track_id)).scalar()

    audio.extend((avg_dance, avg_energy, avg_speech, avg_acoustic, avg_instrumental, avg_liveness, avg_valence))
    
    return audio


def audio_stats(user_id):
    """Returns a user's highest average audio feature and a list of their preferences
    according to Spotify's standard distribution of songs for each feature
    i.e. if danceability > 0.5 , a user likes highly danceable songs"""

    #list for reference of features at indices
    audio_order = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]

    avg_audio = avg_audio_features(user_id)

    #get max value from user's avg list of audio features
    max_feature = max(avg_audio)

    #get index of that feature
    max_index = avg_audio.index(max_feature)

    #identify feature by name
    max_feauture_name = audio_order[max_index]

    audio_stats = []

    if avg_audio[0] >= 0.5:
        audio_stats.append("highly danceable")

    if avg_audio[1] >= 0.5:
        audio_stats.append("high energy") 

    if avg_audio[2] >= 0.2:
        audio_stats.append("spoken word")

    if avg_audio[3] >= 0.2:
        audio_stats.append("acoustic")

    if avg_audio[4] >= 0.15:
        audio_stats.append("instrumental")

    if avg_audio[5] >= 0.2:
        audio_stats.append("live songs")

    if avg_audio[6] >= 0.5:
        audio_stats.append("high valence")

    if audio_stats == []:
        audio_stats.append("lower than average in all categories")

    return (max_feauture_name, audio_stats)


def get_random_song_audio(user_id):
    """Gets audio features for a random song in user_tracks""" 

    audio_features = []

    #get a random Track object from user's tracks
    song = choice(db.session.query(Track).filter((UserTrack.user_id==user_id), (UserTrack.track_id == Track.track_id)).all())
    track_name = song.track_name
    artist_name = song.artist_name

    #access the song's audio features
    audio = song.audio

    
    audio_features.extend((audio.danceability, audio.energy, 
        audio.speechiness, audio.acousticness, audio.instrumentalness, 
        audio.liveness, audio.valence))

    return (track_name, artist_name, audio_features)


################################################################################
#Write to database
################################################################################
def artists_to_db(user_artists, user_id):
    """Add artists to database from API response"""

    #parse artists in response
    for artist in user_artists['items']:
        artist_id = artist['id']
        artist_name = artist['name']
        popularity = artist['popularity']
        if artist["images"] == []:
            image_url = ""
        else:
            image_url = artist["images"][2]["url"]

        #check if artist is in artists table
        if get_artist_by_id(artist_id) == None:
            db_artist = create_artist(artist_id, artist_name, popularity, image_url)

        # if check_user_artists(user_id, artist_id) == None:
        #add each artist to user_artists table
        db_user_artist = create_user_artist(user_id, artist_id)

        #parse genres from list for each artist
        for genre in artist['genres']:
            genre = genre

            #check if genre is in genres table
            if get_genre_by_name(genre) == None:
                db_genre = create_genre(genre)

            #need genre_id as FK to create artist_genre, auto-created in genre table 
            genre_id = get_genre_id_by_name(genre)  

            #add each artist's genres to artist_genres table
            db_artist_genre = create_artist_genres(artist_id, genre_id)

    return "Success"


def tracks_to_db(user_tracks, user_id):
    """Add tracks to database from API response"""

    #parse tracks in response
    for track in user_tracks['items']:
        track_id = track['id']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        print(track_id, track_name, artist_name)

        #check if track in tracks table
        if get_track_by_id(track_id) == None:
            db_track = create_track(track_id, track_name, artist_name)

        #add track to user-tracks table if track doesn't exist for user
        if check_user_tracks(user_id, track_id) == None:
            db_user_track = create_user_track(user_id, track_id)

    return "Success"


def create_audio_features(data):
    """Create and return new Audio object in database.
    Input will be dictionary from server API call
    data = sp.audio_features(crud.get_user_tracks_list(user_id))"""

    for track in data:
        track_id = track["id"]
        danceability = track["danceability"]
        energy = track["energy"]
        speechiness = track["speechiness"]
        acousticness = track["acousticness"]
        instrumentalness = track["instrumentalness"]
        liveness = track["liveness"]
        valence = track["valence"]
        key = track["key"]
        tempo = track["tempo"]
        mode = track["mode"]

        if check_audio(track_id) == None:

            audio = Audio(track_id=track_id, danceability=danceability, energy=energy, 
                    speechiness=speechiness, acousticness=acousticness, 
                    instrumentalness=instrumentalness, liveness=liveness, 
                    valence=valence, key=key, tempo=tempo, mode=mode)

            db.session.add(audio)
            db.session.commit()

    return "Success"

if __name__ == '__main__':
    from server import app
    connect_to_db(app)