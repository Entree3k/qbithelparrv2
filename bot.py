import discord
import qbittorrentapi
import asyncio
import configparser

# Define the Discord bot client and qBittorrent client
client = discord.Client()
qb_client = qbittorrentapi.Client()

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Define the Discord channel ID where the bot will send download progress updates
channel_id = int(config['DISCORD']['CHANNEL_ID'])

# Define the status message that the bot will update with download progress
status_message = None

# Define a coroutine function that updates the download progress in the Discord channel
async def update_download_progress():
    global status_message
    
    # Get the list of all torrents in qBittorrent
    torrents = qb_client.torrents_info()

    # Calculate the total size and downloaded size of all torrents
    total_size = sum([torrent.size for torrent in torrents])
    downloaded_size = sum([torrent.progress * torrent.size for torrent in torrents])

    # Calculate the download progress percentage
    if total_size > 0:
        progress_percentage = int(downloaded_size / total_size * 100)
    else:
        progress_percentage = 0

    # Update the status message with the download progress percentage
    if status_message is not None:
        await status_message.edit(content=f"Download Progress: {progress_percentage}%")

# Define an event listener that runs when the bot is connected and ready to receive commands
@client.event
async def on_ready():
    global status_message

    # Connect to the qBittorrent client
    qb_client.host = config['QBITTORRENT']['HOST']
    qb_client.port = int(config['QBITTORRENT']['PORT'])
    qb_client.username = config['QBITTORRENT']['USERNAME']
    qb_client.password = config['QBITTORRENT']['PASSWORD']
    qb_client.login()

    # Get the Discord channel where the bot will send download progress updates
    channel = client.get_channel(channel_id)

    # Send a status message to the channel and save the message object
    status_message = await channel.send("Download Progress: 0%")

    # Start a background task that updates the download progress every 10 seconds
    while True:
        await update_download_progress()
        await asyncio.sleep(10)

# Run the Discord bot with your Discord bot token
client.run(config['DISCORD']['BOT_TOKEN'])
