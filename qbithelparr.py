import discord
from discord.ext import commands
import requests
import qbittorrentapi
import configparser
import telegram
from telegram import Bot
import asyncio

config = configparser.ConfigParser()
config.read("config.ini")

StatusList = ["Completed", "Downloading", "Files missing", "Stalled", "Attempting to start", "Queued", "Paused", "Unknown status"]
ListSeparator = ",    "
NothingDownloading = "Nothing is downloading! Why not request something?"
DownloadingStatus = "downloading"
CompleteStatus = "completed"

async def filter_by(torrent_info, filter_type: str) -> bool:
    return torrent_info[1] == filter_type or filter_type == "all"

async def filter_list(full_list, filter_type: str):
    filtered_list = [torrent for torrent in full_list if await filter_by(torrent, filter_type)]
    sorted_list = [torrent for torrent in filtered_list if torrent[2] != "100%"]
    sorted_list.sort(key=lambda x: float(x[2][:-1]), reverse=True)
    sorted_list.extend([torrent for torrent in filtered_list if torrent[2] == "100%"])
    return sorted_list

async def rename_states(full_list):
    status_mapping = {
        "uploading": "Completed", "pausedUP": "Completed", "checkingUP": "Completed", "stalledUP": "Completed", "forcedUP": "Completed",
        "downloading": "Downloading",
        "missingFiles": "Files missing",
        "stalledDL": "Stalled",
        "metaDL": "Attempting to start",
        "queuedDL": "Queued",
        "pausedDL": "Paused"
    }
    for torrent in full_list:
        torrent[3] = status_mapping.get(torrent[3], "Unknown status")
    return full_list

async def find_completed(full_list):
    return [torrent for torrent in full_list if torrent[3] == "Completed"]

async def find_downloading(full_list):
    return [torrent for torrent in full_list if torrent[3] in ["Downloading", "Stalled", "Attempting to start", "Queued", "Paused"]]

async def convert_to_discord(info_list):
    if not info_list:
        print("No torrents found to display.")  # Debug line
        return [NothingDownloading]
    
    max_chars_discord = 1700
    index_range = [2, 3, 4, 0]
    final_list = [[torrent[index] for index in index_range] for torrent in info_list]
    print(f"Final list for Discord message construction: {final_list}")  # Debug line
    
    string_list = convert_to_string(final_list)
    print(f"String list for Discord message construction: {string_list}")  # Debug line
    current_length = len(string_list)
    current_msgs = []

    while current_length > 0:
        await asyncio.sleep(0)  # Yield control back to the event loop
        max_length = string_list[:max_chars_discord].count('\n')
        num_chars = find_nth(string_list, '\n', max_length)
        if num_chars == -1:
            num_chars = len(string_list)
        current_msgs.append(string_list[:num_chars])
        string_list = string_list[num_chars + 1:]
        current_length -= num_chars

    print(f"Constructed messages for Discord: {current_msgs}")  # Debug line
    return current_msgs

def find_nth(string, substring, occurrence):
    val = -1
    for _ in range(occurrence):
        val = string.find(substring, val + 1)
    return val

def convert_to_string(non_str_list):
    string_list = str(non_str_list)
    if ListSeparator not in string_list:
        string_list = string_list.replace("'], ['", "\n\n").replace("']]", "").replace("[['", "").replace("', '", ListSeparator)
    else:
        string_list = string_list.replace("', '", "\n\n").replace("']", "").replace("['", "")
    return string_list

async def update_torrent_list():
    print("Updating torrent list...")  # Debug line
    torrent_list = [
        [torrent.name, torrent.category, f"{round(torrent.progress * 100, 2)}%", torrent.state, convert_time(torrent.eta)]
        for torrent in qbt_client.torrents_info()
    ]
    print(f"Updated torrent list: {torrent_list}")  # Debug line
    return torrent_list

def convert_time(seconds):
    if seconds == 8640000:
        return "inf"
    
    intervals = (
        ('weeks', 604800), ('days', 86400), ('hours', 3600),
        ('minutes', 60), ('seconds', 1)
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f"{value} {name}")
    return 'ETA: ' + ', '.join(result)

async def update_all(category, status="all"):
    print(f"Updating all torrents with category: {category} and status: {status}")  # Debug line
    torrent_list = await update_torrent_list()
    filtered_list = await filter_list(torrent_list, category)
    final_list = await rename_states(filtered_list)
    
    if status == DownloadingStatus:
        final_list = await find_downloading(final_list)
    elif status == CompleteStatus:
        final_list = await find_completed(final_list)
    
    discord_list = await convert_to_discord(final_list)
    print(f"Discord list to send: {discord_list}")  # Debug line
    return discord_list

# Initialize Telegram Bot
telegram_token = config['TELEGRAM']['token']
telegram_chat_id = config['TELEGRAM']['chat_id']
telegram_bot = Bot(token=telegram_token)

def send_telegram_message(message):
    telegram_bot.send_message(chat_id=telegram_chat_id, text=message)

print("------------------------------------------------")
print("starting Discord...")

prefix = "/"
bot_intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=bot_intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print("------------------------------------------------")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(
    help=(
        "Use this to see the status of what's currently downloading.\n"
        "If you want to get fancy, you can search for movies/tv shows specifically by type /status movies or /status tv.\n"
        "You can also see what's completed by doing /status completed, or /status all to see everything.\n"
        "Finally, you can combine these (like /status tv completed) to only see completed tv shows.\n"
        "(tip: you can see everything by typing /status all)"
    ),
    brief="Use this to see what's currently downloading"
)
async def status(ctx, *args):
    print(f"Status command received with args: {args}")  # Debug line
    if ctx.message.channel.id == botChannel:
        def not_pinned(message):
            return not message.pinned

        try:
            await ctx.message.channel.purge(check=not_pinned)
        except Exception as e:
            print(f"Failed to purge messages: {e}")  # Debug line

        update_status = "all" if "all" in args else CompleteStatus if "completed" in args else DownloadingStatus
        category = movieCategory if "movies" in args else tvCategory if "tv" in args else "all"
        
        try:
            discord_list = await update_all(category, update_status)
            print(f"Discord list: {discord_list}")  # Debug line
            for msg in discord_list:
                if msg:
                    print(f"Sending message: {msg}")  # Debug line
                    await ctx.send(msg)
                    send_telegram_message(msg)  # Send the same message to Telegram
                else:
                    print("Empty message, skipping.")  # Debug line
        except Exception as e:
            print(f"Failed to update status: {e}")  # Debug line

botChannel_str = config['DISCORD']['botChannel']
print(f"Read botChannel from config: '{botChannel_str}'")  # Debug line
try:
    botChannel = int(botChannel_str.strip())
except ValueError as e:
    print(f"Invalid botChannel ID: {botChannel_str}")
    raise

tvCategory = config['SONARR']['tvCategory']
movieCategory = config['RADARR']['movieCategory']

host = config['QBITTORRENT']['host']
port_str = config['QBITTORRENT']['port']
print(f"Read port from config: '{port_str}'")  # Debug line
try:
    port = int(port_str.strip())
except ValueError as e:
    print(f"Invalid port: {port_str}")
    raise

username = config['QBITTORRENT']['username']
password = config['QBITTORRENT']['password']

qbt_client = qbittorrentapi.Client(
    host=host,
    port=port,
    username=username,
    password=password
)

TOKEN = config['DISCORD']['token']

try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

bot.run(TOKEN)
