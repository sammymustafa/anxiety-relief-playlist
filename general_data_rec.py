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
        self.playlist_name = input("Enter a playlist name: ")
        self.playlist_desc = input("Enter a playlist description: ")

    def get_recs(self):
        # first need to get top songs, can change time range to medium_term or long_term
        query_1 = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=2"
        response_1 = requests.get(query_1,
                                headers={"Content-Type": "application/json",
                                         "Authorization": "Bearer {}".format(self.spotify_token)})
        response_1_json = response_1.json()

        # selects top two results, picks out id numbers only
        rec_id_list = response_1_json["items"]
        library = []
        for song in rec_id_list:
            # add to ["track"] before ["uri"] if looking at liked songs
            rec_id_spotify = song["uri"]
            rec_id_text = "".join(rec_id_spotify)
            rec_id = rec_id_text.replace("spotify:track:", "")
            library.append(rec_id)
        library_tracks = ",".join(library)
        url_library_tracks = urllib.parse.quote(library_tracks)
        
        # input up to three genres of interest
        genres = ""
        url_genres = urllib.parse.quote(genres)

        # get 50 of spotify's recommendations 
        query_2 = "https://api.spotify.com/v1/recommendations?limit=50&seed_genres={}&seed_tracks={}".format(
            url_genres, url_library_tracks)
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
