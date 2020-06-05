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


def get_artists_by_user(user_id):
    """
    >>>get_artists_by_user("test2")

    [('1bL7zNdRZRQtgMnMpsCh0K',), ('2DvbYXMiUAQuupPEQnIt1I',),....]
    """

    return db.session.query(UserArtist.artist_id).filter_by(user_id=user_id).all()

def get_genres_by_artist(artist_id):

   return db.session.query(ArtistGenre.genre_id).filter_by(artist_id=artist_id).all()

# def get_max_genre_by_artist(artist_id):

#     genre_ids = db.session.query(ArtistGenre.genre_id).filter_by(artist_id=artist_id).all()

#     num_genres = {}
#     for genre in genre_ids:
#         num_artists[genre.ge]
#         len(genre[0])
    
def get_count_by_genre_id(genre_id):

    return db.session.query(ArtistGenre.artist_id).filter_by(genre_id=genre_id).count()

if __name__ == '__main__':
    from server import app
    connect_to_db(app)