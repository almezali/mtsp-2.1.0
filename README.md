# Shell Music Player 🎵

A sophisticated command-line music player with comprehensive music library management and playback capabilities.

## ✨ Key Features

- **Music Library Scanning**: Automatic directory scanning and metadata extraction
- **Internal Database**: Store track information (artist, album, duration)
- **Multiple Format Support**: MP3, WAV, FLAC, OGG, M4A
- **Full Playback Control**: 
  - Play/Pause/Resume
  - Next/Previous Track
  - Playlist Shuffling
- **Advanced Search**: Library search by name, artist, or album
- **Playlist Management**
- **User-Friendly CLI Interface**

## 🔧 System Requirements

### Dependencies
- Python 3.7+
- mpv (Media Player)
- Python Libraries:
  - sqlite3
  - mutagen
  - curses

### Recommended Linux Distributions
- Ubuntu 20.04+
- Fedora 33+
- Debian 10+
- Arch Linux
- Linux Mint

## 🚀 Installation

### Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip mpv

# Fedora
sudo dnf install python3 python3-pip mpv

# Arch Linux
sudo pacman -S python python-pip mpv
```

### Install Application
```bash
# Clone the repository
git clone https://github.com/almezali/shell-music-player.git
cd shell-music-player

# Install Python dependencies
pip3 install -r requirements.txt
```

## 🎮 Usage

```bash
# Run the application
python3 MTSP_2.1.0.py

# Specify a custom music directory
python3 MTSP_2.1.0.py -d /path/to/your/music/folder
```

### Available Commands
- `scan`: Scan music library
- `list`: Display tracks
- `play`: Play tracks
- `pause/resume/stop`: Playback control
- `next/prev`: Next/Previous track
- `shuffle`: Randomize playlist
- `search`: Search for tracks
- `playlists`: View playlists

## 📋 Technical Details

- **Database**: SQLite for track and playlist management
- **Metadata Extraction**: Uses Mutagen for retrieving audio file metadata
- **Playback**: Leverages mpv for audio playback
- **Storage**: Tracks stored in `~/.shell_music_player/music_library.db`

## 🛠 Troubleshooting
- Ensure `mpv` is installed
- Check Python dependencies
- Verify music file permissions
- Use `--dir` flag if music folder is not in default location

## 📄 License

[FREE]

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 🔮 Future Roadmap
- Graphical User Interface (GUI)
- Advanced playlist management
- Audio visualization
- Equalizer support
- Streaming service integration
