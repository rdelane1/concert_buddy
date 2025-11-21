"""Agent specializing in creating Spotify playlists based on concert setlists."""

import json
import os
from datetime import datetime

import spotipy  # type: ignore
from agents import Agent, ModelSettings, function_tool
from dotenv import load_dotenv
from httpx import AsyncClient, QueryParams
from openai.types.shared import Reasoning
from pydantic import BaseModel
from spotipy.oauth2 import SpotifyOAuth  # type: ignore

from ..hooks import LoggingHooks

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

            # Filter out future setlists (only keep past/present events)
            today = datetime.now().date()
            past_setlists = []
            for setlist in setlists:
                event_date_str = setlist.get("eventDate")
                if event_date_str:
                    try:
                        # Parse date format: "DD-MM-YYYY"
                        event_date = datetime.strptime(
                            event_date_str, "%d-%m-%Y"
                        ).date()
                        if event_date < today:
                            past_setlists.append(setlist)
                    except (ValueError, TypeError):
                        # If date parsing fails, skip this setlist
                        continue

            if not past_setlists:
                results += f"**No past setlists found for {artist}.**\n"
                continue

            results += (
                f"**Most recent setlists for {artist}:**\n"
                + "\n".join(
                    json.dumps(setlist, indent=2) for setlist in past_setlists[:10]
                )
                + "\n"
            )
    return results


async def get_spotify_track(artist: str, song_name: str) -> SongItem | None:
    """Search Spotify for a track by artist and song name.

    Args:
        artist (str): The name of the artist.
        song_name (str): The name of the song.

    Returns:
        SongItem | None: A SongItem object if found, otherwise None.

    """
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


def get_spotify_artist_id(artist_name: str) -> str | None:
    """Search Spotify for an artist to retrieve their Spotify ID.

    Args:
        artist_name (str): The name of the artist to search for.

    Returns:
        str | None: The Spotify ID of the artist, or None if not found.

    """
    result = sp.search(q=artist_name, type="artist", limit=1)
    artists = result.get("artists").get("items")
    if len(artists) > 0:
        return artists[0].get("id")
    return None


def get_spotify_artist_top_tracks(artist_name: str) -> list[SongItem]:
    """Retrieve the top 10 tracks for a given artist from Spotify.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        list[SongItem]: A list of SongItem objects representing the top tracks of the
            artist.

    """
    artist_id = get_spotify_artist_id(artist_name)
    if not artist_id:
        return []

    try:
        top_tracks_data = sp.artist_top_tracks(artist_id)
        top_tracks = top_tracks_data.get("tracks", [])
        if len(top_tracks) > 0:
            return [
                SongItem.model_validate(
                    {
                        "song_name": track.get("name"),
                        "artist_name": artist_name,
                        "spotify_uri": track.get("uri"),
                    }
                )
                for track in top_tracks
            ]
        return []
    except Exception:
        return []


def create_spotify_playlist(
    playlist_name: str, playlist_description: str, song_list: list[SongItem]
) -> str:
    """Create a Spotify playlist for the current user.

    Args:
        playlist_name (str): The name of the playlist to create.
        playlist_description (str): A description for the playlist.
        song_list (list[SongItem]): A list of SongItem objects representing the songs to
            add to the playlist.

    Returns:
        str: A message indicating the result of the playlist creation.

    """
    # Get current user's Spotify ID
    user_id = sp.me()["id"]

    # Create public playlist
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description=playlist_description,
    )

    # Add songs to the playlist
    playlist_id = playlist["id"]
    track_uris = [song.spotify_uri for song in song_list]
    sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)

    # Validate songs added
    playlist_data = sp.playlist(playlist_id)
    playlist_size = playlist_data["tracks"]["total"]
    if playlist_size > 0:
        return (
            f"Playlist '{playlist_name}' created successfully with "
            f"{playlist_size} songs! You can view it here: "
            f"{playlist['external_urls']['spotify']}\n"
        )
    else:
        return "Failed to add songs to the playlist.\n"


@function_tool
async def create_playlist_from_setlist(
    playlist_name: str, playlist_description: str, song_list: list[SongItem]
) -> str:
    """Create a Spotify playlist based on a concert setlist.

    Args:
        playlist_name (str): The name of the playlist to create.
        playlist_description (str): A description for the playlist.
        song_list (list[SongItem]): A list of SongItem objects representing the songs to
            add to the playlist.

    Returns:
        str: A message indicating the result of the playlist creation.

    """
    # Verify and enrich song list with Spotify URIs
    enriched_song_list = []
    for song in song_list:
        spotify_song = await get_spotify_track(
            artist=song.artist_name, song_name=song.song_name
        )
        if spotify_song:
            enriched_song_list.append(spotify_song)

    if not enriched_song_list:
        return "No valid songs found to add to the playlist."

    # Create the Spotify playlist
    result_message = create_spotify_playlist(
        playlist_name=playlist_name,
        playlist_description=playlist_description,
        song_list=enriched_song_list,
    )
    return result_message


@function_tool
async def create_playlist_from_artist_top_tracks(
    playlist_name: str, playlist_description: str, artist_names: list[str]
) -> str:
    """Create a Spotify playlist based on an artist's top tracks.

    Args:
        playlist_name (str): The name of the playlist to create.
        playlist_description (str): A description for the playlist.
        artist_names (list[str]): A list of artist names whose top tracks to include.

    Returns:
        str: A message indicating the result of the playlist creation.

    """
    total_song_list = []
    # Retrieve the artist's top tracks
    for artist in artist_names:
        top_tracks = get_spotify_artist_top_tracks(artist)
        if not top_tracks:
            return f"No top tracks found for artist '{artist}'."
        total_song_list.extend(top_tracks)

    if not total_song_list:
        return "No valid top tracks found to add to the playlist."

    # Create the Spotify playlist
    result_message = create_spotify_playlist(
        playlist_name=playlist_name,
        playlist_description=playlist_description,
        song_list=top_tracks,
    )
    return result_message


PLAYLIST_INSTRUCTIONS = """You are a playlist curator agent specializing in creating
Spotify playlists for upcoming concerts.

Follow this procedure:

1. **Search for setlists**: Use the 'search_setlists' tool to find recent live concert
setlists for the performing artist(s). If multiple artists are requested
(e.g., headlining artist and supporting acts), search for setlists for each artist.

2. **Select best matching setlist**: For each artist, if setlists are found, analyze
them and select the one that best matches the upcoming concert (consider factors like
venue type, recent date, tour name, or similar context).

3. **Create playlist from combined setlists**: Use the 'create_playlist_from_setlist'
tool to create a Spotify playlist based on all selected setlists. Combine songs from
all requested artists into a single list to give concert-goers an idea of what songs
might be performed by each act.

4. **Fallback to top tracks**: If no setlists are found for any artist, use the
'create_playlist_from_artist_top_tracks' tool instead to create a playlist with the
artist's most popular songs. For multiple artists, combine top tracks from all artists.

When creating playlists, use descriptive names and descriptions that reference the
upcoming concert, all performing artists, venue, and date. The goal is to help fans
prepare for the live experience by familiarizing themselves with likely songs that will
be performed by all acts on the bill.
"""

playlist_agent = Agent(
    name="Playlist Agent",
    instructions=PLAYLIST_INSTRUCTIONS,
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="none"),
    ),
    tools=[
        search_setlists,
        create_playlist_from_setlist,
        create_playlist_from_artist_top_tracks,
    ],
    hooks=LoggingHooks(),
)
