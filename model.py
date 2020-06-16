"""Models for Spotify user data viz app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Data model for Spotify user of app"""

    __tablename__ = "users"

    #get user_id from API
    user_id = db.Column(db.String, primary_key=True)
    display_name = db.Column(db.String)
    image_url = db.Column(db.String) #use type text?

    artists = db.relationship("Artist",
                             secondary="user_artists",
                             backref="users")

    tracks = db.relationship("Track",
                             secondary="user_tracks",
                             backref="users")

    def __repr__(self):
        """Return a human-readable representation of a User."""

        return f"<User user_id={self.user_id} display_name={self.display_name}>"


class UserArtist(db.Model):
    """Association table for users and artists"""

    __tablename__ = "user_artists"

    userartist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    artist_id = db.Column(db.String, db.ForeignKey('artists.artist_id'))

    def __repr__(self):
        """Return a human-readable representation of a UserArtist."""

        return f"<UserArtist artist_id={self.artist_id}>"


class UserTrack(db.Model):
    """Association table for users and tracks"""

    __tablename__ = "user_tracks"

    usertrack_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    track_id = track_id = db.Column(db.String, db.ForeignKey('tracks.track_id'))

    def __repr__(self):
        """Return a human-readable representation of a UserTrack."""

        return f"<UserTrack user_id={self.user_id} track_id={self.track_id}>"

class Artist(db.Model):
    """Data model for Spotify artist"""

    __tablename__ = "artists"

    artist_id = db.Column(db.String, primary_key=True)
    artist_name = db.Column(db.String)
    popularity = db.Column(db.Integer)
    image_url = db.Column(db.String)

    #users relationship to User objects

    related = db.relationship("RelatedArtist", backref="artists")

    genres = db.relationship("Genre",
                         secondary="artist_genres",
                         backref="artists") #uselist=False

    def __repr__(self):
        """Return a human-readable representation of an Artist."""

        return f"<Artist artist_id={self.artist_id} artist_name={self.artist_name}>"


class RelatedArtist(db.Model):
    """Data model for related artists to Artist objects"""

    __tablename__ = "related_artists"

    pair_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    search_artist_id = db.Column(db.String, db.ForeignKey('artists.artist_id'))
    related_artist_id = db.Column(db.String)

    #artists relationship to Artist objects

class Genre(db.Model):
    """Data model for Spotify genres"""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    genre = db.Column(db.String(50))

    #artists relationship to Artist objects

    def __repr__(self):
        """Return a human-readable representation of a Genre."""

        return f"<Genre genre_id={self.genre_id} genre={self.genre}>"

class ArtistGenre(db.Model):
    """Association table for artists and genres"""

    __tablename__ = "artist_genres"

    artistgenre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    artist_id = db.Column(db.String, db.ForeignKey('artists.artist_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'))

    def __repr__(self):
        """Return a human-readable representation of an ArtistGenre."""

        return f"<ArtistGenre artist_id={self.artist_id} genre_id={self.genre_id}>"


class Track(db.Model):
    """Data model for a Spotify track"""

    __tablename__ = "tracks"

    track_id = db.Column(db.String, primary_key=True)
    track_name = db.Column(db.String)
    artist_name = db.Column(db.String)
    

    #users relationship to User objects

    audio = db.relationship("Audio", backref="tracks" , uselist=False)

    def __repr__(self):
        """Return a human-readable representation of an ArtistGenre."""

        return f"<Track track_id={self.track_id} track_name={self.track_name}>"

class Audio(db.Model):
    """Spotify audio features for tracks"""

    __tablename__ = "audio_features"

    audio_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    track_id = db.Column(db.String, db.ForeignKey('tracks.track_id'))
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    speechiness = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    liveness = db.Column(db.Float)
    valence = db.Column(db.Float)
    key = db.Column(db.Integer)
    tempo = db.Column(db.Float)
    mode = db.Column(db.String(5)) #Major is represented by 1 and minor is 0

    #tracks relationship to Track objects

    def __repr__(self):
        """Return a human-readable representation of an Audio object."""

        return f"<Audio track_id={self.track_id}>"


#############################################################################
#Test helper function
def example_data():
    """Create some sample data."""


    with open('top_artists.json') as f:
        data = json.load(f)


    user_id = "test" 
    display_name = "test"
    image_url = "test"

    db_user = crud.create_user(user_id, display_name, image_url)

    for artist in data['items']:
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

################################################################################
def connect_to_db(flask_app, db_uri='postgresql:///synaesthetic', echo=True):
    """Connect the database to Flask app."""

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    flask_app.config['SQLALCHEMY_ECHO'] = echo
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = flask_app
    db.init_app(flask_app)

    print('Connected to the db!')


if __name__ == '__main__':
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)