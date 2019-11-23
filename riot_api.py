import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
riot_token = os.getenv('LEAGUE_API_TOKEN')

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
        return data

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

def call_top_5_mastery(summoner_id):
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
    data = sorted(data, key=lambda x: x['championPoints'], reverse=True)[:5]
    print(data)
    return data

def call_championList():
    champion_list = {}
    response = requests.get("http://ddragon.leagueoflegends.com/cdn/9.23.1/data/en_US/champion.json")
    data = response.json()['data']
    for champion in data.values():
        champion_list[int(champion['key'])] = champion['name']
    return champion_list


