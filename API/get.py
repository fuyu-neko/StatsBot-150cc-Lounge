import aiohttp
import json
from datetime import datetime, timedelta

headers = {'Content-type': 'application/json'}

with open('credentials.json', 'r') as cjson:
    creds = json.load(cjson)

with open('./config.json', 'r') as cjson:
    config = json.load(cjson)


async def getStrikes(name, season=''):
    if season == '':
        season = config['season']
    fromDate = datetime.utcnow() - timedelta(days=30)
    base_url = creds['website_url'] + '/api/penalty/list?'
    request_text = ("name=%s&isStrike=true&from=%s"
                    % (name, fromDate.isoformat()))
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return False
            strikes = await resp.json()
            return strikes

async def getALLStrikes(name, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/penalty/list?'
    request_text = ("name=%s&isStrike=true"
                    % (name,))
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return False
            strikes = await resp.json()
            return strikes


async def checkNames(names, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player?'
    on_lbs = []
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        for name in names:
            request_text = "name=%s" % name
            request_url = base_url + request_text + '&season=%s' % season
            async with session.get(request_url, headers=headers) as resp:
                if resp.status != 200:
                    on_lbs.append(False)
                    continue
                playerData = await resp.json()
                on_lbs.append(playerData["name"])
    return on_lbs


async def getPlayer(name, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player?'
    request_text = "name=%s" % name
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            player = await resp.json()
            return player


async def getPlayerFromMKC(mkcid, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player?'
    request_text = "mkcId=%d" % mkcid
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            player = await resp.json()
            return player

async def getPlayerFromFC(fc, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player?'
    request_text = "fc=%s" % fc
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            player = await resp.json()
            return player

async def getPlayerFromDiscord(discordid, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player?'
    request_text = f"discordId={discordid}"
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            player = await resp.json()
            return player


async def getPlayerInfo(name, season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player/details?'
    request_text = "name=%s" % name
    request_url = base_url + request_text + '&season=%s' % season
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            playerData = await resp.json()
            return playerData


async def getTable(tableID):
    base_url = creds['website_url'] + '/api/table?'
    request_text = "tableId=%d" % tableID
    request_url = base_url + request_text
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return False
            table = await resp.json()
            return table

async def getLeaderboard(season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player/leaderboard?'
    request_text = "season=%s&pageSize=10" % season
    request_url = base_url + request_text
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            Leaderboard = await resp.json()
            return Leaderboard

async def getAllplayer(season=''):
    if season == '':
        season = config['season']
    base_url = creds['website_url'] + '/api/player/list'
    request_text = "?season=%s" % season
    request_url = base_url + request_text
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds["username"], creds["password"])) as session:
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return False
            players = await resp.json()
            return players