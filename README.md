# Orianna_Bot

A discord bot that connects to the Riot League of Legends (LoL) API to do useful things... hopefully. 

The goal of the project
is to teach myself how to work with RESTful API's, JSON and SQL and hopefully create a useful app in the process.

## Technologies
#####Project is created with:

- Python 3.7

- SQLite 3.0

- discord.py 1.2.5

- requests 2.22.0

- python-dotenv 0.10.3

## Setup

#####You will need to create a .env file to store two environment variables:

1. `DISCORD_TOKEN`: This is the authorization token for the bot. A discord bot can be set up
 [here](https://discordapp.com/developers/applications/). Setting up a bot is beyond the scope of this document, but
 [this](https://realpython.com/how-to-make-a-discord-bot-python/) is a good place to start. 
 
2. `LEAGUE_API_TOKEN`: You can get one at the Riot developer portal [here](https://developer.riotgames.com/). There is
no approval process for a 24-hour access token, but you will need to register an account. You can sign in with your
league of legends account if you already have one.

Riot provides a zip file with all data and image assets. Orianna Bot still pulls all of it's data from the Riot API to
ensure she is using the most up-to-date information. However, since the image assets don't change often, I've opted to
use the provided zip to pull the assets locally to optimize performance. 

You'll need to download the [Data Dragon Zip File](https://ddragon.leagueoflegends.com/cdn/dragontail-9.3.1.tgz) and
unzip to dragontail-9.3.1 in the Orianna_Bot project directory. 

## Project Status

The project is in the early stages of development.

##### Planned Features (Loose and subject to change):

- Link your LoL summoner account to your discord account.

- Get various personal statistics, such as: your top champions (ordered by mastery points), champion last played dates
win/loss counts, rank, information on last match played, etc..

- Get static data, such as: Champion abilities, champion lore, item costs, item stats/descriptions.

- Get info on skins, their costs and current sales/discounts, if applicable

- Post news updates and patch notes to specified channel