import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'

class SpotifyAPI:
    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        response = requests.post(
            TOKEN_URL,
            data={
                'grant_type': 'client_credentials',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }
        )
        response.raise_for_status()
        return response.json()['access_token']

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}'
        }

    def get_playlist_tracks(self, playlist_id):
        url = f'{BASE_URL}playlists/{playlist_id}/tracks'
        tracks = []
        params = {'limit': 100, 'offset': 0}
        while True:
            resp = requests.get(url, headers=self.get_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()
            tracks.extend(data['items'])
            if data['next']:
                url = data['next']
                params = {}
            else:
                break
        return tracks

    def get_audio_features(self, track_ids):
        url = f'{BASE_URL}audio-features'
        features = []
        for i in range(0, len(track_ids), 100):
            ids = ','.join(track_ids[i:i+100])
            print(f"Requesting audio features for track IDs: {ids}")
            resp = requests.get(url, headers=self.get_headers(), params={'ids': ids})
            if resp.status_code == 403:
                print(f"403 Forbidden error for batch. Trying individual track IDs...")
                # Try each ID individually
                for tid in track_ids[i:i+100]:
                    single_resp = requests.get(url, headers=self.get_headers(), params={'ids': tid})
                    if single_resp.status_code == 403:
                        print(f"403 Forbidden for track ID: {tid}")
                        print(f"Response: {single_resp.text}")
                    else:
                        single_resp.raise_for_status()
                        features.extend(single_resp.json().get('audio_features', []))
                continue
            resp.raise_for_status()
            features.extend(resp.json()['audio_features'])
        return features

    def get_artist_albums(self, artist_id):
        url = f'{BASE_URL}artists/{artist_id}/albums'
        albums = []
        params = {'limit': 50, 'offset': 0}
        while True:
            resp = requests.get(url, headers=self.get_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()
            albums.extend(data['items'])
            if data['next']:
                url = data['next']
                params = {}
            else:
                break
        return albums
