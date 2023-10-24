from flask import Flask, render_template, request
import spotipy
import spotipy.util as SpotifyOAuth
import os

app = Flask(__name__)

# Set your Spotify API credentials
SPOTIPY_CLIENT_ID = '' # Put your client ID here
SPOTIPY_CLIENT_SECRET = '' # Put your client secret ID here
REDIRECT_URL = 'http://localhost:8888/callback'

template_folder = os.path.join(os.path.dirname(__file__), 'templates')
static_folder = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, REDIRECT_URL, scope="user-top-read"))

@app.route("/", methods=["GET", "POST"])
def index():
    artist_name = ""
    artist_info = None
    top_tracks = None
    top_artists = None

    if request.method == "POST":
        artist_name = request.form["artist_name"]

        search_results = sp.search(q=artist_name, type="artist", limit=1)

        if search_results["artists"]["items"]:
            artist = search_results["artists"]["items"][0]
            artist_name = artist['name']
            genres = ', '.join(artist['genres']) if artist['genres'] else "No genres listed"
            popularity = artist['popularity']
            artist_image = artist['images'][0]['url'] if artist['images'] else None

            artist_info = {
                "name": artist_name,
                "genres": genres,
                "popularity": popularity,
                "image": artist_image
            }

    # Retrieve the user's top tracks and top artists
    top_tracks = sp.current_user_top_tracks(time_range="short_term", limit=10)
    top_artists = sp.current_user_top_artists(time_range="short_term", limit=10)

    # Process data for the template
    processed_tracks = []
    for track in top_tracks['items']:
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        processed_tracks.append({"name": track['name'], "artist_names": artist_names})

    processed_artists = []
    for artist in top_artists['items']:
        artist_name = artist['name']
        genres = artist.get('genres', [])
        genres_str = ', '.join(genres) if genres else 'No genres listed'
        processed_artists.append({"name": artist_name, "genres": genres_str})

    return render_template("index.html", artist_name=artist_name, artist_info=artist_info, top_tracks=processed_tracks, top_artists=processed_artists)

if __name__ == "__main__":
    app.run(debug=True)