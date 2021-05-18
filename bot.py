import discord
import websockets
import json
import asyncio
from utils import get_popular_channel, setup_config

from websockets.exceptions import ConnectionClosed
try:
    import thread
except ImportError:
    import _thread as thread


areas = ["תל אביב", "ראש העין"]
client = discord.Client()
url, token, selected_guild, default_voice_channel, default_text_channel = setup_config()

@client.event
async def on_ready():

    global popular_channel
    global voice_client
    voice_client = None
    guild = None
    for client_guild in client.guilds:
        if client_guild.name == selected_guild:
            guild = client_guild
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    popular_channel, red_alert_channel = get_popular_channel(guild, default_voice_channel, default_text_channel)

    while True:
        async with websockets.connect(url) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    if not voice_client or not voice_client.is_connected():
                        print(f"Connecting to {popular_channel.name} and playing siren.")
                        voice_client = await popular_channel.connect(timeout=3000000, reconnect=True)
                    sound = 'test.mp3'
                    try:
                        json_msg = json.loads(message)
                        text_message = "צבע אדום באזורים: " + f"```\n {json_msg['areas']}```"
                        json_areas = json_msg['areas'].split(',')
                        stripped_areas = []
                        for json_area in json_areas:
                            stripped_areas.append(json_area.strip())
                        for area in areas:
                            if area in stripped_areas:
                                sound = 'siren.mp3'
                        print(json_msg)
                    except Exception as ex:
                        print("Had an error while parsing JSON: " + str(ex))
                    if voice_client and not voice_client.is_playing():
                        print(f"Playing {sound} to {popular_channel.name}")
                        voice_client.play(discord.FFmpegPCMAudio(sound), after=stop_playin)
                    print(message)

                    text_message = await default_text_channel.send(text_message)
                    if voice_client and not voice_client.is_playing():
                        print(f"Diconnecting from {popular_channel.name}")
                        await voice_client.disconnect()
                except ConnectionClosed:
                    print("Connection closed")
                    break


def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


def stop_playin(error):
    coro = voice_client.disconnect()
    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
    try:
        fut.result()
    except:
        # an error happened sending the message
        pass

client.run(token)