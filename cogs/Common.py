import discord
from discord.ext import commands
import json
import statistics
from typing import Optional

import API.get
from constants import getRank, getRankdata
import plotting

with open('config.json', 'r') as cjson:
    config = json.load(cjson)

with open('credentials.json', 'r') as cjson:
    site_creds = json.load(cjson)
    
def channel_id(tier):
        channels = {"X": 698153967820996639,
                    "S": 445716741830737920,
                    "A": 445570804915109889,
                    "AB": 817605040105717830,
                    "B": 445570790151421972,
                    "BC": 874395278520774678,
                    "C": 445570768269475840,
                    "CD": 874395385525854318,
                    "D": 445570755657465856,
                    "DE": 874395482045153322,
                    "E": 445716908923420682,
                    "EF": 874395541482647592,
                    "F": 796870494405394472,
                    "SQ": 741906846209671223}
        channel_id = channels[tier.upper()]
        return channel_id

def my_round(val, digit=0):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p

def average(mmr_sum, mmr_len):
    try:
        avg = mmr_sum / mmr_len
        avg = my_round(avg, 1)
        return avg
    except ZeroDivisionError:
        return False

async def check_perms(ctx: commands.Context):
    try:
        if ctx.guild.id == config['server'] and ctx.channel.category_id in config['tiers_category'] and ctx.channel.id not in config['ignore_channel']:
            return False
        else:
            return True
    except:
        return True

async def check_name(name, id, display_name, season: Optional[int] = config['season']):
    if name == None:
        player = await API.get.getPlayerFromDiscord(id, season)
        if player == None:
            player = await API.get.getPlayer(display_name, season)

    elif name.isdecimal() == True:
        if len(name) == 17 or len(name) == 18 or len(name) == 19:
            player = await API.get.getPlayerFromDiscord(name, season)
        else:
            player = await API.get.getPlayerFromMKC(int(name), season)
    elif name.replace("-", "").isdecimal() == True:
        player = await API.get.getPlayerFromFC(name, season)
    else:
        player = await API.get.getPlayer(name, season)

    return player

async def check_playerDetails(name, id, display_name, season: Optional[int] = config['season']):
    if name == None:
        player = await API.get.getPlayerFromDiscord(id, season)
        if player == None:
            player = await API.get.getPlayer(display_name, season)

    elif name.isdecimal() == True:
        if len(name) == 17 or len(name) == 18 or len(name) == 19:
            player = await API.get.getPlayerFromDiscord(name, season)
        else:
            player = await API.get.getPlayerFromMKC(int(name), season)
    elif name.replace("-", "").isdecimal() == True:
        player = await API.get.getPlayerFromFC(name, season)
    else:
        player = await API.get.getPlayer(name, season)
    
    if player != None:
        playerDetails = await API.get.getPlayerInfo(player['name'], season)
    else:
        playerDetails = None

    return playerDetails

async def get_tier(tiers):
    tier_list = []
    if tiers == None or tiers.upper() == "ALL":
        tier_list = ["Master", "X", "S", "A", "AB", "B", "BC", "C", "CD", "D", "DE", "E", "EF", "F", "SQ"]
        set_tier = "ALL"
    elif tiers.upper() == "TIERS":
        tier_list = ["Master", "X", "S", "A", "AB", "B", "BC", "C", "CD", "D", "DE", "E", "EF", "F"]
        set_tier = "Tiers"
    else: 
        for tier in tiers.split(','):
            tier_list.append(tier.upper())
            set_tier = ','.join(tier_list)
    
    return tier_list, set_tier

async def get_format(formats):
    format_list = []
    if formats == None:
        format_list = [1, 2, 3, 4, 6]
    else:
        for i in str(formats).split(','):
            format_list.append(int(i))

    return format_list

async def check_flm(first, last, mid):
    input_check = 0

    if first != None:
        if int(first) <= 0:
            return False
        input_check += 1

    if mid != None:
        mid = mid.split('-')
        try:
            start_num = mid[0]
            end_num = mid[1]
            if int(start_num) >= int(end_num):
                return None
        except IndexError or ValueError:
            return None
        try:
            if int(start_num) <= 0 or int(end_num) <= 0:
                return None
        except ValueError:
            return None
        input_check += 1

    if last != None:
        if int(last) <= 0:
            return False
        input_check += 1

    return input_check

async def manage_playerdetails(
    ctx: commands.Context,
    season: str, 
    name,
    tiers: Optional[str] = None,
    formats: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
    mid: Optional[str] = None,
    partner_name: Optional[str] = None
) -> dict or bool:
    if ctx.interaction == None and await check_perms(ctx) == False:
        await ctx.send('You cannot use this command in this channel.', ephemeral=True)
        return False, False
    name = await check_name(name, ctx.author.id, ctx.author.display_name)
    if name is None:
        await ctx.send("This id can't be found on the site!")
        return False, False

    title = "S%d" % int(season)

    if first != None or last != None or mid != None: 
        flm = await check_flm(first, last, mid)
        if flm == False:
            await ctx.send("Input error, number needs to be positive.")
            return False, False
        if flm == None:
            await ctx.send("Input error. Check your input. `ex: 10-20`")
            return False, False
        elif flm >= 2:
            await ctx.send("Input error, you can't use [last, mid, first] command at the same time.")
            return False, False

    playerDetails = await API.get.getPlayerInfo(name['name'], season)
    if playerDetails is None:
        await ctx.send("Player not found!")
        return False, False

    if 'overallRank' in playerDetails.keys():
        rank = playerDetails['overallRank']
    else:
        rank = "Null"

    mmrHistory = []
    scores = []
    deltas = []
    changeId = []
    partnerscores = []
    deleted_tables_id = []

    matches = playerDetails['mmrChanges'][::-1]
    events = []
    for match in matches:
        if match['reason'] == "TableDelete":
            deleted_tables_id.append(match['changeId'])
    for match in matches:
        if match['reason'] == "Placement":
            events.append(match)
        if match['reason'] == "Table":
            if match['changeId'] in deleted_tables_id:
                pass
            else:
                events.append(match)

    if first != None:
        events = events[:int(first) + 1]
        rank = "null"
        if tiers == None and formats == None and partner_name == None:
            title += " | First %d Matches" % int(first)
        else:
            title += " | In the First %d Matches" % int(first)
    elif last != None:
        if last >= playerDetails['eventsPlayed']:
            last = playerDetails['eventsPlayed']
        events = events[-last:]
        try:
            mmrHistory.append(matches[-(last+1)]['newMmr'])
        except IndexError:
            await ctx.send('error')
            return False, False
        if tiers == None and formats == None and partner_name == None:
            title += " | Last %d Matches" % int(last)
        else:
            title += " | In the Last %d Matches" % int(last)
    elif mid != None:
        mid = mid.split('-')
        start_num = mid[0]
        end_num = mid[1]
        events = events[int(start_num)-1:int(end_num)+1]
        rank = "null"
        if tiers == None and formats == None and partner_name == None:
            title += f" | Mid {mid} Matches"
        else:
            title += f" | During Mid {mid} Matches"

    tier_list, set_tier = await get_tier(tiers)
    if tiers != None:
        title += f' | Tier: {(set_tier)}'
    format_list = await get_format(formats)
    if formats != None:
        title += f" | Format: {','.join(map(str, format_list))}"
    if partner_name != None:
        partner_idlist = []
        P_playerDetails = await check_playerDetails(partner_name, None, None)
        if P_playerDetails is None:
            await ctx.send("Partner name couldn't be found!")
            return False, False

        title += f" | with {P_playerDetails['name']}"
        partner_id = P_playerDetails['playerId']
        partner_idlist.append(int(partner_id))

        events1 =events
        events = []   
        for match in events1:
            if match['reason'] == "Placement":
                events.append(match)
            if match['reason'] == "Table":
                for p_id in match['partnerIds']:
                    if int(p_id) in partner_idlist:
                        events.append(match)
                    else:
                        pass
    
    check_mid = 0
    for match in events:
        if mid != None and check_mid == 0:
            graph_basemmr = match['newMmr']
            check_mid += 1
            continue
        if match['reason'] == 'Placement':
            mmrHistory.append(match['newMmr'])
            basemmr = match['newMmr']
        if match['reason'] == 'Table' and match['tier'] in tier_list and int(12/match['numTeams']) in format_list:
            for partner in match['partnerScores']:
                partnerscores.append(partner)
            deltas.append(match['mmrDelta'])
            mmrHistory.append(match['newMmr'])
            changeId.append(match['changeId'])
            scores.append(match['score'])
    
    if len(scores) == 0:
        await ctx.send("You must play at least 1 match to see your stats")
        return False, False

    peakMMR = "N/A"
    
    if tiers==None and formats==None and partner_name==None and first==None and last==None and mid==None:
        title += ' Stats'
        if 'maxMmr' in playerDetails.keys():
            peakMMR = playerDetails['maxMmr']
    elif tiers==None and formats==None and partner_name==None:
        peakMMR = max(mmrHistory)
    else:
        peakMMR = 'N/A'

    playerURL = site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
    playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

    if first != None or mid != None:
        mmr = mmrHistory[-1]
    else:
        mmr = playerDetails['mmr']
    mmrRank = getRank(mmr, season)
    ranks = getRankdata(season)
    rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
    rankURL = ranks[mmrRank]["url"]

    # if mmrHistory[-1] != mmr:
    #     mmrHistory.append(mmr)

    if max(deltas) <= 0:
        largestGain = "-"
    else:
        tableURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(max(deltas))]
        largestGain = "[%s](%s)" % (max(deltas), tableURL)

    if min(deltas) >= 0:
        largestLoss = "-"
    else:
        tableURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(min(deltas))]
        largestLoss = "[%s](%s)" % (min(deltas), tableURL)

    wins = len([x for x in (deltas) if x >= 0])
    loses = len([x for x in (deltas) if x < 0])
    gainLoss = sum(deltas)

    if mid != None:
        mmrHistory.insert(0, graph_basemmr)
    img = await plotting.create_plot(mmrHistory, int(season))
    f = discord.File(fp=img, filename='stats.png')

    e = discord.Embed(title=title, description=playerNameAndURL, colour=rankColor)
    if tiers == None and formats == None and partner_name == None:
        e.add_field(name="Rank", value=rank)
        e.add_field(name="MMR", value=mmr)
        e.add_field(name="Peak MMR", value=peakMMR)
    winRate = str(round(len([n for n in deltas if n >= 0]) / len(deltas) * 100, 1))
    e.add_field(name="Win Rate", value=winRate)
    e.add_field(name="W-L", value="%s - %s" % (wins, loses))
    e.add_field(name="+/-", value=gainLoss)
    aveScore = str(round(sum(scores) / len(scores), 1))
    e.add_field(name="Avg. Score", value=aveScore)
    scoreURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[scores.index(max(scores))]
    Top_score = "[%s](%s)" % (max(scores), scoreURL)
    e.add_field(name="Top Score", value=Top_score)
    try:
        partner_ave = sum(partnerscores) / len(partnerscores)
        partner_ave = str(round(partner_ave, 1))
    except ZeroDivisionError:
        partner_ave = "-"
    if partner_name == None:
        e.add_field(name="Partner Avg.", value=partner_ave)
    if first==None and last==None and mid==None:
        e.add_field(name="Events Played", value=str(len(scores)))
    e.add_field(name="Largest Gain", value=largestGain)
    e.add_field(name="Largest Loss", value=largestLoss)
    if tiers==None and formats==None and partner_name==None:
        ave_mmr = average(sum(mmrHistory), len(mmrHistory))
        e.add_field(name="Average MMR", value=ave_mmr)
        if  first==None and last==None and mid==None:
            e.add_field(name="Base MMR", value=basemmr)
    e.set_thumbnail(url=rankURL)
    e.set_image(url="attachment://stats.png")
    if tiers==None and formats==None and partner_name==None:
        return e, f
    else:
        return e, None
    
async def manage_playerdetails_last(
    ctx: commands.Context,
    season: str, 
    name,
    tiers: Optional[str] = None,
    formats: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
    partner_name: Optional[str] = None
):
    if ctx.interaction == None and await check_perms(ctx) == False:
        await ctx.send('You cannot use this command in this channel.', ephemeral=True)
        return False, False
    name = await check_name(name, ctx.author.id, ctx.author.display_name)
    if name is None:
        await ctx.send("This id can't be found on the site!")
        return False, False

    title = "S%d" % int(season)

    if first != None or last != None: 
        flm = await check_flm(first, last, None)
        if flm == False:
            await ctx.send("Input error, number needs to be positive.")
            return False, False
        if flm == None:
            await ctx.send("Input error. Check your input. `ex: 10-20`")
            return False, False
        elif flm >= 2:
            await ctx.send("Input error, you can't use [last, mid, first] command at the same time.")
            return False, False

    playerDetails = await API.get.getPlayerInfo(name['name'], season)
    if playerDetails is None:
        await ctx.send("Player not found!")
        return False, False

    if 'overallRank' in playerDetails.keys():
        rank = playerDetails['overallRank']
    else:
        rank = "Null"

    mmrHistory = []
    scores = []
    deltas = []
    changeId = []
    partnerscores = []
    deleted_tables_id = []

    matches = playerDetails['mmrChanges'][::-1]
    events = []
    for match in matches:
        if match['reason'] == "TableDelete":
            deleted_tables_id.append(match['changeId'])
    for match in matches:
        if match['reason'] == "Placement":
            events.append(match)
        if match['reason'] == "Table":
            if match['changeId'] in deleted_tables_id:
                pass
            else:
                events.append(match)

    if first != None:
        rank = "null"
        title += " | First %d Matches" % int(first)
        check_num = first
    elif last != None:
        if last >= playerDetails['eventsPlayed']:
            last = playerDetails['eventsPlayed']
        title += " | Last %d Matches" % int(last)
        check_num = last

    tier_list, set_tier = await get_tier(tiers)
    if tiers != None:
        title += f' | Tier: {(set_tier)}'
    format_list = await get_format(formats)
    if formats != None:
        title += f" | Format: {','.join(map(str, format_list))}"
    if partner_name != None:
        partner_idlist = []
        P_playerDetails = await check_playerDetails(partner_name, None, None)
        if P_playerDetails is None:
            await ctx.send("Partner name couldn't be found!")
            return False, False

        title += f" | with {P_playerDetails['name']}"
        partner_id = P_playerDetails['playerId']
        partner_idlist.append(int(partner_id))

        events1 =events
        events = []   
        for match in events1:
            if match['reason'] == "Placement":
                events.append(match)
            if match['reason'] == "Table":
                for p_id in match['partnerIds']:
                    if int(p_id) in partner_idlist:
                        events.append(match)
                    else:
                        pass

    count_check = 0
    if last != None:
        events = reversed(events)
    for match in events:
        if match['reason'] == 'Placement':
            mmrHistory.append(match['newMmr'])
            basemmr = match['newMmr']
        if match['reason'] == 'Table' and match['tier'] in tier_list and int(12/match['numTeams']) in format_list:
            count_check += 1
            if count_check == check_num + 1:
                if last != None:
                    mmrHistory.append(match['newMmr'])
                break
            for partner in match['partnerScores']:
                partnerscores.append(partner)
            deltas.append(match['mmrDelta'])
            mmrHistory.append(match['newMmr'])
            changeId.append(match['changeId'])
            scores.append(match['score'])

    if last != None:
        mmrHistory.reverse()
    
    if len(scores) == 0:
        await ctx.send("You must play at least 1 match to see your stats")
        return False, False
    
    peakMMR = "N/A"
    if tiers==None and formats==None and partner_name==None and first==None and last==None and 'maxMmr' in playerDetails.keys():
        peakMMR = playerDetails['maxMmr']
    elif tiers==None and formats==None and partner_name==None:
        peakMMR = max(mmrHistory)
    else:
        peakMMR = 'N/A'

    playerURL = site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
    playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

    if first != None:
        mmr = mmrHistory[-1]
    else:
        mmr = playerDetails['mmr']
    mmrRank = getRank(mmr, season)
    ranks = getRankdata(season)
    rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
    rankURL = ranks[mmrRank]["url"]

    # if mmrHistory[-1] != mmr:
    #     mmrHistory.append(mmr)

    if max(deltas) <= 0:
        largestGain = "-"
    else:
        tableURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(max(deltas))]
        largestGain = "[%s](%s)" % (max(deltas), tableURL)

    if min(deltas) >= 0:
        largestLoss = "-"
    else:
        tableURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(min(deltas))]
        largestLoss = "[%s](%s)" % (min(deltas), tableURL)

    wins = len([x for x in (deltas) if x > 0])
    loses = len([x for x in (deltas) if x < 0])
    gainLoss = sum(deltas)

    img = await plotting.create_plot(mmrHistory, int(season))
    f = discord.File(fp=img, filename='stats.png')

    e = discord.Embed(title=title, description=playerNameAndURL, colour=rankColor)
    if tiers == None and formats == None and partner_name == None:
        e.add_field(name="Rank", value=rank)
        e.add_field(name="MMR", value=mmr)
        e.add_field(name="Peak MMR", value=peakMMR)
    winRate = str(round(len([n for n in deltas if n > 0]) / len(deltas) * 100, 1))
    e.add_field(name="Win Rate", value=winRate)
    e.add_field(name="W-L", value="%s - %s" % (wins, loses))
    e.add_field(name="+/-", value=gainLoss)
    aveScore = str(round(sum(scores) / len(scores), 1))
    e.add_field(name="Avg. Score", value=aveScore)
    scoreURL = site_creds['website_url'] + "/TableDetails/%d" % changeId[scores.index(max(scores))]
    Top_score = "[%s](%s)" % (max(scores), scoreURL)
    e.add_field(name="Top Score", value=Top_score)
    try:
        partner_ave = sum(partnerscores) / len(partnerscores)
        partner_ave = str(round(partner_ave, 1))
    except ZeroDivisionError:
        partner_ave = "-"
    if partner_name == None:
        e.add_field(name="Partner Avg.", value=partner_ave)
    if first==None and last==None:
        e.add_field(name="Events Played", value=str(len(scores)))
    e.add_field(name="Largest Gain", value=largestGain)
    e.add_field(name="Largest Loss", value=largestLoss)
    if tiers==None and formats==None and partner_name==None:
        ave_mmr = average(sum(mmrHistory), len(mmrHistory))
        e.add_field(name="Average MMR", value=ave_mmr)
        if  first==None and last==None:
            e.add_field(name="Base MMR", value=basemmr)
    e.set_thumbnail(url=rankURL)
    e.set_image(url="attachment://stats.png")
    if tiers==None and formats==None and partner_name==None:
        return e, f
    else:
        return e, None

async def get_player_averagemmr(playerDetails):
    mmrHistory = []
    deleted_tables_id = []

    matches = playerDetails['mmrChanges'][::-1]
    events = []
    for match in matches:
        if match['reason'] == "TableDelete":
            deleted_tables_id.append(match['changeId'])
    for match in matches:
        if match['reason'] == "Placement":
            events.append(match)
        if match['reason'] == "Table":
            if match['changeId'] in deleted_tables_id:
                pass
            else:
                events.append(match)

    for match in events:
        if match['reason'] == 'Placement':
                mmrHistory.append(match['newMmr'])
        if match['reason'] == 'Table':
            mmrHistory.append(match['newMmr'])

    ave_mmr = average(sum(mmrHistory), len(mmrHistory))
    return ave_mmr

async def get_player_scores(ctx: commands.Context, playerDetails, tiers, formats, first: Optional[int], mid: Optional[str], last: Optional[int], partner_name: Optional[str]):
    scores = []
    deleted_tables_id = []
    title = ''

    if first != None or last != None or mid != None: 
        flm = await check_flm(first, last, mid)
        if flm == False:
            await ctx.send("Input error, number needs to be positive.")
            return None, False, False, False, False, False
        if flm == None:
            await ctx.send("Input error. Check your input. `ex: 10-20`")
            return None, False, False, False, False, False
        elif flm >= 2:
            await ctx.send("Input error, you can't use [last, mid, first] command at the same time.")
            return None, False, False, False, False, False

    tier_list, set_tier = await get_tier(tiers)
    if tiers != None:
        title += f' | Tier: {(set_tier)}'
    format_list = await get_format(formats)
    if formats != None:
        title += f" | Format: {','.join(map(str, format_list))}"

    matches = playerDetails['mmrChanges'][::-1]
    events = []
    for match in matches:
        if match['reason'] == "TableDelete":
            deleted_tables_id.append(match['changeId'])
    for match in matches:
        if match['reason'] == "Placement":
            events.append(match)
        if match['reason'] == "Table":
            if match['changeId'] in deleted_tables_id:
                pass
            else:
                events.append(match)

    if first != None:
        events = events[:int(first) + 1]
        rank = "null"
        if tiers == None and formats == None and partner_name == None:
            title += " | First %d Matches" % int(first)
        else:
            title += " | In the First %d Matches" % int(first)
    elif last != None:
        if last >= playerDetails['eventsPlayed']:
            last = playerDetails['eventsPlayed']
        events = events[-last:]
        if tiers == None and formats == None and partner_name == None:
            title += " | Last %d Matches" % int(last)
        else:
            title += " | In the Last %d Matches" % int(last)
    elif mid != None:
        mid = mid.split('-')
        start_num = mid[0]
        end_num = mid[1]
        events = events[int(start_num)-1:int(end_num)+1]
        if tiers == None and formats == None and partner_name == None:
            title += f" | Mid {mid} Matches"
        else:
            title += f" | During Mid {mid} Matches"

    tier_list, set_tier = await get_tier(tiers)
    if tiers != None:
        title += f' | Tier: {(set_tier)}'
    format_list = await get_format(formats)
    if formats != None:
        title += f" | Format: {','.join(map(str, format_list))}"
    if partner_name != None:
        partner_idlist = []
        P_playerDetails = await check_playerDetails(partner_name, None, None)
        if P_playerDetails is None:
            await ctx.send("Partner name couldn't be found!")
            return None, False, False, False, False, False
        title += f" | with {P_playerDetails['name']}"
        partner_id = P_playerDetails['playerId']
        partner_idlist.append(int(partner_id))

        events1 =events
        events = []   
        for match in events1:
            if match['reason'] == "Placement":
                events.append(match)
            if match['reason'] == "Table":
                for p_id in match['partnerIds']:
                    if int(p_id) in partner_idlist:
                        events.append(match)
                    else:
                        pass

    for match in events:
        if match['reason'] == 'Table' and match['tier'] in tier_list and int(12/match['numTeams']) in format_list:
            scores.append(match['score'])

    ave_score = average(sum(scores), len(scores))
    if len(scores) == 0:
        return False, False, False, False, False, False
    max_score = max(scores)
    median = statistics.median(scores)
    stdev = statistics.pstdev(scores)
    return ave_score, max_score, scores, title, median, stdev

    
