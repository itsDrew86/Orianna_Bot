import os
import discord
from discord.ext import commands
import riot_api
from random import randint
import db_handler

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
        profile_icon_id = summoner_data['profileIconId']
        summoner_image = "{}.png".format(profile_icon_id)

        # Add the author and summoner name to the user database
        created = db_handler.create_user(author.id, author.name, summoner_name, summoner_id)

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
async def top(ctx):

    # Get the command author
    author = ctx.message.author

    db_summoner_id = db_handler.get_summoner_id(author.id)
    db_summoner_name = db_handler.get_summoner_name(author.id)

    if db_summoner_id != False:

        # API request for summoner's top 5 champion sorted by mastery score
        top_5 = riot_api.call_top_5_mastery(db_summoner_id)

        champion_list = riot_api.call_championList()
        for champ in top_5:
            champ['name'] = champion_list[champ['championId']]

        print(type(top_5[0]['championId']))
        print(type(next(iter(champion_list))))
        description = "Top 5 champions are:\n\n" \
                      "**Champion/Points**\n"
        for champ in top_5:
            description += "**{}**".format(champion_list[champ['championId']]) + "{}\n".format(champ['championPoints'])

        embed = discord.Embed(
            title='Mastery: {}'.format(db_summoner_name),
            color=embed_color,
            description=description
            # description="Top 5 champions with most mastery points\n\n"
            #             "**Champion/Points**\n"
            #             "**{}** - {}\n"
            #             "**{}** - {}\n"
            #             "**{}** - {}\n"
            #             "**{}** - {}\n"
            #             "**{}** - {}".format(
            #     top_5[0]['name'], top_5[0]['championPoints'],
            #     top_5[1]['name'], top_5[1]['championPoints'],
            #     top_5[2]['name'], top_5[2]['championPoints'],
            #     top_5[3]['name'], top_5[3]['championPoints'],
            #     top_5[4]['name'], top_5[4]['championPoints'],
            )
        await ctx.send(embed=embed)


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


@ori.command(name='dick', help="Get mentioned user's dick size: !dick [@user]")
async def dick_size(ctx, user):
    value = randint(1, 16)
    await ctx.send(f"{user} has a {value}-inch penis.")


ori.run(discord_token)