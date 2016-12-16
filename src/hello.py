import json, re, spotipy, sys, time, urllib2
import spotipy.util as util

def get_reddit_tracks():
    req = urllib2.Request('https://www.reddit.com/r/Music/top.json?sort=top&t=week&limit=100&raw_json=1')
    req.add_header('User-agent', 'redify')
    json_response = json.loads(urllib2.urlopen(req).read())
    top_music_posts = json_response['data']['children']
    tracks = []
    for post in top_music_posts:
        post_data = post['data']
        if post_data['link_flair_text'] == 'music streaming':
            try:
                title = re.match(r"[\w+ \.&'-]+", post_data['title']).group()
                split = title.split(' - ')
                tracks.append((split[0], split[1].rstrip()))
            except:
                print('Could not parse track with title: %s' % post_data['title'])
    return tracks

def authorize_user():
    scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-library-read user-library-modify'
    token = util.prompt_for_user_token('chriswills123', scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        return sp
    else:
        print "Can't get token for", username

def get_spotify_track(artist, title, client):
    results = client.search(q='%s %s' % (artist, title), type='track')
    for track in results['tracks']['items']:
        found_title = track['name']
        found_artist = track['artists'][0]['name']
        if (title.lower() in found_title.lower() or found_title.lower() in title.lower()) and (artist.lower() in found_artist.lower() or found_artist.lower() in artist.lower()):
            return track['id']
    print('Could not find: %s - %s' % (artist, title))

def get_rmusic_playlist_id(client):
    current_playlists = client.user_playlists('chriswills123', limit=50, offset=0)
    for playlist in current_playlists['items']:
        if playlist['name'] == '/r/music':
            return playlist['id']
    return None

def main():
    client = authorize_user()
    reddit_tracks = get_reddit_tracks()
    spotify_tracks = []
    for track in reddit_tracks:
        spotify_track = get_spotify_track(track[0], track[1], client)
        if spotify_track:
            spotify_tracks.append(spotify_track)
    
    current_playlist = get_rmusic_playlist_id(client)
    if current_playlist:
        client.user_playlist_replace_tracks('chriswills123', current_playlist, spotify_tracks)
    else:
        new_playlist_id = client.user_playlist_create('chriswills123', '/r/music', public=True)['id']
        client.user_playlist_add_tracks('chriswills123', new_playlist_id, spotify_tracks)

if __name__ == '__main__':
    main()
