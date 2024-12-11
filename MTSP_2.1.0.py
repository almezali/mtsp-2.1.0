#!/usr/bin/env python3

import os
import sys
import time
import argparse
import sqlite3
import random
import mutagen
from typing import List, Dict
import subprocess
import curses

class ShellMusicPlayer:
    def __init__(self, music_dir=None):
        """Initialize the music player"""
        # Home directory for configuration and database
        self.home_dir = os.path.expanduser("~/.shell_music_player")
        os.makedirs(self.home_dir, exist_ok=True)

        # Database setup
        self.db_path = os.path.join(self.home_dir, "music_library.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_database()

        # Music directory
        self.music_dir = music_dir or os.path.expanduser("~/Music")
        
        # Playback state
        self.current_playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False

        # Player process
        self.player_process = None

    def _create_database(self):
        """Create database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                filename TEXT,
                artist TEXT,
                album TEXT,
                duration REAL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER,
                track_id INTEGER,
                FOREIGN KEY(playlist_id) REFERENCES playlists(id),
                FOREIGN KEY(track_id) REFERENCES tracks(id)
            )
        ''')
        self.conn.commit()

    def scan_music_library(self):
        """Scan music directory and add tracks to database"""
        supported_formats = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')
        tracks_added = 0

        for root, _, files in os.walk(self.music_dir):
            for file in files:
                if file.lower().endswith(supported_formats):
                    full_path = os.path.join(root, file)
                    
                    # Check if track already exists
                    self.cursor.execute("SELECT id FROM tracks WHERE path = ?", (full_path,))
                    if self.cursor.fetchone():
                        continue

                    # Extract metadata
                    try:
                        metadata = mutagen.File(full_path, easy=True)
                        artist = metadata.get('artist', ['Unknown Artist'])[0]
                        album = metadata.get('album', ['Unknown Album'])[0]
                        duration = metadata.get('length', 0)
                    except Exception:
                        artist = 'Unknown Artist'
                        album = 'Unknown Album'
                        duration = 0

                    # Insert track
                    self.cursor.execute('''
                        INSERT INTO tracks (path, filename, artist, album, duration)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (full_path, file, artist, album, duration))
                    tracks_added += 1

        self.conn.commit()
        return tracks_added

    def get_tracks(self, limit=50, offset=0, search=None):
        """Retrieve tracks from database"""
        query = "SELECT id, path, filename, artist, album FROM tracks"
        params = []

        if search:
            query += " WHERE filename LIKE ? OR artist LIKE ? OR album LIKE ?"
            search_param = f"%{search}%"
            params = [search_param, search_param, search_param]

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def play(self, tracks=None):
        """Play tracks"""
        if tracks:
            self.current_playlist = tracks
            self.current_track_index = 0

        if not self.current_playlist:
            print("No tracks to play.")
            return

        # Stop any existing playback
        self.stop()

        # Play current track
        current_track = self.current_playlist[self.current_track_index]
        try:
            # Use mpv for playback
            self.player_process = subprocess.Popen([
                'mpv', current_track[1],  # Use full path
                '--no-video',
                '--terminal=no'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.is_playing = True
            print(f"Now playing: {current_track[2]} - {current_track[3]}")
        except Exception as e:
            print(f"Error playing track: {e}")

    def pause(self):
        """Pause playback"""
        if self.player_process:
            self.player_process.send_signal(subprocess.signal.SIGSTOP)
            self.is_paused = True
            print("Playback paused.")

    def resume(self):
        """Resume playback"""
        if self.player_process and self.is_paused:
            self.player_process.send_signal(subprocess.signal.SIGCONT)
            self.is_paused = False
            print("Playback resumed.")

    def stop(self):
        """Stop playback"""
        if self.player_process:
            try:
                self.player_process.terminate()
                self.player_process.wait()
            except Exception:
                pass
            
            self.player_process = None
            self.is_playing = False
            self.is_paused = False
            print("Playback stopped.")

    def next_track(self):
        """Play next track in playlist"""
        if not self.current_playlist:
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.current_playlist)
        self.play()

    def previous_track(self):
        """Play previous track in playlist"""
        if not self.current_playlist:
            return

        self.current_track_index = (self.current_track_index - 1) % len(self.current_playlist)
        self.play()

    def shuffle_playlist(self):
        """Shuffle current playlist"""
        if self.current_playlist:
            random.shuffle(self.current_playlist)
            print("Playlist shuffled.")

    def create_playlist(self, name, tracks):
        """Create a new playlist"""
        self.cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        playlist_id = self.cursor.lastrowid

        for track in tracks:
            self.cursor.execute('''
                INSERT INTO playlist_tracks (playlist_id, track_id)
                VALUES (?, ?)
            ''', (playlist_id, track[0]))

        self.conn.commit()
        print(f"Playlist '{name}' created with {len(tracks)} tracks.")

    def list_playlists(self):
        """List all playlists"""
        self.cursor.execute("SELECT id, name FROM playlists")
        return self.cursor.fetchall()

    def interactive_shell(self):
        """Interactive shell interface"""
        print("Shell Music Player")
        print("Type 'help' for available commands")

        while True:
            try:
                command = input("music> ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()

                if cmd == 'scan':
                    tracks = self.scan_music_library()
                    print(f"Added {tracks} new tracks to library")
                
                elif cmd == 'list':
                    tracks = self.get_tracks(limit=20)
                    for track in tracks:
                        print(f"{track[0]}: {track[2]} - {track[3]}")
                
                elif cmd == 'play':
                    if len(command) > 1:
                        # Play specific tracks or playlist
                        tracks = [self.get_tracks(limit=1, offset=int(command[1])-1)[0]]
                    else:
                        # Get random tracks to play
                        tracks = self.get_tracks(limit=10)
                    self.play(tracks)
                
                elif cmd == 'pause':
                    self.pause()
                
                elif cmd == 'resume':
                    self.resume()
                
                elif cmd == 'stop':
                    self.stop()
                
                elif cmd == 'next':
                    self.next_track()
                
                elif cmd == 'prev':
                    self.previous_track()
                
                elif cmd == 'shuffle':
                    self.shuffle_playlist()
                
                elif cmd == 'search':
                    if len(command) > 1:
                        tracks = self.get_tracks(search=' '.join(command[1:]))
                        for track in tracks:
                            print(f"{track[0]}: {track[2]} - {track[3]}")
                
                elif cmd == 'playlists':
                    playlists = self.list_playlists()
                    for playlist in playlists:
                        print(f"{playlist[0]}: {playlist[1]}")
                
                elif cmd == 'help':
                    print("""
Available commands:
  scan          - Scan music library
  list          - List tracks
  play [id]     - Play tracks (optional: start from track ID)
  pause         - Pause playback
  resume        - Resume playback
  stop          - Stop playback
  next          - Next track
  prev          - Previous track
  shuffle       - Shuffle playlist
  search [term] - Search tracks
  playlists     - List playlists
  help          - Show this help
  exit          - Exit application
""")
                
                elif cmd == 'exit':
                    break
                
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Shell Music Player")
    parser.add_argument('-d', '--dir', help="Music directory path")
    args = parser.parse_args()

    player = ShellMusicPlayer(music_dir=args.dir)
    player.interactive_shell()

if __name__ == "__main__":
    main()
