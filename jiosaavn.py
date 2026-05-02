import requests
import endpoints
import helper
import json
from traceback import print_exc
import re


def search_for_song(query, lyrics, songdata):
    if query.startswith('http') and 'saavn.com' in query:
        id = get_song_id(query)
        song = get_song(id, lyrics)
        return format_clean(song)

    search_base_url = endpoints.search_base_url + query
    response = requests.get(search_base_url).text.encode().decode('unicode-escape')
    pattern = r'\(From "([^"]+)"\)'
    response = json.loads(re.sub(pattern, r"(From '\1')", response))

    song_response = response['songs']['data']

    songs = []

    for song in song_response:
        id = song['id']
        song_data = get_song(id, lyrics)

        if song_data:
            clean_song = {
                "id": song_data.get("id"),
                "song": song_data.get("song"),
                "artist": song_data.get("primary_artists"),
                "duration": song_data.get("duration"),
                "image": song_data.get("image"),
                "media_url": song_data.get("media_url"),
                "preview_url": song_data.get("vlink"),
                "lyrics": song_data.get("lyrics")
            }

            songs.append(clean_song)

    return {
        "owner": "@ll_PANDA_BBY_ll",
        "channel": "https://t.me/sxyaru",
        "results": songs
    }

def get_song(id, lyrics):
    try:
        song_details_base_url = endpoints.song_details_base_url + id
        song_response = requests.get(song_details_base_url).text.encode().decode('unicode-escape')
        song_response = json.loads(song_response)

        song_data = helper.format_song(song_response[id], lyrics)

        if song_data:
            return song_data
    except:
        return None
        
def format_clean(song_data):
    if not song_data:
        return None

    return {
        "owner": "@pandababay",
        "channel": "https://t.me/sxyaru",
        "results": [{
            "id": song_data.get("id"),
            "song": song_data.get("song"),
            "artist": song_data.get("primary_artists"),
            "duration": song_data.get("duration"),
            "image": song_data.get("image"),
            "media_url": song_data.get("media_url"),
            "preview_url": song_data.get("vlink"),
            "lyrics": song_data.get("lyrics")
        }]
    }