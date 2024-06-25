import pandas as pd
from sklearn.cluster import KMeans
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def extract_features(tracks, sp):
    features = []
    for track in tracks:
        audio_features = sp.audio_features(track['id'])[0]
        features.append({
            'danceability': audio_features['danceability'],
            'energy': audio_features['energy'],
            'tempo': audio_features['tempo'],
            'valence': audio_features['valence'],
            'acousticness': audio_features['acousticness'],
            'instrumentalness': audio_features['instrumentalness']
        })
    return pd.DataFrame(features)

def get_recommendations(seed_tracks, sp, seed_genres):
    seed_track_ids = [track['id'] for track in seed_tracks[:5]]  # Use the first 5 tracks as seeds
    
    # Form the parameters for the recommendations API
    params = {
        'limit': 100,
        'seed_tracks': seed_track_ids,
        'seed_genres': seed_genres
    }

    # Filter out any empty seed parameters
    params = {k: v for k, v in params.items() if v}

    if not params:
        raise ValueError("No valid seed tracks or genres provided.")

    recommendations = sp.recommendations(limit=100, seed_tracks=seed_track_ids, seed_genres=seed_genres)
    return recommendations['tracks']

def recommend_songs(sp, start_date=None, end_date=None, genre=None):
    top_tracks = sp.current_user_top_tracks(time_range='short_term')['items']
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        top_tracks = [track for track in top_tracks if start_date <= datetime.strptime(track['album']['release_date'], '%Y-%m-%d') <= end_date]

    seed_genres = [genre.lower()] if genre else []

    top_track_ids = {track['id'] for track in top_tracks}

    # If no genre is provided, don't use genre as seed
    if genre and seed_genres:
        recommendations = get_recommendations(top_tracks, sp, seed_genres)
    else:
        recommendations = sp.recommendations(seed_tracks=[track['id'] for track in top_tracks[:5]], limit=100)['tracks']
    
    filtered_recommendations = [track for track in recommendations if track['id'] not in top_track_ids]
    filtered_recommendations = filtered_recommendations[:25]  # Get only the top 25 recommendations

    recommended_tracks = []
    for track in filtered_recommendations:
        recommended_tracks.append({
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album_cover': track['album']['images'][1]['url'],  # Medium size album cover
            'spotify_url': track['uri']  # Use URI for playback
        })
    
    return recommended_tracks