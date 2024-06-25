# app.py
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from recommendation import recommend_songs
from spotify_api import sp_oauth, get_spotify_client, get_token, get_available_genres
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    auth_url, token_info = get_token()
    if auth_url:
        return redirect(auth_url)
    sp = get_spotify_client(token_info)
    session['token_info'] = token_info
    user = sp.current_user()
    session['user'] = user
    return render_template('index.html', user=user)

@app.route('/callback')
def callback():
    try:
        token_info = sp_oauth.get_access_token(request.args.get('code'))
        session['token_info'] = token_info
        return redirect(url_for('home'))
    except Exception as e:
        return str(e)

@app.route('/recommend', methods=['GET'])
def recommend():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('home'))
    sp = get_spotify_client(token_info)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    genre = request.args.get('genre')
    recommendations = recommend_songs(sp, start_date=start_date, end_date=end_date, genre=genre)
    return jsonify(recommendations)

@app.route('/play', methods=['POST'])
def play():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('home'))
    sp = get_spotify_client(token_info)
    track_uri = request.json.get('uri')
    print(f"Playing track URI: {track_uri}")  # Debug statement
    if track_uri:
        try:
            sp.start_playback(uris=[track_uri])
            print("Playback started successfully")  # Debug statement
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(f"Error starting playback: {e}")  # Debug statement
            return jsonify({'status': 'failed', 'error': str(e)}), 500
    return jsonify({'status': 'failed', 'error': 'No track URI provided'}), 400

@app.route('/save_playlist', methods=['POST'])
def save_playlist():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('home'))
    sp = get_spotify_client(token_info)
    track_uris = request.json.get('uris')
    playlist_name = request.json.get('name', 'Catify Playlist')
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name)
    sp.user_playlist_add_tracks(user_id, playlist['id'], track_uris)
    return jsonify({'status': 'success', 'playlist_url': playlist['external_urls']['spotify']}), 200

@app.route('/genres', methods=['GET'])
def genres():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('home'))
    sp = get_spotify_client(token_info)
    genres = get_available_genres(sp)
    return jsonify(genres)

if __name__ == '__main__':
    app.run(debug=True, port=5000)