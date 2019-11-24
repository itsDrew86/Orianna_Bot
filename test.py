import json

with open("dragontail-9.23.1/9.23.1/data/en_US/summoner.json", encoding='utf8') as json_file:
    data = json.load(json_file)['data']
    print(data)

# with open("dragontail-9.23.1/9.23.1/data/en_US/champion/Aatrox.json", encoding='utf8') as json_file:
#     data = json.load(json_file)['data']
#     print(data)


