# Synaesthetic

Synaesthetic is a Spotify app for visualizing user-specific data, based on the idea of “seeing sound” (synesthesia). Utilizing OAuth and the Spotify Web API, users can explore their listening patterns and relationships among their top artists and genres via an interactive dashboard of stats and charts made with D3.js, viz.js, and Charts.js (aesthetic). Think: visual Spotify Unwrapped

#### Deployment

  - Deployed via Lightsail on AWS
  - [www.synaesthetic.me](www.synaesthetic.me)
  
### Contents
- [Tech Stack](https://github.com/corinnejachelski/synaesthetic/blob/master/README.md#tech-stack)
- [Features](https://github.com/corinnejachelski/synaesthetic/blob/master/README.md#features)
- [Data Model](https://github.com/corinnejachelski/synaesthetic/blob/master/README.md#data-model)
- [Installation](https://github.com/corinnejachelski/synaesthetic/blob/master/README.md#installation)

### Tech Stack
- Python: back-end language
- JavaScript: front-end language
- Flask: web framework
- PostgresQL
- SQLAlchemy
- jQuery
- Bootstrap
- CSS
- HTML
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/reference/)
- [spotipy](https://spotipy.readthedocs.io/en/2.12.0/#): lightweight Python library for the Spotify Web API
- D3.js
- viz.js
- Charts.js

### Features
The features are primarily built off of a user's [top 50 artists and tracks](https://developer.spotify.com/documentation/web-api/reference/personalization/get-users-top-artists-and-tracks/).
1. Artists and Genres
Most Spotify artists are associated with one or more genres, which can be highly specific. The app seeks to understand the relationship between artists and genres by displaying the data in a D3.js Circle Pack chart. Artists are only shown in one genre, which is the genre that has the highest number of other artists a user listens to (i.e. Lizzo's genres are "escape room", "minnesota hip hop", "pop", "pop rap", and "trap queen" and it is mostly likely for her to show up in "pop", depending on a user's other artists). This is done in order to show the highest level of association among artists and genres. 

Users can re-render the circle pack based on top artists over a different time frame or from a personal playlist.

![Artists and Genres Circle Pack](https://github.com/corinnejachelski/synaesthetic/blob/master/static/images/artists-genres.gif)

2. Sub-genres
Due to the highly specific nature of Spotify's genres, a method was created to be able to "nest" genres based on a common shared word for greater insight into genre preferences. One-word "base genres" were taken from [Spotify](https://developer.spotify.com/console/get-available-genre-seeds/) and then a function searches a user's genres for sub-genres (i.e. "pop" would include "pop rap", "art pop", "chamber pop", etc) and displays them in a D3 zoomable circle pack. 

![Sub-genres Zoomable Circle Pack](https://github.com/corinnejachelski/synaesthetic/blob/master/static/images/genres-zoomable.gif)

3. Related Artists Network
Each artist has a set of "related artists", as specified by Spotify (which can be viewed in Spotify through the "Fans Also Like" page for any artists). A network chart was created using viz.js. The algorithm calls the API for a list of related artists for each of a user's top 50 artsits and adds the artist as an edge (line between 2 artists) if any related artist is also in a user's top artists. Users can click or hover over any node to highlight the connections between other artists.

![Related Artists Network](https://github.com/corinnejachelski/synaesthetic/blob/master/static/images/artist-network.gif)

If users interact with the app a lot or have a lot of playlists, they can also view a robust network of up to 250 artists they listen to on a separate page. Due to the structure of the API, where getting related artists can only happen one artist at a time, this calls the API up to 250 times in real time and parses each response, leading to a slow runtime. 

4. Audio Features
Each Spotify track has a set of audio features, or characteristics which help to classify the song. Users are shown their average listening preferences for audio features based on their top 50 songs in a Charts.js radar chart. Users can explore the audio features for any random song in their top 50 with the click of a button. A few summary stats are provided to help users interpret the data or to explore what each audio feature means.  

![Audio Features](https://github.com/corinnejachelski/synaesthetic/blob/master/static/images/audio-features.gif)

### Data Model
![Data model](https://github.com/corinnejachelski/synaesthetic/blob/master/static/images/data_model.JPG)
This data model is reflected in model.py as SQLAlchemy classes

### Installation
To run Synaesthetic on your own machine:

Install PostgresQL

Clone or fork this repo:
```sh
https://github.com/corinnejachelski/synaesthetic
```
Create and activate a virtual environment inside your project directory:
```sh
$virtualenv env
(if on Windows: $virtualenv env --always-copy)
$ source env/bin/activate
```
Install the dependencies:
```sh
$ pip install -r requirements.txt
```
#### Spotify API
Sign up with the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/login)
- Create an app
- Go to your app and locate Client ID and Client Secret
- Create a file in your project directory called secrets.sh and add environment variables
```sh
export SPOTIPY_CLIENT_ID="yourclientid"
export SPOTIPY_CLIENT_SECRET="yourclientsecret"
export SPOTIPY_REDIRECT_URI="http://localhost:5000/callback"
export USERNAME="username associated with your app"
```
- Go to "Edit Settings" and add "http://localhost:5000/" and "http://localhost:5000/callback" to Redirect URIs

Source your keys from your secrets.sh file into your virtual environment:
```sh
$ source secrets.sh
```
Set up the database:
```sh
$ createdb synaesthetic
$ python3 model.py
>>> db.create_all()
```
Run the app:
```sh
$ python3 server.py
```
You can now navigate to 'localhost:5000/' to access Synaesthetic.
