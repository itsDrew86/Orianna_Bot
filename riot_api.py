import requests
import os
from dotenv import load_dotenv
import json
from discord import File as discord_file
from bs4 import BeautifulSoup
import time


load_dotenv()
riot_token = os.getenv('LEAGUE_API_TOKEN')


champion_data_by_name = {}
champion_data_by_id = {}

headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": riot_token,
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
}

errors = {400: 'Bad request',
          401: 'Unauthorized',
          403: 'Forbidden',
          404: 'Data not found',
          405: 'Method not allowed',
          415: 'Unsupported media type',
          429: 'Rate limit exceeded',
          500: 'Internal server error',
          502: 'Bad gateway',
          503: 'Service unavailable',
          504: 'Gateway timeout',}


def request_matchlist(account_id):
    response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}'.format(account_id), headers=headers)
    while response.status_code != 200:
        print(f'API Response: {response.status_code} - {errors[response.status_code]}. Sleeping 1')
        time.sleep(1)
        print('Retrying Request')
        response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}'.format(account_id), headers=headers)
    print('Matchlist Request Success')
    response = response.json()
    return response

def request_match(match_id):
    response = requests.get(f'https://na1.api.riotgames.com/lol/match/v4/matches/{match_id}', headers=headers)
    while response.status_code != 200:
        print(f'API Response: {response.status_code} - {errors[response.status_code]}. Sleeping 1')
        time.sleep(1)
        print('Retrying request')
        response = requests.get(f'https://na1.api.riotgames.com/lol/match/v4/matches/{match_id}', headers=headers)
    response = response.json()
    return response


def get_request_error(err):
    pass


def call_summonerByName(summoner_name):
        # response example:
        # {
        #     "profileIconId": 4379,
        #     "name": "Wishamuhfucawud",
        #     "puuid": "_C21_AZO5H5OcGI5Hcv1KjDT8N2kS7F9EX3fwPGRKOxvH0zX8wE-q-_J6WtxWH15k7Xw_fLpDATwWA",
        #     "summonerLevel": 181,
        #     "accountId": "gTOFnrmF7aa4VIzLIptO0Gn9Ng7T-JbYhljfkZeN_8SakA",
        #     "id": "TJEAB0ncKyYGWPbXEkFbNoEgkoUMYxJXzgVFQFvmXn8GVKQ",
        #     "revisionDate": 1574320866000
        # }
        response = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}",
                                headers=headers)
        data = response.json()
        return response.status_code, data


def call_summonerById(summoner_id):
    # response example:
    # {
    #     "profileIconId": 4379,
    #     "name": "Wishamuhfucawud",
    #     "puuid": "_C21_AZO5H5OcGI5Hcv1KjDT8N2kS7F9EX3fwPGRKOxvH0zX8wE-q-_J6WtxWH15k7Xw_fLpDATwWA",
    #     "summonerLevel": 182,
    #     "accountId": "gTOFnrmF7aa4VIzLIptO0Gn9Ng7T-JbYhljfkZeN_8SakA",
    #     "id": "TJEAB0ncKyYGWPbXEkFbNoEgkoUMYxJXzgVFQFvmXn8GVKQ",
#     "revisionDate": 1574398327000
    # }
    response = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}", headers=headers)
    data = response.json()
    return data


def call_top_10_mastery(summoner_id):
    # response example:
    # [
    #     {
    #         "championLevel": 7,
    #         "chestGranted": true,
    #         "championPoints": 366930,
    #         "championPointsSinceLastLevel": 345330,
    #         "championPointsUntilNextLevel": 0,
    #         "summonerId": "TJEAB0ncKyYGWPbXEkFbNoEgkoUMYxJXzgVFQFvmXn8GVKQ",
    #         "tokensEarned": 0,
    #         "championId": 61,
    #         "lastPlayTime": 1574391499000
    #     },
    #     {
    #         "championLevel": 7,
    #         "chestGranted": true,
    #         "championPoints": 169695,
    #         "championPointsSinceLastLevel": 148095,
    #         "championPointsUntilNextLevel": 0,
    #         "summonerId": "TJEAB0ncKyYGWPbXEkFbNoEgkoUMYxJXzgVFQFvmXn8GVKQ",
    #         "tokensEarned": 0,
    #         "championId": 81,
    #         "lastPlayTime": 1574393677000
    #     }
    # ]
    response = requests.get(f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}",
                            headers=headers)
    data = response.json()
    data = sorted(data, key=lambda x: x['championPoints'], reverse=True)[:10]
    return data


def get_league_version():
    response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    data = response.json()
    return data[0]


def cache_champion_data():
    with open("dragontail-{}/{}/data/en_US/championFull.json".format(league_version, league_version), encoding='utf8')\
            as json_file:
        data = json.load(json_file)['data']
        temp_dict = {}
        for value in data.values():
            temp_dict[value['id'].lower().strip("'")] = value

        champion_data_by_name.update(temp_dict)
        wukong = champion_data_by_name['monkeyking']
        champion_data_by_name['wukong'] = wukong
        temp_dict = {}
        for value in data.values():
            value['name'] = value['name'].replace("'","").replace(".","").replace(" ", "").lower()
            temp_dict[value['key']] = value
        champion_data_by_id.update(temp_dict)
        champion_data_by_id['20']['name'] = 'nunu'


def get_patch_url(game):
    url = "https://na.leagueoflegends.com/en/news/game-updates/patch"

    raw_html = requests.get(url=url, stream=True)
    html = BeautifulSoup(raw_html.content, 'html.parser')
    patches = html.select('h4')

    tft_patch = ''
    lol_patch = ''

    for patch in patches:
        if "Tactics" in patch.text and tft_patch == '':
            tft_patch = patch.text
            temp_str = ''
            for char in tft_patch:
                if char.isdigit():
                    temp_str += char
            tft_patch = temp_str
        if "Tactics" not in patch.text and lol_patch == '':
            lol_patch = patch.text
            temp_str = ''
            for char in lol_patch:
                if char.isdigit():
                    temp_str += char
            lol_patch = temp_str

    if game == 'tft':
        return tft_patch
    elif game == 'lol':
        return lol_patch


league_version = "10.3.1"
cache_champion_data()

