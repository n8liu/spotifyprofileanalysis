import os
from flask import Flask, render_template, redirect, url_for, session, request
from flask_session import Session
import pandas as pd
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SPOTIFY_CLIENT_SECRET', 'dev')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

TRACKS_CSV = 'tracks.csv'
FEATURES_CSV = 'features.csv'

# Spotify OAuth config
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
SCOPE = 'user-read-private user-read-email playlist-read-private playlist-read-collaborative user-top-read'
AUTH_BASE_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/login')
def login():
    spotify = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE.split())
    auth_url, state = spotify.authorization_url(AUTH_BASE_URL)
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/callback')
def callback():
    spotify = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=session.get('oauth_state'))
    token = spotify.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )
    session['oauth_token'] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    user_info = None
    top_artists = []
    top_tracks = []
    top_genres = []
    genre_count = {}
    playlists = []
    playlists_tracks = {}
    if 'oauth_token' in session:
        spotify = OAuth2Session(CLIENT_ID, token=session['oauth_token'])
        resp = spotify.get(API_BASE_URL + 'me')
        if resp.status_code == 200:
            user_info = resp.json()
        # Top artists
        artists_resp = spotify.get(API_BASE_URL + 'me/top/artists', params={'limit': 50, 'time_range': 'medium_term'})
        if artists_resp.status_code == 200:
            top_artists = artists_resp.json().get('items', [])
        # Top tracks
        tracks_resp = spotify.get(API_BASE_URL + 'me/top/tracks', params={'limit': 50, 'time_range': 'medium_term'})
        if tracks_resp.status_code == 200:
            top_tracks = tracks_resp.json().get('items', [])
        # Top genres (from all top artists)
        for artist in top_artists:
            for genre in artist.get('genres', []):
                genre_count[genre] = genre_count.get(genre, 0) + 1
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        top_genres = [g[0] for g in sorted_genres[:20]]
        # All playlists
        next_url = API_BASE_URL + 'me/playlists?limit=50'
        while next_url:
            pl_resp = spotify.get(next_url)
            if pl_resp.status_code != 200:
                break
            pl_json = pl_resp.json()
            playlists.extend(pl_json.get('items', []))
            next_url = pl_json.get('next')
        # All tracks in each playlist
        for pl in playlists:
            pl_id = pl['id']
            pl_name = pl['name']
            pl_tracks = []
            next_track_url = API_BASE_URL + f'playlists/{pl_id}/tracks?limit=100'
            while next_track_url:
                tr_resp = spotify.get(next_track_url)
                if tr_resp.status_code != 200:
                    break
                tr_json = tr_resp.json()
                pl_tracks.extend([t['track'] for t in tr_json.get('items', []) if t.get('track')])
                next_track_url = tr_json.get('next')
            playlists_tracks[pl_name] = pl_tracks
    # Sort all top artists by popularity (descending)
    sorted_artists_by_popularity = sorted(top_artists, key=lambda a: a.get('popularity', 0), reverse=True)

    tracks_df = pd.read_csv(TRACKS_CSV) if os.path.exists(TRACKS_CSV) else pd.DataFrame()
    features_df = pd.read_csv(FEATURES_CSV) if os.path.exists(FEATURES_CSV) else pd.DataFrame()
    # Minimal analytics UI
    return render_template('index.html', user_info=user_info, top_genres=top_genres, top_artists=top_artists, top_tracks=top_tracks, sorted_artists_by_popularity=sorted_artists_by_popularity, playlists_tracks=playlists_tracks)

@app.route('/my_tracks')
def my_tracks():
    if 'oauth_token' not in session:
        return redirect(url_for('login'))
    spotify = OAuth2Session(CLIENT_ID, token=session['oauth_token'])
    # Get the user's playlists
    playlists_resp = spotify.get(API_BASE_URL + 'me/playlists', params={'limit': 10})
    playlists = playlists_resp.json().get('items', []) if playlists_resp.status_code == 200 else []
    # Get tracks from the first playlist (if any)
    tracks = []
    audio_features = []
    playlist_name = None
    if playlists:
        playlist = playlists[0]
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        tracks_resp = spotify.get(API_BASE_URL + f'playlists/{playlist_id}/tracks', params={'limit': 10})
        if tracks_resp.status_code == 200:
            tracks = tracks_resp.json().get('items', [])
            track_ids = [t['track']['id'] for t in tracks if t['track'] and t['track']['id']]
            # Fetch audio features for these tracks
            if track_ids:
                features_resp = spotify.get(API_BASE_URL + 'audio-features', params={'ids': ','.join(track_ids)})
                if features_resp.status_code == 200:
                    audio_features = features_resp.json().get('audio_features', [])
    return render_template_string('''
    <html>
    <head><title>My Spotify Tracks & Features</title></head>
    <body>
        <h1>Tracks from Playlist: {{ playlist_name or 'None found' }}</h1>
        <table border="1">
            <tr><th>Name</th><th>Artist</th><th>Album</th><th>ID</th></tr>
            {% for t in tracks %}
                <tr>
                    <td>{{ t['track']['name'] }}</td>
                    <td>{{ t['track']['artists'][0]['name'] }}</td>
                    <td>{{ t['track']['album']['name'] }}</td>
                    <td>{{ t['track']['id'] }}</td>
                </tr>
            {% endfor %}
        </table>
        <h2>Audio Features</h2>
        <table border="1">
            <tr>
                <th>ID</th><th>Danceability</th><th>Energy</th><th>Tempo</th><th>Valence</th>
            </tr>
            {% for f in audio_features %}
                <tr>
                    <td>{{ f['id'] }}</td>
                    <td>{{ f['danceability'] }}</td>
                    <td>{{ f['energy'] }}</td>
                    <td>{{ f['tempo'] }}</td>
                    <td>{{ f['valence'] }}</td>
                </tr>
            {% endfor %}
        </table>
        <p><a href="/">Back to Home</a></p>
    </body>
    </html>
    ''', tracks=tracks, audio_features=audio_features, playlist_name=playlist_name)

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
