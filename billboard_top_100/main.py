import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import RequestException
from spotipy.exceptions import SpotifyException
import sys, os
from datetime import datetime
from dotenv import load_dotenv

def validate_date(date_string):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def authenticate_spotify(client_id, client_secret, redirect_uri):
    """Set up Spotify authentication"""
    try:
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-private"
        ))
    except SpotifyException as e:
        print(f"Failed to authenticate with Spotify: {e}")
        sys.exit(1)

def get_billboard_songs(date):
    """Scrape Billboard Hot 100 songs for a given date"""
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                     " (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(
            f"https://www.billboard.com/charts/hot-100/{date}", 
            headers=header,
            timeout=10
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        songs = soup.select("h3.c-title")  # Using CSS selector instead
        
        if not songs:
            print(f"No songs found for date {date}")
            return []
            
        cleaned_songs = []
        excluded_terms = ["Songwriter(s):", "Producer(s):", "Imprint/Promotion Label:"]
        
        for song in songs:
            # Using string property to get just the text content
            text = song.string.strip() if song.string else song.get_text(strip=True)
            if text and not any(term in text for term in excluded_terms):
                cleaned_songs.append(text)
                
        return cleaned_songs
    except RequestException as e:
        print(f"Failed to fetch Billboard data: {e}")
        return []

def create_spotify_playlist(sp, user_id, date, description):
    """Create a new private Spotify playlist"""
    try:
        return sp.user_playlist_create(
            user=user_id,
            name=f"Billboard 100 - {date}",
            public=False,
            description=description
        )
    except SpotifyException as e:
        print(f"Failed to create playlist: {e}")
        return None

def search_spotify_songs(sp, songs, year):
    """Search for songs on Spotify and return their URIs"""
    if not songs:
        print("No songs to search for")
        return []
        
    song_uris = []
    for song in songs:
        try:
            result = sp.search(q=f"track:{song} year:{year}", type="track")
            if not result["tracks"]["items"]:
                print(f"No results found for '{song}'")
                continue
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
            print(f"Found: {song}")
        except IndexError:
            print(f"'{song}' not found on Spotify. Skipped.")
        except SpotifyException as e:
            print(f"Spotify API error while searching for '{song}': {e}")
        except Exception as e:
            print(f"Unexpected error while searching for '{song}': {e}")
    return song_uris

def add_songs_to_playlist(sp, playlist_id, song_uris, batch_size=100):
    """Add songs to playlist in batches"""
    if not song_uris:
        print("No songs to add to playlist")
        return
    
    try:
        for i in range(0, len(song_uris), batch_size):
            batch = song_uris[i:i + batch_size]
            sp.playlist_add_items(playlist_id=playlist_id, items=batch)
            print(f"Added batch of {len(batch)} songs")
        print(f"Successfully added total of {len(song_uris)} songs")
    except SpotifyException as e:
        print(f"Failed to add songs to playlist: {e}")

def main():
    # Load environment variables
    load_dotenv()

    # Get credentials from environment variables
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        print("Error: Missing Spotify credentials in .env file")
        sys.exit(1)

    try:
        # Initialize Spotify
        sp = authenticate_spotify(client_id, client_secret, redirect_uri)
        user_id = sp.current_user()["id"]
        
        # Get and validate user input
        while True:
            date = input("Enter date (YYYY-MM-DD): ")
            if validate_date(date):
                break
            print("Invalid date format. Please use YYYY-MM-DD")
        
        year = date.split("-")[0]
        
        # Execute the main flow with error checking
        songs = get_billboard_songs(date)
        if not songs:
            print("No songs found. Exiting.")
            return
            
        playlist = create_spotify_playlist(sp, user_id, date, f"Billboard Hot 100 songs from {date}")
        if not playlist:
            print("Failed to create playlist. Exiting.")
            return
            
        song_uris = search_spotify_songs(sp, songs, year)
        if not song_uris:
            print("No songs found on Spotify. Exiting.")
            return
            
        add_songs_to_playlist(sp, playlist["id"], song_uris)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()