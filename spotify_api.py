from spotipy.oauth2 import SpotifyOAuth
import spotipy
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope='user-top-read playlist-modify-public user-modify-playback-state')

def get_spotify_client(token_info):
    return spotipy.Spotify(auth=token_info['access_token'])

def get_token():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return auth_url, None
    return None, token_info

def get_available_genres(sp):
    genres = sp.recommendation_genre_seeds()
    return genres['genres']

def get_top_tracks(sp, time_range='short_term', limit=50):
    results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    return results['items']