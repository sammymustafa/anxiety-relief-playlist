import json
import requests
import urllib.parse
from secrets import spotify_user_id
from refresh import Refresh


class SaveSongs:
    def __init__(self):
        # save variables of interest
        self.user_id = spotify_user_id
        self.spotify_token = ""
        self.tracks = ""
        self.new_playlist_id = ""
        song_input = input("Enter the name of a song: ")
        self.url_song_input = urllib.parse.quote(song_input)
        self.playlist_name = input("Enter a playlist name: ")
        self.playlist_desc = input("Enter a playlist description: ")

    def get_recs(self):
        # first need to search up inputted song
        query_1 = "https://api.spotify.com/v1/search?q={}&type=track".format(
            self.url_song_input)
        response_1 = requests.get(query_1,
                                headers={"Content-Type": "application/json",
                                         "Authorization": "Bearer {}".format(self.spotify_token)})
        response_1_json = response_1.json()
        # selects top result, picks out id number only
        rec_id_list = response_1_json["tracks"]["items"][0]["uri"]
        rec_id_text = "".join(rec_id_list)
        rec_id = rec_id_text.replace("spotify:track:", "")
        
        # input genres shown to reduce anxiety, lower blood pressure, etc.
        genres = "classical,jazz,ambient,piano"
        url_genres = urllib.parse.quote(genres)

        # get 50 of spotify's recommendations with target instrumentalness, tempo, speech, etc. for anxiety relief
        query_2 = "https://api.spotify.com/v1/recommendations?limit=50&seed_genres={}&seed_tracks={}&min_instrumentalness=0.75&max_instrumentalness=1&target_speechiness=0&min_tempo=45&max_tempo=80&target_tempo=60".format(
            url_genres, rec_id)
        response_2 = requests.get(query_2,
                                headers={"Content-Type": "application/json",
                                         "Authorization": "Bearer {}".format(self.spotify_token)})
        response_2_json = response_2.json()
        # put the track id's in a list
        for i in response_2_json["tracks"]:
            self.tracks += (i["uri"] + ",")
        self.tracks = self.tracks[:-1]
        self.add_to_playlist()

    def create_playlist(self):
        # create the new playlist
        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        # input desired name and description, can change privacy if needed
        request_body = json.dumps({
            "name": self.playlist_name, "description": str(self.playlist_desc), "public": True
        })
        response = requests.post(query, data=request_body, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.spotify_token)
        })
        response_json = response.json()
        # save id of new playlist to add tracks to
        return response_json["id"]

    def add_to_playlist(self):
        # add recommended songs to newly made playlist
        self.new_playlist_id = self.create_playlist()
        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
            self.new_playlist_id, self.tracks)
        response = requests.post(query, headers={"Content-Type": "application/json",
                                                 "Authorization": "Bearer {}".format(self.spotify_token)})

    def call_refresh(self):
        # refreshing token so can run this at any time
        refreshCaller = Refresh()
        self.spotify_token = refreshCaller.refresh()
        self.get_recs()

a = SaveSongs()
a.call_refresh()
print("Check your Spotify account for your new playlist!")
