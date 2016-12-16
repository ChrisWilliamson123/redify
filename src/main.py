import json, re, spotipy, sys, time, urllib2
import spotipy.util as util

def parse_track(original_title):
    title = re.match(r"[\w+ \.&'-]+", original_title).group()
    split = title.replace('--', '-').split(' - ')
    return (split[0], split[1].rstrip())

def get_reddit_tracks(subreddits):
    tracks = []
    for sub in subreddits:
        req = urllib2.Request('https://www.reddit.com/r/%s/top.json?sort=top&t=week&limit=100&raw_json=1' % sub)
        req.add_header('User-agent', 'redify')
        json_response = json.loads(urllib2.urlopen(req).read())
        top_music_posts = json_response['data']['children']
        for post in top_music_posts:
            post_data = post['data']
            if sub == 'music':
                if post_data['link_flair_text'] == 'music streaming':
                    try:
                        tracks.append(parse_track(post_data['title']))
                    except:
                        print('Could not parse track with title: %s' % post_data['title'])
            else:
                try:
                    tracks.append(parse_track(post_data['title']))
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
        if playlist['name'] == 'Reddit Top Tracks':
            return playlist['id']
    return None

def add_tracks(client, spotify_tracks):
    current_playlist = get_rmusic_playlist_id(client)
    if current_playlist:
        for index, tracks in enumerate(spotify_tracks):
            if index == 0:
                client.user_playlist_replace_tracks('chriswills123', current_playlist, tracks)
            else:
                client.user_playlist_add_tracks('chriswills123', current_playlist, tracks)
    else:
        new_playlist_id = client.user_playlist_create('chriswills123', 'Reddit Top Tracks', public=True)['id']
        for tracks in spotify_tracks:
            client.user_playlist_add_tracks('chriswills123', new_playlist_id, tracks)

def main():
    client = authorize_user()
    subreddits = ['music', 'listentothis']
    reddit_tracks = get_reddit_tracks(subreddits)
    spotify_tracks = []
    for track in reddit_tracks:
        spotify_track = get_spotify_track(track[0], track[1], client)
        if spotify_track:
            spotify_tracks.append(spotify_track)
    spotify_tracks = [spotify_tracks[i:i + 90] for i in xrange(0, len(spotify_tracks), 90)]
    add_tracks(client, spotify_tracks)

if __name__ == '__main__':
    main()
