import json 

with open('config.json', 'r') as cjson:
    config = json.load(cjson)

# contains the emoji ID and role ID for each rank in the server;
# rank names should match up with getRank function below
def getRankdata(season=''):
    if season == '':
        season = config['season']

    if season == 1 or season == 2:
        ranks = {
            "Master": {
                "color": "#0E0B0B",
                "url": "https://images-ext-2.discordapp.net/external/818NjPBjrnnWfyerw_2aEneujaXvbx8FqpFVDJb7QFo/%3Fv%3D1568666322577/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fmaster.png"},
            "Diamond": {
                "color": "#B6F2FF",
                "url": "https://images-ext-1.discordapp.net/external/vFN0gVHQfKiuibLwGiXLU1AyNakAvDW1Y6qAJz9OpIU/%3Fv%3D1568666334772/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fdiamond.png"},
            "Platinum": {
                "color": "#3fABB8",
                "url": "https://images-ext-2.discordapp.net/external/BOV2_4s_hHzyc_k86CmwRmBlCiWATO1_hhgMEocDD8w/%3Fv%3D1568666339226/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fplatinum.png"},
            "Gold": {
                "color": "#FFD700",
                "url": "https://images-ext-1.discordapp.net/external/TNePvgcc2x0r1XVCc7YvW6ESZHD6EhyipuD8tVXddl4/%3Fv%3D1568666343936/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fgold.png"},
            "Silver": {
                "color": "#7D8396",
                "url": "https://images-ext-2.discordapp.net/external/UY9xNJ5dHt09Er_ZNqPtt5KF6FHqZbxkQrt0k6JgrrU/%3Fv%3D1568666348185/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fsilver.png"},
            "Bronze": {
                "color": "#CD7F32",
                "url": "https://images-ext-2.discordapp.net/external/lyRHPXnzii9wSXhgffi8ugSrGSQCWEYc7Bo-YVUYGc8/%3Fv%3D1568666353508/https/cdn.glitch.com/3daabc84-e598-4559-b112-0a2f1ad29d80%252Fbronze.png"},
        }
    
    elif season == 3 or season == 4:
        ranks = {
            "Grandmaster": {
                "color": "#A3022C",
                "url": "https://i.imgur.com/EWXzu2U.png"},
            "Master": {
                "color": "#D9E1F2",
                "url": "https://i.imgur.com/3yBab63.png"},
            "Diamond": {
                "color": "#BDD7EE",
                "url": "https://i.imgur.com/RDlvdvA.png"},
            "Sapphire": {
                "color": "#286CD3",
                "url": "https://i.imgur.com/bXEfUSV.png"},
            "Platinum": {
                "color": "#3FABB8",
                "url": "https://i.imgur.com/8v8IjHE.png"},
            "Gold": {
                "color": "#FFD966",
                "url": "https://i.imgur.com/6yAatOq.png"},
            "Silver": {
                "color": "#D9D9D9",
                "url": "https://i.imgur.com/xgFyiYa.png"},
            "Bronze": {
                "color": "#C65911",
                "url": "https://i.imgur.com/DxFLvtO.png"},
            "Iron": {
                "color": "#817876",
                "url": "https://i.imgur.com/AYRMVEu.png"}
        }

    elif season >= 5:
        ranks = {
            "Grandmaster": {
                "emoji": "<:grandmaster:731579876846338161>",
                "roleid": 874340227177668699,
                "color": "#A3022C",
                "url": "https://i.imgur.com/EWXzu2U.png"},
            "Master": {
                "emoji": "<:master:731597294914502737>",
                "roleid": 874340298048831578,
                "color": "#D9E1F2",
                "url": "https://i.imgur.com/3yBab63.png"},
            "Diamond 2": {
                "emoji": "<:diamond:731579813386780722> 2",
                "roleid": 874340374083154030,
                "color": "#BDD7EE",
                "url": "https://i.imgur.com/RDlvdvA.png"},
            "Diamond 1": {
                "emoji": "<:diamond:731579813386780722> 1",
                "roleid": 874340476080238612,
                "color": "#BDD7EE",
                "url": "https://i.imgur.com/RDlvdvA.png"},
            "Sapphire 2": {
                "emoji": "<:sapphire:731579851802411068>",
                "roleid": 874340543923118130,
                "color": "#286CD3",
                "url": "https://i.imgur.com/bXEfUSV.png"},
            "Sapphire": {
                "emoji": "<:sapphire:731579851802411068>",
                "roleid": 874340543923118130,
                "color": "#286CD3",
                "url": "https://i.imgur.com/bXEfUSV.png"},
            "Sapphire 1": {
                "emoji": "<:sapphire:731579851802411068>",
                "roleid": 950073170071781467,
                "color": "#286CD3",
                "url": "https://i.imgur.com/bXEfUSV.png"},
            "Platinum 2": {
                "emoji": "<:platinum:542204444302114826> 2",
                "roleid": 874340619751931934,
                "color": "#3FABB8",
                "url": "https://i.imgur.com/8v8IjHE.png"},
            "Platinum 1": {
                "emoji": "<:platinum:542204444302114826> 1",
                "roleid": 874340697887637535,
                "color": "#3FABB8",
                "url": "https://i.imgur.com/8v8IjHE.png"},
            "Gold 2": {
                "emoji": "<:gold:731579798111125594> 2",
                "roleid": 874340761964003389,
                "color": "#FFD966",
                "url": "https://i.imgur.com/6yAatOq.png"},
            "Gold 1": {
                "emoji": "<:gold:731579798111125594> 1",
                "roleid": 874340824861794324,
                "color": "#FFD966",
                "url": "https://i.imgur.com/6yAatOq.png"},
            "Silver 2": {
                "emoji": "<:silver:731579781828575243> 2",
                "roleid": 874340970764861511,
                "color": "#D9D9D9",
                "url": "https://i.imgur.com/xgFyiYa.png"},
            "Silver 1": {
                "emoji": "<:silver:731579781828575243> 1",
                "roleid": 874341090579349504,
                "color": "#D9D9D9",
                "url": "https://i.imgur.com/xgFyiYa.png"},
            "Bronze 2": {
                "emoji": "<:bronze:731579759712010320> 2",
                "roleid": 874341171399376896,
                "color": "#C65911",
                "url": "https://i.imgur.com/DxFLvtO.png"},
            "Bronze 1": {
                "emoji": "<:bronze:731579759712010320> 1",
                "roleid": 874342922601005066,
                "color": "#C65911",
                "url": "https://i.imgur.com/DxFLvtO.png"},
            "Iron 2": {
                "emoji": "<:iron:731579735544430703> 2",
                "roleid": 874343078784274502,
                "color": "#817876",
                "url": "https://i.imgur.com/AYRMVEu.png"},
            "Iron 1": {
                "emoji": "<:iron:731579735544430703> 1",
                "roleid": 874343146316783708,
                "color": "#817876",
                "url": "https://i.imgur.com/AYRMVEu.png"}
        }

    return ranks


# this is where you define the MMR thresholds for each rank
def getRank(mmr: int, season=''):
    if season == '':
        season = config['season']

    if season == 1 or season == 2:
        if mmr >=9000:
            return "Master"
        elif mmr >= 7000:
            return "Diamond"
        elif mmr >= 5500:
            return "Platinum"
        elif mmr >= 4000:
            return "Gold"
        elif mmr >= 2500:
            return "Silver"
        else:
            return "Bronze"
    
    elif season == 3:
        if mmr >= 12500:
            return "Grandmaster"
        elif mmr >= 11000:
            return "Master"
        elif mmr >= 9500:
            return "Diamond"
        elif mmr >= 8000:
            return "Sapphire"
        elif mmr >= 6500:
            return "Platinum"
        elif mmr >= 5000:
            return "Gold"
        elif mmr >= 3500:
            return "Silver"
        elif mmr >= 2000:
            return "Bronze"
        else:
            return "Iron"

    elif season == 4:
        if mmr >= 14500:
            return "Grandmaster"
        elif mmr >= 13000:
            return "Master"
        elif mmr >= 11500:
            return "Diamond"
        elif mmr >= 10000:
            return "Sapphire"
        elif mmr >= 8500:
            return "Platinum"
        elif mmr >= 7000:
            return "Gold"
        elif mmr >= 5500:
            return "Silver"
        elif mmr >= 4000:
            return "Bronze"
        else:
            return "Iron"

    elif season == 5:
        if mmr >= 14000:
            return "Grandmaster"
        elif mmr >= 13000:
            return "Master"
        elif mmr >= 12000:
            return "Diamond 2"
        elif mmr >= 11000:
            return "Diamond 1"
        elif mmr >= 10000:
            return "Sapphire"
        elif mmr >= 9000:
            return "Platinum 2"
        elif mmr >= 8000:
            return "Platinum 1"
        elif mmr >= 7000:
            return "Gold 2"
        elif mmr >= 6000:
            return "Gold 1"
        elif mmr >= 5000:
            return "Silver 2"
        elif mmr >= 4000:
            return "Silver 1"
        elif mmr >= 3000:
            return "Bronze 2"
        elif mmr >= 2000:
            return "Bronze 1"
        elif mmr >= 1000:
            return "Iron 2"
        else:
            return "Iron 1"

    elif season == 6 or season == 7:
        if mmr >= 15000:
            return "Grandmaster"
        elif mmr >= 14000:
            return "Master"
        elif mmr >= 13000:
            return "Diamond 2"
        elif mmr >= 12000:
            return "Diamond 1"
        elif mmr >= 11000:
            return "Sapphire 2"
        elif mmr >= 10000:
            return "Sapphire 1"
        elif mmr >= 9000:
            return "Platinum 2"
        elif mmr >= 8000:
            return "Platinum 1"
        elif mmr >= 7000:
            return "Gold 2"
        elif mmr >= 6000:
            return "Gold 1"
        elif mmr >= 5000:
            return "Silver 2"
        elif mmr >= 4000:
            return "Silver 1"
        elif mmr >= 3000:
            return "Bronze 2"
        elif mmr >= 2000:
            return "Bronze 1"
        elif mmr >= 1000:
            return "Iron 2"
        else:
            return "Iron 1"