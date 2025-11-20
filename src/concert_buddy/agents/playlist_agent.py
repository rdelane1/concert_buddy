"""Agent specializing in creating Spotify playlists based on concert setlists."""

import json
import os

import spotipy  # type: ignore
from agents import Agent, function_tool
from dotenv import load_dotenv
from httpx import AsyncClient, QueryParams
from pydantic import BaseModel
from spotipy.oauth2 import SpotifyOAuth  # type: ignore

load_dotenv(override=True)


class SongItem(BaseModel):
    """A song item with metadata."""

    song_name: str
    """The name of the song."""

    artist_name: str
    """The name of the artist who performs the song."""

    spotify_uri: str = "Unknown"
    """The Spotify resource identifier of the song."""


class Setlist(BaseModel):
    """A live concert setlist."""

    event_date: str
    """The date the event took place in string format."""

    artist_name: str
    """The name of the artist that performed the event."""

    venue_name: str
    """The name of the venue that hosted the event."""

    set: list[SongItem]
    """List of songs in the order they were performed."""


SETLIST_FM_URL = "https://api.setlist.fm/rest/1.0"
SETLIST_FM_API_KEY = os.getenv("SETLIST_FM_API_KEY")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-public",
    )
)


@function_tool
async def search_setlists(artists: list[str]) -> str:
    """Search Setlist FM for artist setlists.

    Retrieve the most recent setlistsfor a given artist or list of artists.
    Multiple artists can be provided if there are multiple artists performing
    at the same concert.

    Args:
        artists (list[str]): A list of artist or band names to retrieve setlists for.

    Returns:
        str: A formatted string containing the most recent setlists for the given
            artists.

    """
    if not SETLIST_FM_API_KEY:
        return "Setlist FM API key is not configured, unable to search for setlists."
    headers = {"Accept": "application/json", "x-api-key": SETLIST_FM_API_KEY}
    results = ""
    async with AsyncClient() as client:
        for artist in artists:
            params = QueryParams({"artistName": artist, "p": 1})
            response = await client.get(
                SETLIST_FM_URL + "/search/setlists", headers=headers, params=params
            )
            setlists = response.json().get("setlist")
            if not setlists:
                results += f"**No setlists found for {artist}.**\n"
                continue
            results += (
                f"**Most recent setlists for {artist}:**\n"
                + "\n".join(json.dumps(setlist, indent=2) for setlist in setlists[:3])
                + "\n"
            )
    return results


async def _search_song(artist: str, song_name: str) -> SongItem | None:
    query = f"artist:'{artist}' track:'{song_name}'"
    result = sp.search(q=query, type="track")
    tracks = result.get("tracks").get("items")
    if len(tracks) > 0:
        track = tracks[0]
        return SongItem.model_validate(
            {
                "song_name": track.get("name"),
                "artist_name": track.get("artists")[0].get("name"),
                "spotify_uri": track.get("uri"),
            }
        )
    return None


@function_tool
async def create_playlist(
    playlist_name: str, playlist_description: str, song_list: list[SongItem]
) -> str:
    """Create a Spotify playlist with the given name, description, and list of songs.

    Args:
        playlist_name (str): The name of the playlist to create.
        playlist_description (str): A description for the playlist.
        song_list (list[SongItem]): A list of SongItem objects representing the songs to
            add to the playlist.

    Returns:
        str: A message indicating the result of the playlist creation.

    """
    result = ""
    song_list_with_uris = []
    if len(song_list) == 0:
        return "No songs provided to add to the playlist."
    else:
        for song in song_list:
            song_with_uri = await _search_song(
                artist=song.artist_name, song_name=song.song_name
            )
            if not song_with_uri:
                result += (
                    f"Could not find '{song.song_name}' by '{song.artist_name}' "
                    f"on Spotify.\n"
                )
            else:
                song_list_with_uris.append(song_with_uri)
    if len(song_list_with_uris) > 0:
        user_id = sp.me()["id"]
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            description=playlist_description,
        )
        playlist_id = playlist["id"]
        track_uris = [song.spotify_uri for song in song_list_with_uris]
        sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
        result += (
            f"Playlist '{playlist_name}' created successfully with "
            f"{len(song_list_with_uris)} songs! You can view it here: "
            f"{playlist['external_urls']['spotify']}\n"
        )
    else:
        result += (
            "No valid songs found to add to the playlist. Playlist was not created.\n"
        )
    return result


PLAYLIST_INSTRUCTIONS = """You are a playlist curator agent.
Your task is to create a Spotify playlist based on a specific, upcoming live concert
event.
You will be provided with details about the concert event, including the artist(s)
performing, the venue, and the date. Your job is to research the artist's most
recent live concert setlist(s) and create a Spotify playlist that includes the songs
performed at that event.
You should use the 'search_setlists' tool to retrieve the setlist information
and the 'create_playlist' tool to create the Spotify playlist.
"""

playlist_agent = Agent(
    name="Playlist Agent",
    instructions=PLAYLIST_INSTRUCTIONS,
    model="gpt-4.1",
    tools=[search_setlists, create_playlist],
)
