# Discord Torrent Status Bot

This project is a Discord bot that integrates with qBittorrent, Sonarr, and Radarr to provide real-time status updates on torrent downloads. The bot can filter and display the status of TV shows and movies based on their categories, and it can also show completed and downloading torrents.

## Features

- Display the status of currently downloading torrents.
- Filter torrents by category (TV shows or movies).
- Show completed torrents.
- Customizable through a `config.ini` file.

## Prerequisites

- Python 3.6+
- A Discord bot token
- qBittorrent with WebUI enabled
- Sonarr and Radarr (optional but recommended)

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/discord-torrent-status-bot.git
   cd discord-torrent-status-bot

2. Install the dependencies:

   ```sh
   pip install -r requirements.txt

3. Configure the bot:

   ```sh
   [DISCORD]
   botChannel = YOUR_DISCORD_CHANNEL_ID
   token = YOUR_DISCORD_BOT_TOKEN

   [SONARR]
   tvCategory = YOUR_SONARR_TV_CATEGORY

   [RADARR]
   movieCategory = YOUR_RADARR_MOVIE_CATEGORY

   [QBITTORRENT]
   host = YOUR_QBITTORRENT_HOST
   port = YOUR_QBITTORRENT_PORT
   username = YOUR_QBITTORRENT_USERNAME
   password = YOUR_QBITTORRENT_PASSWORD

Replace the placeholder values with your actual configuration details.

## Usage

1. Run the bot:

   ```sh
   pip install -r requirements.txt

2. Use the commands:

    /status - Shows the status of currently downloading torrents.
    /status all - Shows all torrents.
    /status completed - Shows completed torrents.
    /status movies - Shows the status of movie torrents.
    /status tv - Shows the status of TV show torrents.
    Combine commands for more specific results, like /status tv completed.

## Example

Here's how you might use the bot in a Discord server:

  User  /status tv

  Bot: Displays the status of all currently downloading TV shows.

  User: /status movies completed

  Bot: Displays the status of all completed movie torrents.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.
