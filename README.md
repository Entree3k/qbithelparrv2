# qbithelparr Bot

qbithelparr is a Discord and Telegram bot that provides torrent status updates from qBittorrent. It can send notifications to both Discord channels and Telegram chats.

## Features

- **Discord Integration**: Provides status updates on torrents directly in your Discord server.
- **Telegram Integration**: Sends notifications to a specified Telegram chat.
- **Torrent Status Updates**: Shows the status of torrents, including downloading, completed, stalled, and more.
- **Customizable**: Configure categories and status types through a configuration file.

## Prerequisites

- Python 3.9+
- qBittorrent
- Discord Bot Token
- Telegram Bot Token and Chat ID

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd qbithelparr
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create and configure `config.ini`:

    ```ini
    [DISCORD]
    token = <YOUR_DISCORD_BOT_TOKEN>
    botChannel = <YOUR_DISCORD_CHANNEL_ID>

    [SONARR]
    tvCategory = <YOUR_TV_CATEGORY>

    [RADARR]
    movieCategory = <YOUR_MOVIE_CATEGORY>

    [QBITTORRENT]
    host = <YOUR_QBITTORRENT_HOST>
    port = <YOUR_QBITTORRENT_PORT>
    username = <YOUR_QBITTORRENT_USERNAME>
    password = <YOUR_QBITTORRENT_PASSWORD>

    [TELEGRAM]
    token = <YOUR_TELEGRAM_BOT_TOKEN>
    chat_id = <YOUR_TELEGRAM_CHAT_ID>
    ```

## Usage

1. Run the bot:
    ```bash
    python qbithelparr.py
    ```

2. Interact with the bot on Discord using the `/status` command to get the status of torrents.

## Docker

To run the bot in a Docker container:

1. Build the Docker image:
    ```bash
    docker build -t qbithelparr .
    ```

2. Run the Docker container:
    ```bash
    docker run -d --name qbithelparr-container qbithelparr
    ```

## Commands

- **/status**: Use this to see the status of what's currently downloading.
    - `/status movies`: See the status of movie torrents.
    - `/status tv`: See the status of TV torrents.
    - `/status completed`: See the completed torrents.
    - `/status all`: See all torrents.
    - Combine commands, like `/status tv completed`, to see completed TV shows.

## Telegram Integration

To receive notifications on Telegram:

1. Create a Telegram bot and get the bot token. You can follow the instructions [here](https://core.telegram.org/bots#creating-a-new-bot).
2. Get your chat ID. You can find this by sending a message to your bot and visiting `https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getUpdates` to find the chat ID in the response.
3. Add the Telegram bot token and chat ID to the `config.ini` file under the `[TELEGRAM]` section.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.
