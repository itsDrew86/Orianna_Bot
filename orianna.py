import os
import discord
from discord.ext import commands
import riot_api
import db_handler
import datetime
import numpy as np
import matplotlib.pyplot as plt


discord_token = os.getenv('DISCORD_TOKEN')
league_token = os.getenv('LEAGUE_API_TOKEN')

ori = commands.Bot(command_prefix='!ori ')
embed_color = 0xdfdf00
emojis = {}


class Player:
    def __init__(self, summoner_name, champion_id, team_id, lane, role, kills, deaths, assists, dmg_to_champions,
                 dmg_to_objectives, turret_kills, inhibitor_kills, cs_score, vision_score, wards_purchased,
                 wards_placed, wards_killed, creeps_per_min_deltas, cs_diff_per_min_deltas):
        self.summoner_name = summoner_name
        self.champion_id = champion_id
        self.team_id = team_id
        self.lane = lane
        self.role = role
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.dmg_to_champions = dmg_to_champions
        self.dmg_to_objectives = dmg_to_objectives
        self.total_damage = self.dmg_to_champions + self.dmg_to_objectives
        self.turret_kills = turret_kills
        self.inhibitor_kills = inhibitor_kills
        self.cs_score = cs_score
        self.vision_score = vision_score
        self.wards_purchased = wards_purchased
        self.wards_placed = wards_placed
        self.wards_killed = wards_killed
        self.creeps_per_min_deltas = creeps_per_min_deltas
        self.cs_diff_per_min_deltas = cs_diff_per_min_deltas


@ori.event
async def on_ready():
    print(f'{ori.user.name} has connected to Discord!')

    # Cache custom emoji ID's
    emoji_sets = [651145265104814103,
                  651147761277730818,
                  651148360081866760,
                  673328777492824124]
    for guild_id in emoji_sets:
        guild = ori.get_guild(guild_id)
        for emoji in guild.emojis:
            emojis.setdefault(emoji.name.lower(), emoji.id)


@ori.command(name='add', help='Connects your Summoner Account to your Discord Account.')
async def add(ctx, summoner_name):
    """
    Links the Summoner Name specified by the discord author to their discord ID and stores them in an SQL database with
    the discord_id as the primary key. Database table structure:

    discord_id | discord_name | summoner_name | summoner_id | account_id | puuid |

    :param ctx: The discord context
    :param summoner_name: The league of legends summoner name
    :return: Returns a discord Embed either confirming whether or not the summoner name and discord account were linked
    """

    # Get the discord command author (stored as object)
    author = ctx.message.author

    # Check if the author is in the user database already.
    db_summoner_name = db_handler.get_summoner_name(author.id)
    if db_summoner_name:

        # Inform the author their discord_id is already linked to a League of Legends account
        embed = discord.Embed(
            title="<:no_entry_sign:647646871459987458>  Orianna Add Command",
            description="**{}** is already linked to your account!\n"
                        "If you wish to remove it, try the `!ori remove` command".format(db_summoner_name),
            color=0xdfdf00
        )
        await ctx.send(embed=embed)
        return

    # If the author is not already stored in the database, try to link their summoner name and insert them

    # call_summonerByName():
    # if summoner exists, returns response code 200 and json a object that models the LoL summoner data
    # if summoner does not exist, returns response code 402 and 'None' object
    response_status, summoner_data = riot_api.call_summonerByName(summoner_name)

    # Called from Command Dispatcher below.
    async def create_user():

        # The data to store in the SQL database
        summoner_id = summoner_data['id']
        account_id = summoner_data['accountId']
        puu_id = summoner_data['puuid']

        # Get the info needed to retrieve the summoner profile icon from data dragon assets
        profile_icon_id = summoner_data['profileIconId']
        summoner_image = "{}.png".format(profile_icon_id)

        # create_user() tries to add the author and summoner name to the 'users' table on the SQL database. It returns
        # a boolean value that determines whether the record was created or not and stores in the variable 'created'.
        # Returns false if the user's discord ID already exists in the database.
        created = db_handler.create_user(author.id, author.name, summoner_name, summoner_id, account_id, puu_id)

        # Send message to confirm whether or not the summoner has been mapped to author's discord account
        if created:
            version = riot_api.league_version
            file = discord.File("dragontail-{}/{}/img/profileicon/{}".format(version, version, summoner_image),
                                filename=summoner_image)
            user_created = discord.Embed(
                title="{}".format(summoner_name),
                description="This summoner is now linked to your account!",
                color=0xdfdf00
            )
            user_created.set_thumbnail(url="attachment://{}".format(summoner_image))
            await ctx.send(file=file, embed=user_created)
            print("{} assigned to {}, ID: {}".format(summoner_name, author, author.id))
        else:
            await ctx.send("There was a problem adding {} to your adding".format(summoner_name))

    async def does_not_exist():
        dne_embed = discord.Embed(
            title='<:no_entry_sign:647646871459987458>  Orianna Add Command',
            description="Summoner does not exist in this region",
            color=embed_color
        )
        await ctx.send(embed=dne_embed)
        return

    # Command Dispatcher: Calls different function based on response code returned from Riot API request. If the
    # summoner exists (code 200), then we will link that summoner to the discord user's ID and store it in the SQL
    # database. If the summoner does not exist (code 404), then Orianna will return an embed informing the user that the
    # summoner name does not exist in this region
    dispatcher = {200: create_user,
                  404: does_not_exist,
                  }
    try:
        await dispatcher[response_status]()
        return
    except KeyError:
        print("Ori Add Command: {} code not in dispatcher".format(response_status))


@ori.command(name='remove', help='Remove summoner from discord account')
async def remove(ctx):

    # Get the command author id
    author = ctx.message.author

    # remove_user():
    # returns (True, Summoner Name) if user exists and is succesfully removed.
    # Otherwise, returns (False, None)

    removed, summoner_name = db_handler.remove_user(author.id)

    if removed:
        embed = discord.Embed(
            title='<:ballot_box_with_check:647645266257772554>  Orianna Remove Command',
            description="**{}** is no longer linked to your account".format(summoner_name),
            color=embed_color
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title='<:no_entry_sign:647646871459987458>  Orianna Remove Command',
            description="There is currently no summoner linked to your account\n"
                        "To add a summoner, try the `!ori add [summoner name]` command",
            color=embed_color
        )
        await ctx.send(embed=embed)


@ori.command(name='top10', help='Show your top 10 mastery champions')
async def top10(ctx):

    # Get the command author
    author = ctx.message.author

    # Try to get summoner id and name from the user database
    db_summoner_id = db_handler.get_summoner_id(author.id)
    db_summoner_name = db_handler.get_summoner_name(author.id)

    # If user exists in database, then do the following
    if db_summoner_id:

        # API request for summoner's top 10 champion sorted by mastery score and get cached champion list
        top_10 = riot_api.call_top_10_mastery(db_summoner_id)
        champion_list = riot_api.champion_data_by_id

        # API request for fresh summoner data (to get most up-to-date profile icon)
        summoner_data = riot_api.call_summonerById(db_summoner_id)

        # Get profile icon id from summoner data dict
        profile_icon_id = summoner_data['profileIconId']
        summoner_image_file = "{}.png".format(profile_icon_id)

        # Get league version
        version = riot_api.league_version

        file = discord.File("dragontail-{}/{}/img/profileicon/{}".format(version, version, summoner_image_file),
                            filename=summoner_image_file)
        embed = discord.Embed(
            color=embed_color,
            description="Top 10 champions are:"
        )

        champ_value = ''
        points_value = ''
        last_played_value = ''
        for emoji in emojis:
            print(emoji)

        for champion in top_10:
            champion_name = champion_list[str(champion['championId'])]['name']
            champ_value += "<:{}:{}> **{}**\n".format(champion_name, emojis[champion_name], champion_name.capitalize())
            points_value += "{:,}\n".format(champion['championPoints'])
            last_played_value += "{}\n".format(datetime.date.fromtimestamp(champion['lastPlayTime']/1000).strftime(
                "%b %d, %Y"))

        embed.set_author(name="Mastery: {}".format(db_summoner_name.title()), icon_url="attachment://{}".format(
            summoner_image_file))
        embed.add_field(name="Champion", value=champ_value)
        embed.add_field(name="Mastery Points", value=points_value)
        embed.add_field(name="Last Played", value=last_played_value, inline=True)
        await ctx.send(file=file, embed=embed)
    else:
        embed = discord.Embed(
            title=":no_entry_sign: Orianna top10 Command",
            description="You don't have a summoner linked yet.\n"
                        "To link a summoner, try the `!ori add [summoner name]` command",
            color=embed_color
        )

        await ctx.send(embed=embed)


@ori.command(name='patchnotes', help="Link the latest league of legends patch notes")
async def patch_notes(ctx, game):
    if game == 'lol':

        version = riot_api.get_patch_url('lol')
        patch = ''
        delimiter_count = 0
        for char in version:
            if char != '.':
                patch += char
            else:
                delimiter_count += 1
            if delimiter_count == 2:
                break
        title_patch = "{}.{}{}".format(patch[0], patch[1], patch[2])
        embed = discord.Embed(
            title="League of Legends Patch {} Notes".format(title_patch),
            description="The latest patch notes",
            color=embed_color,
            url="https://na.leagueoflegends.com/en/news/game-updates/patch/patch-{}-notes".format(patch)

        )
        embed.set_image(url="https://na.leagueoflegends.com/sites/default/files/styles/wide_small/public/upload/patch_."
                            "{}_notes_header.jpg".format(title_patch))

        await ctx.send(embed=embed)

    elif game == 'tft':
        version = riot_api.get_patch_url('tft')
        title_patch = "{}.{}{}".format(version[0], version[1], version[2])
        embed = discord.Embed(
            title="Teamfight Tactics Patch {} Notes".format(title_patch),
            description="The latest patch notes",
            color=embed_color,
            url="https://na.leagueoflegends.com/en/news/game-updates/patch/teamfight-tactics-patch-{}-notes".format(
                version)
        )
        embed.set_image(
            url="https://na.leagueoflegends.com/sites/default/files/styles/wide_small/public/upload/tft_patch"
                "_{}_notes_header.jpg".format(title_patch))

        await ctx.send(embed=embed)


@ori.command(name="info", help="get champion info")
async def info(ctx, *champion_name):
    champion = ''.join(word.lower() for word in champion_name)
    try:
        version = riot_api.league_version
        champion_data = riot_api.champion_data_by_name[champion]
        stats = champion_data['stats']
        champion_info = champion_data['info']
        spells = champion_data['spells']
        champion_thumbnail = champion_data['image']['full']
        file = discord.File("dragontail-{}/{}/img/champion/{}".format(version, version, champion_thumbnail),
                            filename=f"{champion_thumbnail}")
        embed = discord.Embed(
            description="{}, {}:".format(champion, champion_data['title']),
            color=embed_color
        )
        embed.set_author(name="Orianna Info Command")
        embed.set_thumbnail(url="attachment://{}".format(champion_thumbnail))

        type_value = champion_data['tags'][0]
        if len(champion_data['tags']) > 1:
            type_value += "/{}".format(champion_data['tags'][1])
        embed.add_field(name="Type: ", value=type_value, inline=True)
        embed.add_field(name="Difficulty: ", value="{}/10".format(champion_info['difficulty'], inline=True))
        embed.add_field(name="Blurb", value="```{}```".format(champion_data['blurb']), inline=False)
        embed.add_field(name="Stats",
                        value="**HP**: {:.2f} (+{:.2f})\n"
                              "**HP Reg**: {:.2f} (+{:.2f})\n"
                              "**MP**: {:.2f} (+{:.2f})\n"
                              "**MP Reg**: {:.2f} (+{:.2f})\n"
                              "**Speed**: {}\n\n"
                              # TODO Add detailed spell information
                              "**[Q]**: {}\n"
                              "**[W]**: {}\n"
                              "**[E]**: {}\n"
                              "**[R]**: {}".format(stats['hp'], stats['hpperlevel'], stats['hpregen'],
                                                   stats['hpregenperlevel'], stats['mp'], stats['mpperlevel'],
                                                   stats['mpregen'], stats['mpregenperlevel'], stats['movespeed'],
                                                   spells[0]['name'], spells[1]['name'], spells[2]['name'],
                                                   spells[3]['name']),
                        inline=True)
        embed.add_field(name="Stats",
                        value="**Att Dmg**: {:.2f} (+{:.2f})\n"
                              "**Att Spd**: {}\n"
                              "**Att Rng**: {})\n"
                              "**Armor**: {:.2f} (+{:.2f})\n"
                              "**MR**: {:.2f} (+{:.2f})\n\n"
                              "**Attack**: {}\n"
                              "**Magic**: {}\n"
                              "**Defense**: {}".format(stats['attackdamage'], stats['attackdamageperlevel'],
                                                       stats['attackspeed'], stats['attackrange'], stats['armor'],
                                                       stats['armorperlevel'], stats['spellblock'],
                                                       stats['spellblockperlevel'], champion_info['attack'],
                                                       champion_info['magic'], champion_info['defense']),
                        inline=True
                        )

        await ctx.send(file=file, embed=embed)
    except KeyError:
        embed = discord.Embed(
            title="<:no_entry_sign:650497964195840061> Orianna Info Command",
            description="Why must you deceive me?\n "
                        "Please provide a real champion name.",
            color=embed_color
        )
        await ctx.send(embed=embed)


@ori.command(name='lg', help='Get stats from your last played game')
async def lastgame(ctx, stat):

    def get_role_emoji(summoner):
        duo_codes = {'DUO_CARRY': 'bot',
                     'DUO_SUPPORT': 'support'}
        if summoner.lane == 'BOTTOM':
            emoji_name = duo_codes[summoner.role]
        else:
            emoji_name = summoner.lane.lower()
        emoji_code = emojis.get(emoji_name, 'Emoji is not available')

        return emoji_code, emoji_name

    champion_list = riot_api.champion_data_by_id

    # get discord user
    author = ctx.message.author
    # get riot account ID from database using the author's discord ID
    account_id = db_handler.get_account_id(author.id)

    # api request the user's matchlist of last 100 matches
    matchlist = riot_api.request_matchlist(account_id)
    # get the last game played at matchlist index 0
    last_match_id = matchlist['matches'][0]['gameId']

    # api request the data from the last match played
    match_data = riot_api.request_match(last_match_id)
    game_duration = match_data['gameDuration']/60

    # initialize lists to use for embed
    player_list = []
    summoner_names = {}

    # # iterate through data and map participant ID's to summoner names and store in player_list dict
    for player in match_data['participantIdentities']:
        summoner_names.setdefault(player['participantId'], player['player']['summonerName'])

    for participant in match_data['participants']:
        summoner_name = summoner_names[participant['participantId']]
        champion_id = participant['championId']
        team_id = participant['teamId']
        stats = participant['stats']
        timeline = participant['timeline']
        kills = stats['kills']
        deaths = stats['deaths']
        assists = stats['assists']
        dmg_to_champions = stats['totalDamageDealtToChampions']
        dmg_to_objectives = stats['damageDealtToObjectives']
        turret_kills = stats['turretKills']
        inhibitor_kills = stats['inhibitorKills']
        cs_score = stats['totalMinionsKilled']
        vision_score = stats['visionScore']
        wards_purchased = stats['visionWardsBoughtInGame']
        wards_placed = stats['wardsPlaced']
        wards_killed = stats['wardsKilled']
        lane = timeline['lane']
        role = timeline['role']
        creeps_per_min_deltas = timeline['creepsPerMinDeltas']
        try:
            cs_diff_per_min_deltas = timeline['csDiffPerMinDeltas']
        except KeyError:
            cs_diff_per_min_deltas = None

        player = Player(summoner_name, champion_id, team_id, lane, role, kills, deaths, assists, dmg_to_champions,
                        dmg_to_objectives, turret_kills, inhibitor_kills, cs_score, vision_score, wards_purchased,
                        wards_placed, wards_killed, creeps_per_min_deltas, cs_diff_per_min_deltas)
        player_list.append(player)

    async def vision():

        champions = riot_api.champion_data_by_id
        summoner = ''
        vision_stats_column = ''
        vision_score_column = ''
        player_list.sort(key=lambda x: x.vision_score, reverse=True)
        for player in player_list:
            champion_name = champions[str(player.champion_id)]['name'].replace("'", "").lower()
            role_emoji_code, role_emoji_name = get_role_emoji(player)
            champion_emoji_code = emojis[champion_name]
            summoner += "<:{}:{}> <:{}:{}> {}\n".format(champion_name, champion_emoji_code, role_emoji_name,
                                                        role_emoji_code, player.summoner_name)
            vision_stats_column += "{} / {} / {}\n".format(player.wards_placed, player.wards_killed,
                                                           player.wards_purchased)
            vision_score_column += f"{player.vision_score} ... ( {round(player.vision_score/game_duration, 1)}/min )\n"

        embed = discord.Embed(
            color=embed_color
        )
        embed.set_author(name='Vision Score')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/673248997451759646.png?v=1")
        embed.add_field(name='Summoner', value=summoner)
        embed.add_field(name='Pl/Cl/Pinks', value=vision_stats_column)
        embed.add_field(name='Vision Score', value=vision_score_column)

        await ctx.send(embed=embed)

    async def damage():

        player_list.sort(key=lambda x: x.dmg_to_champions + x.dmg_to_objectives, reverse=True)

        players = list(player.summoner_name[0:4] for player in player_list)
        damage_legend = ['Champion Damage', 'Objective Damage']
        pos = np.arange(len(players))
        x = list(player.dmg_to_champions for player in player_list)
        y = list(player.dmg_to_objectives for player in player_list)
        # 956D28
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.set_facecolor("#303136")
        plt.bar(pos, x, color="#956D28", ec="black")
        plt.bar(pos, y, color="#0F5564", ec="black", bottom=x)
        plt.xticks(pos, players)
        plt.xlabel('Summoner', fontsize=14)
        plt.ylabel('Damage', fontsize=14)
        plt.title('Damage Contribution by Summoner', fontsize=16)
        plt.legend(damage_legend, loc=1)
        plt.savefig("champion_damage.png")
        file = discord.File("champion_damage.png", filename="champion_damage.png")

        summoner = ''
        dmg_to_champions = ''
        dmg_to_objectives = ''
        for player in player_list:
            champion_name = champion_list[str(player.champion_id)]['name'].replace("'", "").replace(" ", "").lower()
            role_emoji_code, role_emoji_name = get_role_emoji(player)
            champion_emoji_code = emojis[champion_name]
            summoner += "<:{}:{}> <:{}:{}> {}\n".format(champion_name, champion_emoji_code, role_emoji_name, role_emoji_code, player.summoner_name[0:15])
            dmg_to_champions += "{:,}\n".format(player.dmg_to_champions)
            dmg_to_objectives += "{:,}\n".format(player.dmg_to_objectives)
        embed = discord.Embed(
            color=embed_color
        )
        embed.set_author(name='Damage Report')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/643972725114667037.png?v=1")
        embed.set_image(url="attachment://champion_damage.png")
        embed.add_field(name='Summoner', value=summoner)
        embed.add_field(name='Champ Dmg', value=dmg_to_champions)
        embed.add_field(name='Obj Dmg', value=dmg_to_objectives)
        await ctx.send(file=file, embed=embed)

    async def creep_score():

        summoner = ''
        creep_score = ''
        cs_diff = ''

        player_list.sort(key=lambda x: x.cs_score, reverse=True)
        for player in player_list:
            opposite_player = list(filter(lambda x: x.role == player.role and x.team_id != player.team_id, player_list))[0]
            champion_name = champion_list[str(player.champion_id)]['name'].replace("'", "").lower()
            role_emoji_code, role_emoji_name = get_role_emoji(player)
            champion_emoji_code = emojis[champion_name]
            summoner += "<:{}:{}> <:{}:{}> {}\n".format(champion_name, champion_emoji_code, role_emoji_name,
                                                        role_emoji_code, player.summoner_name)
            creep_score += f"{player.cs_score}\n"
            cs_diff += f"{player.cs_score - opposite_player.cs_score}\n"

        embed = discord.Embed(color=embed_color)
        embed.set_author(name="Creep Score")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/675044023823761419.png?v=1")
        embed.add_field(name='Summoner', value=summoner)
        embed.add_field(name='CS', value=creep_score)
        embed.add_field(name='CS Diff', value=cs_diff)
        await ctx.send(embed=embed)

    dispatcher = {'vision': vision,
                  'damage': damage,
                  'cs': creep_score,
                  }
    await dispatcher[stat]()


# @ori.command(name='map')
# async def display_map(ctx):
#     im = plt.imread("map12.png")
#     plt.imshow(im)
#     plt.xlim(0, 1000)
#     plt.ylim(0, 1000)
#     plt.scatter(500, 500)
#     plt.scatter(800, 300)
#     plt.scatter(100, 600)
#
#     plt.savefig("map.png")
#     file = discord.File("map.png", filename="map.png")
#     embed = discord.Embed(color=embed_color)
#     embed.set_image(url="attachment://map.png")
#     await ctx.send(file=file, embed=embed)


ori.run(discord_token)

