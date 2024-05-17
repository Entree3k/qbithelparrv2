import discord
from discord.ext import commands
import requests
import qbittorrentapi
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

StatusList = ["Completed", "Downloading", "Files missing", "Stalled", "Attempting to start", "Queued", "Paused", "Unknown status"]
ListSeparator = ",    "
NothingDownloading = "Nothing is downloading! Why not request something?"
DownloadingStatus = "downloading"
CompleteStatus = "completed"

def filter_by(torrent_info, filter_type: str) -> bool:
    return torrent_info[1] == filter_type or filter_type == "all"

def filter_list(full_list, filter_type: str):
    filtered_list = [torrent for torrent in full_list if filter_by(torrent, filter_type)]
    sorted_list = [torrent for torrent in filtered_list if torrent[2] != "100%"]
    sorted_list.sort(key=lambda x: float(x[2][:-1]), reverse=True)
    sorted_list.extend([torrent for torrent in filtered_list if torrent[2] == "100%"])
    return sorted_list

def rename_states(full_list):
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

def find_completed(full_list):
    return [torrent for torrent in full_list if torrent[3] == "Completed"]

def find_downloading(full_list):
    return [torrent for torrent in full_list if torrent[3] in ["Downloading", "Stalled", "Attempting to start", "Queued", "Paused"]]

def convert_to_discord(info_list):
    if not info_list:
        return [NothingDownloading]
    
    max_chars_discord = 1700
    index_range = [2, 3, 4, 0]
    final_list = [[torrent[index] for index in index_range] for torrent in info_list]
    
    string_list = convert_to_string(final_list)
    current_length = len(string_list)
    current_msgs = []

    while current_length > 0:
        max_length = string_list[:max_chars_discord].count('\n')
        num_chars = find_nth(string_list, '\n', max_length)
        current_msgs.append(string_list[:num_chars])
        string_list = string_list[num_chars + 1:]
        current_length -= num_chars

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

def update_torrent_list():
    return [
        [torrent.name, torrent.category, f"{round(torrent.progress * 100, 2)}%", torrent.state, convert_time(torrent.eta)]
        for torrent in qbt_client.torrents_info()
    ]

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

def update_all(category, status="all"):
    torrent_list = update_torrent_list()
    filtered_list = filter_list(torrent_list, category)
    final_list = rename_states(filtered_list)
    
    if status == DownloadingStatus:
        final_list = find_downloading(final_list)
    elif status == CompleteStatus:
        final_list = find_completed(final_list)
    
    discord_list = convert_to_discord(final_list)
    return discord_list

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
    if ctx.message.channel.id == botChannel:
        def not_pinned(message):
            return not message.pinned
        
        await ctx.message.channel.purge(check=not_pinned)
        
        update_status = "all" if "all" in args else CompleteStatus if "completed" in args else DownloadingStatus
        category = movieCategory if "movies" in args else tvCategory if "tv" in args else "all"
        
        discord_list = update_all(category, update_status)
        
        for msg in discord_list:
            await ctx.channel.send(msg)

botChannel = int(config['DISCORD']['botChannel'])
tvCategory = config['SONARR']['tvCategory']
movieCategory = config['RADARR']['movieCategory']
qbt_client = qbittorrentapi.Client(
    host=config['QBITTORRENT']['host'],
    port=int(config['QBITTORRENT']['port']),
    username=config['QBITTORRENT']['username'],
    password=config['QBITTORRENT']['password']
)
TOKEN = config['DISCORD']['token']

try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

bot.run(TOKEN)
