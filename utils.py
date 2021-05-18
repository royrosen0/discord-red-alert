from configparser import ConfigParser


def get_popular_channel(guild, default_voice_channel, default_text_channel):
    max_members = 0
    popular_channel = None
    for channel in guild.channels:
        if channel.type.name == "voice":
            if len(channel.voice_states) > max_members:
                max_members = len(channel.voice_states)
                popular_channel = channel
            else:
                if channel.name == default_voice_channel:
                    if not popular_channel:
                        popular_channel = channel
                        try:
                            max_members = len(channel.voice_states)
                        except:
                            pass
        if channel.name == default_text_channel:
            default_text_channel = channel
    print(
        f'Bot will connect to the following voice chat:\n'
        f'{popular_channel.name}(id: {popular_channel.id})'
    )
    return popular_channel, default_text_channel


def setup_config():
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")
    url = config['Discord']['ws']
    token = config['Discord']['token']
    selected_guild = config['Discord']['guild']
    default_voice_channel = config['Discord']['default_voice_channel']
    default_text_channel = config['Discord']['default_text_channel']
    return url, token, selected_guild, default_voice_channel, default_text_channel
