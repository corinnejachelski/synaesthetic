"""CRUD operations"""

from model import (db, User, UserArtist, UserTrack, Artist, RelatedArtist, 
Genre, ArtistGenre, Track, Audio, connect_to_db)

#seed database helper functions
def create_user(user_id, display_name, image_url):
    """Create and return new User"""

    user = User(user_id=user_id, 
                display_name= display_name, 
                image_url=image_url)

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
    'indietronica': ['Grimes', 'Big Wild'],..}"""

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

    #just artist lists in dictionaries to access repeating artists
    artists = sorted(user_genres.values())

    return user_genres

def count_user_artists_by_genre(user_id):
    """returns {'dance pop': 1, 'electropop': 2, 
    'escape room': 1, 'indietronica': 2,...}"""


    user_genres = get_genres_by_user_artists(user_id)

    count_artists = {}
    for genre in user_genres:
        count_artists[genre] = count_artists.get(genre, 0) + len(user_genres[genre])

    return count_artists 



if __name__ == '__main__':
    from server import app
    connect_to_db(app)