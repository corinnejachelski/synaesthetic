"""CRUD operations"""

from model import db, User, UserArtist, UserTrack, Artist, RelatedArtist, Genre, ArtistGenre, Track, Audio, connect_to_db

def create_artist(artist_id, artist_name, popularity):
    """Create and return a new Artist"""

    artist = Artist(artist_id=artist_id, 
                    artist_name=artist_name, 
                    popularity=popularity)

    db.session.add(artist)
    db.session.commit()

    return artist


def create_artist_genres(artistgenre_id, artist_id, genre_id):

    artist_genres = ArtistGenre(artistgenre_id=artistgenre_id,
                                artist_id=artist_id,
                                genre_id=genre_id)

    db.session.add(artist_genres)
    db.session.commit()

    return artist_genres



if __name__ == '__main__':
    from server import app
    connect_to_db(app)