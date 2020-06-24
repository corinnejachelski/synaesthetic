"""CRUD operations"""

from model import (db, User, UserArtist, UserTrack, UserPlaylist, Artist, RelatedArtist, 
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


def create_user_artist(user_id, artist_id, api_type):
    """Create and return a new UserArtist"""

    user_artist = UserArtist(user_id=user_id, artist_id=artist_id, api_type=api_type)

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


def check_user_artists(user_id, artist_id, api_type):
    """Check if an artist is in a user's artists"""

    return db.session.query(UserArtist).filter((UserArtist.user_id==user_id), (UserArtist.artist_id==artist_id), (UserArtist.api_type==api_type)).first()


def check_artist_genres(artist_id, genre_id):
    """Check if a genre is in an artist's genres"""

    return ArtistGenre.query.filter_by(artist_id=artist_id).first() and ArtistGenre.query.filter_by(genre_id=genre_id).first()    


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


def check_user_api_type(user_id, api_type):
    """Check if a time range or playlist id is in a user's artists api_type column"""

    return db.session.query(UserArtist).filter((UserArtist.api_type==api_type), (UserArtist.user_id==user_id)).all()

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


def optimize_genres(user_id, api_type):
    """Returns a list of artists by genre with artists in their genre with the 
    highest count of artists by user

    >>>optimize_genres("test")
    >>>{'shamanic': ['Beautiful Chorus', 'Rising Appalachia', 'Ayla Nereo'], 
    'brain waves': ['Alpha Brain Waves'], 'electropop': ['Grimes', 'Sylvan Esso', 
    'Overcoats', 'Purity Ring', 'Charlotte Day Wilson'],...}"""

    # user_join = User.query.options( 
    #          db.joinedload('artists') # attribute for user 
    #            .joinedload('genres')  # attribute from artist
    #         ).get(user_id)  

    filtered_artists = db.session.query(Artist).filter((UserArtist.api_type==api_type), 
                    (UserArtist.user_id==user_id), 
                    (UserArtist.artist_id==Artist.artist_id)).all()

    #count of artists in each genre
    """{'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""
    artist_genres = count_user_artists_by_genre(user_id) 

    final_dict = {}

    for artist in filtered_artists:
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


def circle_pack_json(user_id, api_type):
    """Returns formatted input for D3 Circle Pack"""
    # user_join = User.query.options( 
    #          db.joinedload('artists') # attribute for user 
    #            .joinedload('genres')  # attribute from artist
    #         ).get(user_id)  

    #count of artists in each genre
    """{'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""
    artist_genres = optimize_genres(user_id, api_type) 


    #     >>>{'shamanic': ['Beautiful Chorus', 'Rising Appalachia', 'Ayla Nereo'], 
    # 'brain waves': ['Alpha Brain Waves'], 'electropop': ['Grimes', 'Sylvan Esso', 
    # 'Overcoats', 'Purity Ring', 'Charlotte Day Wilson'],...}"""

    data = {"name" : "genres", "children": [] }

    for genre, artists in artist_genres.items():
        genre_object = {"name": genre, "children": artists}
        data["children"].append(genre_object)

    return data


def nested_genres(user_id):
    """Return dictionary with keys that are one-word genres and values that are genres
    containing the key (i.e. {pop: [pop rap, indie pop, pop punk]}"""

    user_genres = db.session.query(Genre).filter((UserArtist.user_id==user_id), (UserArtist.artist_id==ArtistGenre.artist_id),(ArtistGenre.genre_id==Genre.genre_id)).all()
    all_genres = db.session.query(Genre).all()

    #one-word genres
    # base_genres = {"indie": [], "hip": [], "chill": [], "jazz": [], "house": [], "trap": [], "dance": [], "electro": []}

    base_genres = {'acoustic': [], 'afrobeat': [], 'alt-rock': [], 'alternative': [], 'ambient': [], 'americana': [], 'anime': [], 'black-metal': [], 
    'bluegrass': [], 'blues': [], 'bossanova': [], 'brazil': [], 'breakbeat': [], 'british': [], 'cantopop': [], 
    'chicago-house': [], 'children': [], 'chill': [], 'classical': [], 'club': [], 'comedy': [], 'contemporary': [], 'country': [], 
    'dance': [], 'dancehall': [], 'death-metal': [], 'deep': [], 'deep-house': [], 'disco': [], 'disney': [], 
    'drum-and-bass': [], 'dub': [], 'dubstep': [], 'edm': [], 'electro': [], 'electronic': [], 'emo': [], 'folk': [], 
    'forro': [], 'french': [], 'funk': [], 'garage': [], 'german': [], 'gospel': [], 'goth': [], 'grindcore': [], 
    'groove': [], 'grunge': [], 'guitar': [], 'happy': [], 'hard': [], 'hard-rock': [], 'hardcore': [], 'hardstyle': [], 'heavy-metal': [], 
    'hip': [], 'holidays': [], 'honky-tonk': [], 'house': [], 'idm': [], 'indian': [], 'indie': [],  
    'industrial': [], 'iranian': [], 'j-dance': [], 'j-idol': [], 'j-pop': [], 'j-rock': [], 'jazz': [], 'k-pop': [], 'kids': [], 
    'latin': [], 'latino': [], 'malay': [], 'mandopop': [], 'metal': [], 'metal-misc': [], 'metalcore': [], 'minimal-techno': [], 
    'movies': [], 'mpb': [], 'new-age': [], 'new-release': [], 'opera': [], 'pagode': [], 'party': [], 'philippines-opm': [], 
    'piano': [], 'pop': [], 'pop-film': [], 'post-dubstep': [], 'power-pop': [], 'progressive-house': [], 'psych': [], 'psych-rock': [], 
    'psychedelic': [], 'punk': [], 'punk-rock': [], 'r-n-b': [], 'rainy-day': [], 'reggae': [], 'reggaeton': [], 'road-trip': [], 'rock': [], 
    'rock-n-roll': [], 'rockabilly': [], 'romance': [], 'sad': [], 'salsa': [], 'samba': [], 'sertanejo': [], 'show-tunes': [], 
    'singer-songwriter': [], 'ska': [], 'sleep': [], 'songwriter': [], 'soul': [], 'soundtracks': [], 'spanish': [], 'study': [], 
    'swedish': [], 'synthpop': [], 'tango': [], 'techno': [], 'trance': [], 'turkish': [], 'vapor': [], 
    'world': []}


    #search all genres in db for better base genre results
    for genre in all_genres:
        #if the genre is one word, add as key in dictionary
        if len(genre.genre.split()) == 1:
            base_genres[genre.genre] = base_genres.get(genre.genre, [])

    for genre in user_genres:
        genre_split = genre.genre.split()
        if len(genre_split) >= 2:
            for word in genre_split:
                #check if genre shares a word with any base genre and add as value
                if word in base_genres.keys():
                    base_genres[word] = base_genres.get(word, []) + [{"name":genre.genre, "value": 100}]

    #delete keys with no values
    length_keys = {k: len(v) for k, v in base_genres.items()}

    for k in length_keys:
        if length_keys[k] <= 1:
            del base_genres[k]

    return base_genres


def circle_pack_genres(user_id):

    genres = nested_genres(user_id)

    data = {"name" : "genres", "children": [] }

    for base_genre, sub_genres in genres.items():
        genre_object = {"name": base_genre, "children": sub_genres}
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
#Playlist functions
################################################################################

def create_user_playlist(playlist_id, user_id, playlist_name, total_tracks):

    user_playlist = UserPlaylist(playlist_id=playlist_id, user_id=user_id, playlist_name=playlist_name, total_tracks=total_tracks)

    db.session.add(user_playlist)
    db.session.commit()

    return user_playlist


def get_playlist_by_id(playlist_id):

    return UserPlaylist.query.get(playlist_id)

def get_playlist_id_by_name(user_id, playlist_name):

    playlist = db.session.query(UserPlaylist).filter((UserPlaylist.playlist_name==playlist_name), (UserPlaylist.user_id==user_id)).first()

    return playlist.playlist_id


################################################################################
#Write API response to database
################################################################################
def artists_to_db(user_artists, user_id, api_type):
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

        if check_user_artists(user_id, artist_id, api_type) == None:
        #add each artist to user_artists table if not already there
            db_user_artist = create_user_artist(user_id, artist_id, api_type)

        #parse genres from list for each artist
        for genre in artist['genres']:
            genre = genre

            #check if genre is in genres table
            if get_genre_by_name(genre) == None:
                db_genre = create_genre(genre)

            #need genre_id as FK to create artist_genre, auto-created in genre table 
            genre_id = get_genre_id_by_name(genre)  

            if check_artist_genres(artist_id, genre_id) == None:
            #add each artist's genres to artist_genres table if not existing
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