"""CRUD operations"""

from model import (db, User, UserArtist, UserTrack, Artist, RelatedArtist, 
Genre, ArtistGenre, Track, Audio, connect_to_db)
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


def create_artist(artist_id, artist_name, popularity):
    """Create and return a new Artist"""

    artist = Artist(artist_id=artist_id, 
                    artist_name=artist_name, 
                    popularity=popularity)

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
            ).get(user_id)  # test is the user id ()                                                                                               

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
    """Get a user's most popular genre (highest artist count)"""

    genres = count_user_artists_by_genre(user_id)

    max_genre = max(genres, key=genres.get)
    max_genre_artists = max(genres.values())
    genre_count = len(genres)
    print(genre_count)

    return (max_genre, max_genre_artists, genre_count)


def get_num_artists(user_id):
    """Gets count of user artists (50 are not always returned)"""
    user = User.query.get(user_id)

    num_artists = len(user.artists)

    return num_artists


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


def artists_to_db(user_artists, user_id):
    """Add artists to database from API response"""

    #parse artists in response
    for artist in user_artists['items']:
        artist_id = artist['id']
        artist_name = artist['name']
        popularity = artist['popularity']

        #check if artist is in artists table
        if get_artist_by_id(artist_id) == None:
            db_artist = create_artist(artist_id, artist_name, popularity)

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

def size_circle_pack(user_id):

    num_artists = get_num_artists(user_id)

    #800 is size of svg 
    circle_size = (800/num_artists) * 2

    return circle_size


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
            ).get(user_id)  # test is the user id ()  

    #count of artists in each genre
    """{'chillwave': 3, 'dance pop': 3, 'electropop': 6, 
    'escape room': 4,....}"""
    artist_genres = count_user_artists_by_genre(user_id) 

    #dynamically size circles based on number of user artists to optimize chart space
    value = size_circle_pack(user_id)

    final_dict = {}
    for artist in user_join.artists:
        max_genre = "" #genre name
        genre_count = 0 #count of artists in that genre
        for genre in artist.genres:
            if artist_genres[genre.genre] == 0:
                final_dict["No Genre"] = final_dict.get("No Genre", []) + [{"name":artist.artist_name, "value": value}]
            #iterates through each artist's genres to find genre with highest
            #number of associated artists
            elif artist_genres[genre.genre] >= genre_count:
                genre_count = artist_genres[genre.genre]
                max_genre = genre.genre
        
        final_dict[max_genre] = final_dict.get(max_genre, []) + [{"name": artist.artist_name, "value": value}]

    return final_dict


def circle_pack_json(user_id):
    """Input for D3 Circle Pack"""
    user_join = User.query.options( 
             db.joinedload('artists') # attribute for user 
               .joinedload('genres')  # attribute from artist
            ).get(user_id)  # test is the user id ()  

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

#create_track
#create_user_track
#create_audio_features
#get_count_keys_by_user_tracks - donut chart with colors

if __name__ == '__main__':
    from server import app
    connect_to_db(app)