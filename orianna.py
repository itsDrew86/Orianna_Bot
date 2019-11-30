import os
import discord
from discord.ext import commands
import riot_api
import db_handler
import datetime
import time

discord_token = os.getenv('DISCORD_TOKEN')
league_token = os.getenv('LEAGUE_API_TOKEN')


embed_color = 0xdfdf00

ori = commands.Bot(command_prefix='!ori ')

@ori.event
async def on_ready():
    print(f'{ori.user.name} has connected to Discord!')


@ori.command(name='add', help='Connects your Summoner Account to your Discord Account.')
async def add(ctx, summoner_name):

    # Get the command author
    author = ctx.message.author

    # Check if the author is in the user database already.
    db_summoner_name = db_handler.get_summoner_name(author.id)
    if db_summoner_name != False:

        # Let the author know their account is already linked to a summoner
        embed=discord.Embed(
            title="<:no_entry_sign:647646871459987458>  Orianna Add Command",
            description="**{}** is already linked to your account!\n"
                        "If you wish to remove it, try the `!ori remove` command".format(db_summoner_name),
            color=0xdfdf00
        )
        await ctx.send(embed=embed)
        return

    # Else if the author is not already in the database, try to add them

    # Get the summoner Data
    response_status, summoner_data = riot_api.call_summonerByName(summoner_name)

    async def create_user():
        summoner_id = summoner_data['id']
        account_id = summoner_data['accountId']
        puu_id = summoner_data['puuid']
        profile_icon_id = summoner_data['profileIconId']
        summoner_image = "{}.png".format(profile_icon_id)

        # Add the author and summoner name to the user database
        created = db_handler.create_user(author.id, author.name, summoner_name, summoner_id, account_id, puu_id)

        # Send message to confirm summoner has been mapped to author's discord account
        if created:
            version = riot_api.league_version
            file = discord.File("dragontail-{}/{}/img/profileicon/{}".format(version, version, summoner_image),
                                filename=summoner_image)
            embed = discord.Embed(
                title="{}".format(summoner_name),
                description="This summoner is now linked to your account!",
                color=0xdfdf00
            )
            embed.set_thumbnail(url="attachment://{}".format(summoner_image))
            await ctx.send(file=file, embed=embed)
            print("{} assigned to {}, ID: {}".format(summoner_name, author, author.id))
        else:
            await ctx.send("There was a problem adding {} to your adding".format(summoner_name))

    async def does_not_exist():
        embed = discord.Embed(
            title='<:no_entry_sign:647646871459987458>  Orianna Add Command',
            description="Summoner does not exist in this region",
            color=embed_color
        )
        await ctx.send(embed=embed)
        return

    dispatcher = {200: create_user,
                  404: does_not_exist,
                  }
    try:
        await dispatcher[response_status]()
        return
    except KeyError:
        print("Ori Add Command: {} code not in dispatcher".format(response_status))


@ori.command(name='top5', help='Show your top 5 mastery champions')
async def top5(ctx):

    # Get the command author
    author = ctx.message.author

    # Try to get summoner id and name from the user database
    db_summoner_id = db_handler.get_summoner_id(author.id)
    db_summoner_name = db_handler.get_summoner_name(author.id)

    # If user exists in database, then do the following
    if db_summoner_id != False:

        # API request for summoner's top 5 champion sorted by mastery score and get cached champion list
        top_5 = riot_api.call_top_5_mastery(db_summoner_id)
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
        # for champ in top_5:
        #     description += f"**{champion_list[str(champ['championId'])]['name']}** - {champ['championPoints']}\n"
        embed = discord.Embed(
            color=embed_color,
            description="Top 5 champions are:"
        )

        champ_value = ''
        points_value = ''
        last_played_value = ''



        for champion in top_5:
            champ_value += "**{}**\n".format(champion_list[str(champion['championId'])]['name'])
            points_value += "{:,}\n".format(champion['championPoints'])
            last_played_value += "{}\n".format(datetime.date.fromtimestamp(champion['lastPlayTime']/1000).strftime("%b %d, %Y"))

        embed.set_author(name="Mastery: {}".format(db_summoner_name.title()), icon_url="attachment://{}".format(summoner_image_file))
        embed.add_field(name="Champion", value=champ_value)
        embed.add_field(name="Mastery Points", value=points_value)
        embed.add_field(name="Last Played", value=last_played_value, inline=True)



        await ctx.send(file=file, embed=embed)


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


@ori.command(name='patchnotes', help="Link the latest league of legends patch notes")
async def patch_notes(ctx, game):
    if game == 'lol':

        version = riot_api.get_league_version()
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
        embed.set_image(url="https://na.leagueoflegends.com/sites/default/files/styles/wide_small/public/upload/patch_.{}_notes_header.jpg".format(title_patch))

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
            url="https://na.leagueoflegends.com/sites/default/files/styles/wide_small/public/upload/tft_patch_{}_notes_header.jpg".format(
                title_patch))

        await ctx.send(embed=embed)


@ori.command(name="info", help="get champion info")
async def info(ctx, *champion_name):


    champion = ''.join(word.lower() for word in champion_name)

    version = riot_api.get_league_version()
    champion_data = riot_api.champion_data_by_name[champion]
    stats = champion_data['stats']
    info = champion_data['info']
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
    embed.add_field(name="Difficulty: ", value="{}/10".format(info['difficulty'], inline=True))
    embed.add_field(name="Blurb", value="```{}```".format(champion_data['blurb']), inline=False)
    embed.add_field(name="Stats",
                    value="**HP**: {:.2f} (+{:.2f})\n"
                          "**HP Reg**: {:.2f} (+{:.2f})\n"
                          "**MP**: {:.2f} (+{:.2f})\n"
                          "**MP Reg**: {:.2f} (+{:.2f})\n"
                          "**Speed**: {}\n\n"
                          #TODO Add detailed spell information
                          "**[Q]**: {}\n"
                          "**[W]**: {}\n"
                          "**[E]**: {}\n"
                          "**[R]**: {}".format(stats['hp'], stats['hpperlevel'], stats['hpregen'],
                                                   stats['hpregenperlevel'], stats['mp'], stats['mpperlevel'],
                                                   stats['mpregen'], stats['mpregenperlevel'], stats['movespeed'],
                                                   spells[0]['name'], spells[1]['name'], spells[2]['name'], spells[3]['name']),
                    inline=True
                    )
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
                                                   stats['armorperlevel'], stats['spellblock'], stats['spellblockperlevel'],
                                                   info['attack'], info['magic'], info['defense']),
                    inline=True
                    )

    await ctx.send(file=file, embed=embed)




ori.run(discord_token)