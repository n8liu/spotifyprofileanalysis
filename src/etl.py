from spotify_api import SpotifyAPI
import pandas as pd

def extract_playlist_data(playlist_id):
    api = SpotifyAPI()
    tracks = api.get_playlist_tracks(playlist_id)
    track_ids = [item['track']['id'] for item in tracks if item['track']]
    features = api.get_audio_features(track_ids)
    return tracks, features

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    import sys
    playlist_id = sys.argv[1] if len(sys.argv) > 1 else 'YOUR_PLAYLIST_ID'
    tracks, features = extract_playlist_data(playlist_id)
    save_to_csv(tracks, 'tracks.csv')
    save_to_csv(features, 'features.csv')
