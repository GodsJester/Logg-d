import ssl
import aiohttp
sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE
import os
os.environ['SSL_CERT_FILE'] = 'C:/Users/Administrator/Documents/Shared/cacert.pem' #obviously use your own path to a cert file (if necessary. Windows servers don't play nice with this script.)

# aiohttp.TCPConnector(ssl=False, ssl_context=sslcontext)
aiohttp.connector.TCPConnector(ssl=False)
# none of the above is necessary unless you want to run this on a windows server OS

import discord
from discord.ext import commands
from datetime import datetime

devs = [421405605656526848, 395265673967697920] # just put your own userID's here

auth = "YOUR_TOKEN_HERE"
targets = {}
intents = discord.Intents.all()
client = commands.Bot(command_prefix='-', intents=intents)

@client.event
async def on_ready():
    print("Bot Running...")
    activity = discord.Game(name="with your data")
    await client.change_presence(status=discord.Status.online, activity=activity)

# @client.command()
# async def prepTable(ctx):
#     targets.clear()
#     await ctx.send("Table was prepped successfully...")

@client.command()
async def acquire(ctx, user: discord.User):
    ''' adds the specified user to the list of people being logged '''
    if ctx.author.id not in devs:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")
    else:
        print(f"Prioritized {user}")
        targets[user.id] = []
        await ctx.send(f"Added to table.\nLogging data for [{user.name}]")

@client.command()
async def ls_users(ctx):
    ''' lists users currently being logged '''
    send2 = await ctx.send("Calling users... (This may take some time)\nThis message will update with the user list once it's done parsing.")
    formatted = {"Users": ", ".join([str(await client.fetch_user(user_id)) for user_id in targets.keys()])}
    embed = discord.Embed(title="Logging Users:", description=f"{formatted}", color=0xFF5733)
    await send2.edit(content="Parsing Complete, List below.", embed=embed)

@client.command()
async def priorityWipe(ctx):
    ''' wipes all users off of logging list '''
    if ctx.author.id not in devs:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")
    else:
        targets.clear()
        await ctx.send("Wiped Users")

@client.command()
async def list_messages(ctx, user: discord.User):
    ''' lists the logged messages from any given user '''
    if user.id in targets:
        messages = targets[user.id]
        if messages:
            formatted_messages = "\n".join([f"{message['time']} in {message['channel']}: {message['content']}" for message in messages])
            embed = discord.Embed(title=f"Messages from {user.name}", description=f"{formatted_messages}", color=0x2ecc71)
            embed.set_author(icon_url=user.avatar_url, name=user.name)
            # await ctx.send(f"Messages from {user.name}:\n{formatted_messages}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No messages logged for {user.name}")
    else:
        await ctx.send(f"{user.name} is not in the list of users being tracked.")

# version = discord.__version__
import pkg_resources # This is only necessary because some fucked up discord's __version__ attribute.
@client.command()
async def version(ctx):
    ''' returns the discord API version that the bot is running '''
    await ctx.send(f"Bot is running using Discord.py version {discord.__version__}")
    # print(version)

@client.command()
async def wipeLogs(ctx):
    ''' wipes all logs from the Log list '''
    if ctx.author.id not in devs:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")
    else:
        await ctx.send("cleared args")
        for user in targets.values():
            user.clear()

@client.event
async def on_message(message):
    if message.author.id in targets:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        channel_name = message.channel.name
        targets[message.author.id].append({"time": timestamp, "channel": channel_name, "content": message.content})
    await client.process_commands(message)


@client.command()
async def purgeOld(ctx, user: discord.User, num: int):
    ''' purges a specified number of old messages from a given user. (Discord has a character limit on sent messages. Use the dump command to dump the users logs to a txt if you don't want to lose anything.) '''
    if ctx.author.id in devs:
        if user.id in targets:
            messages = targets[user.id]
            if num <= len(messages):
                for _ in range(num):
                    messages.pop(0)
                await ctx.send(f"{num} old entries have been parsed and removed.")
            else:
                await ctx.send(f"Only {len(messages)} messages available, cannot remove {num}.")
        else:
            await ctx.send(f"{user.name} is not in the list of users being tracked.")
    else:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")

@client.command()
async def dump(ctx, user:discord.User):
    ''' dumps a given users logs to a txt file on the server. Can be posted later with the send_dump command. '''
    if user.id in targets:
        messages = targets[user.id]
        if messages:
            formatted_messages = "\n".join([f"{message['time']} in {message['channel']}: {message['content']}" for message in messages])
            f=open(f"logs_{user.name}.txt", "a", encoding='utf-8)
            f.write(formatted_messages)
            f.write("\n")
            await ctx.send(f"Dumped to logs_{user.name}.txt successfully")
        else:
            await ctx.send(f"No messages logged for {user.name}")
    else:
        await ctx.send(f"{user.name} is not in the list of users being tracked.")

@client.command()
async def send_dump(ctx, user:discord.User):
    ''' sends the dumped txt file of any given user. '''
    if user.id in targets:
        f=open(f"logs_{user.name}.txt", "r", encoding='utf-8')
        embed = discord.Embed(title=f"Dumped Messages from {user.name}", description=f.read(), color=0xffd700)
        embed.set_author(icon_url=user.avatar_url, name=user.name)
        # await ctx.send(f"Messages from {user.name}:\n{formatted_messages}")
        await ctx.send(embed=embed)
        # await ctx.send(f.read())
    else:
        await ctx.send(f"{user.name} is not in the list of users being tracked.")

@client.command()
async def purgeOldDump(ctx, user: discord.User, number: int):
    ''' purges a specified number of a given user's txt dump entries. I actually don't knwow why I wrote this command, I think I was just bored. '''
    if ctx.author.id in devs:
        if user.id in targets:
            file_path = f"logs_{user.name}.txt"
            with open(file_path, "r+") as f:
                lines = f.readlines()
                new_lines = [line for i, line in enumerate(lines, 1) if i < 1 or i > number]
                f.seek(0)
                f.writelines(new_lines)
                f.truncate()
            await ctx.send(f"{number} lines removed from {user.name}'s logs.")
        else:
            await ctx.send(f"{user.name} is not in the list of users being tracked.")
    else:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")

@client.command()
async def openSource(ctx):
    ''' the code is open source, this will send the github link here. Or maybe it won't. Haven't tested it '''
    try:
        await ctx.send("https://github.com/GodsJester/Logg-d")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        
@client.command()
async def addAll(ctx):
    ''' adds all users, recursively, to the list of users being logged '''
    guild = ctx.guild
    members = guild.members
    send = await ctx.send(f"__Adding Users to table__")
    import time
    time.sleep(1)
    if ctx.author.id not in devs:
        await ctx.send("https://tenor.com/view/nuh-uh-nuh-gif-25159854")
    else:
        for member in members:
            targets[member.id] = []
            await send.edit(content=f"Adding {member} to table...")
        await ctx.send("Users added successfully.")
        
    
client.run(auth)
