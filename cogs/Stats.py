import discord
from discord.ext import commands
from discord import app_commands

import collections
import datetime
import json
import time
import statistics
from typing import Optional
import pandas as pd

import API.get
import cogs.Common as Common
import cogs.Prev_Stats as Prev_Stats
from constants import getRank, getRankdata
import plotting
import calc

with open('config.json', 'r') as cjson:
    config = json.load(cjson)

with open('timezones.json', 'r') as cjson:
    timezones = json.load(cjson)


class Stats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.site_creds = bot.site_creds
        self.ctx_menu = app_commands.ContextMenu(
            name='Make table',
            callback=self.context_menu_maketable,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def context_menu_maketable(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.defer()
        lineup = message.content
        lineup = lineup[lineup.find("!scoreboard"):]
        index = lineup.find("Decide")
        if index != -1:
            lineup = lineup[:lineup.find("Decide")]
            lineup = lineup[:-2]
        lineup = lineup[14:]
        members = lineup.replace("`", "").replace(", ", ",").split(",")

        m_content = "!submit size tier\n"

        for i in range(len(members)):
            name = members[i]
            score = 0

            m_content += f'{name} {score}\n'

        await interaction.followup.send(m_content)

    def is_allowed_server():
        def predicate(ctx):
            try:
                if ctx.guild.id not in config['ignore_server']:
                    return True
            except AttributeError:
                return True
        return commands.check(predicate)

    @is_allowed_server()
    @commands.hybrid_command()
    async def stats(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 1, config['season']]] = config['season'],
        *,
        name: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
        mid: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        partner_name: Optional[str] = None,
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        if season <= config['web_season']:
            await Prev_Stats.Previous.stats(self, ctx, name, season)
            return
        e, f = await Common.manage_playerdetails(ctx, season, name, tiers, formats, first, last, mid, partner_name)
        if e == False:
            return

        if f != None:
            await ctx.send(embed=e, file=f, ephemeral=True)
        else:
            await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def mmr(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 1, config['season']]] = config['season'],
        *,
        name: Optional[str] = None 
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        if season < config['web_season']:
            await Prev_Stats.Previous.mmr(self, ctx, name, season)
            return
        if name != None:
            names = name.split(',')

        if name == None or len(names) == 1:
            player = await Common.check_name(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:
                await ctx.send("This player can't be found on the site!")
                return
            if 'mmr' not in player.keys():
                await ctx.send("This player has not been given a placement MMR yet!")
                return

            mmrRank = getRank(player['mmr'], season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            playerURL = self.bot.site_creds['website_url'] + '/PlayerDetails/%d' % player['id']

            e = discord.Embed(title="S%d MMR" % season, url=playerURL, colour=rankColor)
            e.add_field(name=player['name'], value=player['mmr'])

        else:
            e = discord.Embed(title="S%d MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                player = await Common.check_name(name, ctx.author.id, ctx.author.display_name, season=season)

                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    if 'mmr' in player.keys():
                        mmr = player['mmr']
                        MMR_list.append(int(player['mmr']))
                    else:
                        mmr = "Placement"
                    e.add_field(name=player['name'], value=mmr, inline=True)

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                e.add_field(name="**MMR Avg.**", value='Null', inline=False)
            else:
                e.add_field(name="**MMR Avg.**", value="%.1f" % average, inline=False)
        
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def averagemmr(
        self,
        ctx: commands.Context,
        season: Optional[int] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        if name != None:
            names = name.split(',')
        if name == None or len(names) == 1:
            player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:
                await ctx.send("This player can't be found on the site!")
                return
            if 'mmr' not in player.keys():
                await ctx.send("This player has not been given a placement MMR yet!")
                return

            average_mmr = await Common.get_player_averagemmr(player)

            mmrRank = getRank(average_mmr, season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            playerURL = self.bot.site_creds['website_url'] + '/PlayerDetails/%d' % player['playerId']

            e = discord.Embed(title="S%d Average MMR" % season, url=playerURL, colour=rankColor)
            e.add_field(name=player['name'], value=average_mmr)

        else:
            e = discord.Embed(title="S%d Average MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)

                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    average_mmr = await Common.get_player_averagemmr(player)
                    if average_mmr == False:
                        e.add_field(name=player['name'], value='Null', inline=True)
                    else:
                        e.add_field(name=player['name'], value=average_mmr, inline=True)
                        MMR_list.append(average_mmr)

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                e.add_field(name="**Average MMR Avg.**", value='Null', inline=False)
            else:
                e.add_field(name="**Average MMR Avg.**", value="%.1f" % average, inline=False)
        
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def peak(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 1, config['season']]] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        if season < config['web_season']:
            await Prev_Stats.Previous.peak(self, ctx, name, season)
            return
        if name != None:
            names = name.split(',')

        if name == None or len(names) == 1:
            player = await Common.check_name(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:
                await ctx.send("This player can't be found on the site!")
                return
            if 'maxMmr' not in player.keys():
                await ctx.send("This player doesn't have Peak MMR.")
                return

            mmrRank = getRank(player['maxMmr'], season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % player['id']

            e = discord.Embed(title="S%d Peak MMR" % season, url=playerURL, colour=rankColor)
            e.add_field(name=player['name'], value=player['maxMmr'])

        else:
            e = discord.Embed(title="S%d Peak MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                player = await Common.check_playerDetails(name, name, ctx.author.display_name, season=season)

                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    if 'maxMmr' in player.keys():
                        maxMmr = player['maxMmr']
                        MMR_list.append(int(player['maxMmr']))
                    else:
                        maxMmr = "Null"
                    e.add_field(name=player['name'], value=maxMmr, inline=True)

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                e.add_field(name="**Peak MMR Avg.**", value="Null", inline=False)
            else:
                e.add_field(name="**Peak MMR Avg.**", value="%.1f" % average, inline=False)
            
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def rank(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        if name != None:
            names = name.split(',')

        if name == None or len(names) == 1:
            player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:
                await ctx.send("This player can't be found on the site!")
                return
            if player['eventsPlayed'] == 0:
                await ctx.send("You need to play at least 1 events to check your rank.")
                return

            mmrRank = getRank(player['mmr'], season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % player['playerId']

            e = discord.Embed(title="S%d Rank" % season, url=playerURL, colour=rankColor)
            e.add_field(name=player['name'], value=player['overallRank'])

        else:
            e = discord.Embed(title="S%d Peak MMR" % season)
            for name in names:
                name = name.strip()
                player = await Common.check_name(name, name, ctx.author.display_name, season=season)

                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    if player['eventsPlayed'] != 0:
                        rank = player['overallRank']
                    else:
                        rank = "Null"
                    e.add_field(name=player['name'], value=rank, inline=True)
            
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    @app_commands.choices(show_sma = [
        app_commands.Choice(name='Yes', value="Yes"),
        app_commands.Choice(name='No', value="No")])
    @app_commands.choices(show_scores = [
        app_commands.Choice(name='Yes', value="Yes"),
        app_commands.Choice(name='No', value="No")])
    async def scores(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        first: Optional[int] = None,
        mid: Optional[str] = None,
        last: Optional[int] = None,
        partner_name: Optional[str] = None,
        show_scores: Optional[str] = "Yes",
        show_sma: Optional[str] = "No",
        num_sma: Optional[int] = 3
    ):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if player is None:
            await ctx.send("This player can't be found on the site!")
            return
        if player['eventsPlayed'] == 0:
            await ctx.send("You need to play at least 1 events to check your scores.")
            return

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % player['playerId']
        playerNameAndURL = "[%s](%s)" % (player['name'], playerURL)
        ave_score, max_score, scores, title, median, stdev = await Common.get_player_scores(ctx, player, tiers, formats, first, mid, last, partner_name)
        if ave_score == False:
            await ctx.send("You need to play at least 1 events to check your scores.")
            return
        if ave_score == None:
            return

        img = await plotting.create_score_plot(scores, ave_score, show_scores, show_sma, num_sma)
        f = discord.File(fp=img, filename='scores.png')

        e = discord.Embed(title=f"S{season} Scores" + str(title), description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Average Score", value=ave_score)
        e.add_field(name="Top Score", value=max_score)
        e.add_field(name="Median Score", value=median, inline=False)
        e.add_field(name="Standard Deviation", value="%.1f" % stdev, inline=True)

        e.set_image(url="attachment://scores.png")
        await ctx.send(embed=e, file=f, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='ts')
    async def tierstats(
        self,
        ctx: commands.Context,
        tiers: Optional[str] = 'ALL',
        *,
        name: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        e, f = await Common.manage_playerdetails(ctx, season, name, tiers=tiers)
        if e == False:
            return
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='fs')
    async def formatstats(
        self,
        ctx: commands.Context,
        formats: str,
        *,
        name: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        e, f = await Common.manage_playerdetails(ctx, season, name, formats=formats)
        if e == False:
            return
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def events(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        if name != None:
            names = name.split(',')

        if name == None or len(names) == 1:
            player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:    
                await ctx.send("This player can't be found on the site!")
                return
            if 'eventsPlayed' not in player.keys():
                eventsPlayed = 0
            else:
                eventsPlayed = player['eventsPlayed']

            playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % player['playerId']

            e = discord.Embed(title="S%d Events Played" % season, url=playerURL, colour=0x0eff0a)
            e.add_field(name=player['name'], value=eventsPlayed)

        else:
            e = discord.Embed(title="S%d Events Played" % season, colour=0x0eff0a)
            for name in names:
                name = name.strip()
                player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    if 'eventsPlayed' in player.keys():
                        eventsPlayed = player['eventsPlayed']
                    else:
                        eventsPlayed = 0
                    e.add_field(name=player['name'], value=eventsPlayed, inline=True)

        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='dd')
    async def daily(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None,
        timezone: Optional[str] = 'utc'
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("This player can't be found on the site!")
            return

        dates = []
        deleted_tables_id = []

        if timezone.upper() in timezones.keys():
            timezone_hours = timezones[timezone.upper()]
            timezone = timezone.upper()
        else:
            timezone_hours = 0
            timezone = 'UTC'
                    
        set_timezone = datetime.timezone(datetime.timedelta(hours=timezone_hours))
        start_time = datetime.datetime.now(set_timezone) + datetime.timedelta(days=-14)

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
            if match['reason'] == 'Table':
                Mogi_time = str(match['time'][:19])
                dte = datetime.datetime.strptime(Mogi_time, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=timezone_hours)
                if start_time.replace(tzinfo=None).date() <= dte.date():
                    dates.append(dte.date())
                else:
                    pass

        m_content = ""
        total = 0
        month = collections.Counter(dates)
        for m, n in month.items():
            m = time.mktime(datetime.datetime.strptime(str(m), "%Y-%m-%d").timetuple())
            m_content += f"<t:{int(m)}:d>" + " : %d\n" % int(n)
            total += int(n)

        if len(m_content) == 0:
            await ctx.send('There are no events played in the last 2 weeks.')
            return

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
        playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

        e = discord.Embed(title="Daily Data", description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Events Played: %d" % total, value=m_content)
        e.set_footer(text="Timezone: %s" % str(timezone))
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='wd')
    async def weekly(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None,
        timezone: Optional[str] = 'utc'
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("This player can't be found on the site!")
            return

        deleted_tables_id = []

        if timezone.upper() in timezones.keys():
            timezone_hours = timezones[timezone.upper()]
            timezone = timezone
        else:
            timezone_hours = 0  
            timezone = 'UTC'

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
        dates = []
        for match in events:
            if match['reason'] == 'Table':
                Mogi_time = str(match['time'][:19])
                dte = datetime.datetime.strptime(Mogi_time, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=timezone_hours)
                dates.append(dte.date())

        if len(dates) == 0:
            await ctx.send("You must play at least 1 match to see your weekly data.")
            return

        df = pd.DataFrame({'date': dates})
        df["date"] = pd.to_datetime(df["date"])
        dates = df["date"].dt.to_period("W")

        m_content = "```"
        total = 0
        month = collections.Counter(dates)
        for m, n in month.items():
            m_content += str(m) + ": %d\n" % int(n)
            total += int(n)

        m_content += '```'

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
        playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

        e = discord.Embed(title="S%d Weekly Data" % season, description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Events Played: %d" % total, value=m_content)
        e.set_footer(text="Timezone: %s" % str(timezone))
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='md')
    async def monthly(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None,
        timezone: Optional[str] = 'utc'
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("This player can't be found on the site!")
            return

        deleted_tables_id = []

        if timezone.upper() in timezones.keys():
            timezone_hours = timezones[timezone.upper()]
            timezone = timezone
        else:
            timezone_hours = 0  
            timezone = 'UTC'

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
        dates = []
        for match in events:
            if match['reason'] == 'Table':
                Mogi_time = str(match['time'][:19])
                Mogi_Month = datetime.datetime.strptime(Mogi_time, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=timezone_hours)
                dates.append(str(Mogi_Month)[:7])

        if len(dates) == 0:
            await ctx.send("You must play at least 1 match to see your monthly data.")
            return

        m_content = ""
        total = 0
        month = collections.Counter(dates)
        for m, n in month.items():
            m_content += str(m) + ": %d\n" % int(n)
            total += int(n)

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
        playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

        e = discord.Embed(title="S%d Monthly Data" % season, description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Events Played: %d" % total, value=m_content)
        e.set_footer(text="Timezone: %s" % str(timezone))
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='td')
    async def tierdata(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("This player can't be found on the site!")
            return

        tiers = []
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
            if match['reason'] == 'Table':
                tier = match['tier']
                tiers.append(tier)

        if len(tiers) == 0:
            await ctx.send("You must play at least 1 match to see your tierdata.")
            return

        tiers_order = config['tiers_list']
        tiers = sorted(tiers, key=tiers_order.index)

        m_content = ""
        total = 0
        tiers_data = collections.Counter(tiers)
        for m, n in tiers_data.items():
            m_content += m + ": %d\n" % int(n)
            total += int(n)

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
        playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

        e = discord.Embed(title="S%d Tier Data" % season, description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Events Played: %d" % total, value=m_content)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command(name='fd')
    async def formatdata(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("Player not found!")
            return

        formats = []
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
            if match['reason'] == 'Table':
                format_type = match['numTeams']
                formats.append(format_type)

        if len(formats) == 0:
            await ctx.send("You must play at least 1 match to see your tierdata.")
            return

        format_order = [12, 6, 4, 3, 2]

        formats = sorted(formats, key=format_order.index)

        m_content = ""
        total = 0
        tiers_data = collections.Counter(formats)
        for m, n in tiers_data.items():
            if m == 12:
                type = "FFA"
            else:
                f_num = 12 / m
                type = "%dv%d" % (f_num, f_num)
            m_content += type + ": %d\n" % int(n)
            total += int(n)

        playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']
        playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

        e = discord.Embed(title="S%d Format Data" % season, description=playerNameAndURL, colour=0x0eff0a)
        e.add_field(name="Events Played: %d" % total, value=m_content)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def base(
        self,
        ctx: commands.Context,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season'],
        *,
        name: Optional[str] = None
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        if name != None:
            names = name.split(',')

        if name == None or len(names) == 1:
            player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
            if player is None:
                await ctx.send("Player not found!")
                return

            events = player['mmrChanges'][::-1]
            for match in events:
                if match['reason'] == 'Placement':
                    base = match['newMmr']
                    break
            
            mmrRank = getRank(base, season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
            playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % player['playerId']

            e = discord.Embed(title="S%d Base MMR" % season, url=playerURL, colour=rankColor)
            e.add_field(name=player['name'], value=base)

        else:
            e = discord.Embed(title="S%d Base MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                player = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)

                if player is None:
                    e.add_field(name=name, value='name error', inline=True)
                else:
                    events = player['mmrChanges'][::-1]
                    for match in events:
                        if match['reason'] == 'Placement':
                            base = match['newMmr']
                            e.add_field(name=player['name'], value=base, inline=True)
                            MMR_list.append(int(match['newMmr']))
                            break

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                e.add_field(name="**Base MMR Avg.**", value='Null', inline=False)
            else:
                e.add_field(name="**Base MMR Avg.**", value="%.1f" % average, inline=False)

        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def lastmatch(
        self,
        ctx: commands.Context,
        last: Optional[commands.Range[int, 1]] = 1,
        *,
        name: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("Player not found!")
            return

        tier_list, set_tier = await Common.get_tier(tiers)
        format_list = await Common.get_format(formats)

        deleted_tables_id = []

        matches = playerDetails['mmrChanges'][::-1]
        events = []
        for match in matches:
            if match['reason'] == "TableDelete":
                deleted_tables_id.append(match['changeId'])
        for match in matches:
            if match['reason'] == 'Table' and match['tier'] in tier_list and int(12/match['numTeams']) in format_list:
                if match['changeId'] in deleted_tables_id:
                    pass
                else:
                    events.append(match)

        if len(events) == 0:
            await ctx.send("You must play at least 1 match to see your lastmatch.")
            return

        if last > playerDetails['eventsPlayed']:
            await ctx.send('Input error. Number needs to be Events played or fewer.')
            return

        if last > len(events):
            last = len(events)
        id = events[-last]['changeId']
        pageURL = self.site_creds['website_url'] + '/TableDetails/%d' % id
        TableDetails = await API.get.getTable(tableID=id)
        e = discord.Embed(title="Table ID: %d" % id, url=pageURL, colour=0x1da3dd)
        format = TableDetails['format']
        tier = TableDetails['tier']
        created = TableDetails['createdOn'][:19]
        created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        created = int(created.timestamp())
        if 'verifiedOn' not in TableDetails.keys():
            await ctx.send("This table hasn't updated yet")
            return
        verified = TableDetails['verifiedOn'][:19]
        verified = datetime.datetime.strptime(verified, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        verified = int(verified.timestamp())

        message_id = TableDetails['tableMessageId']
        id_link = "https://discord.com/channels/445404006177570829/%s/%s" % (
            Common.channel_id(tier=tier), message_id)
        id_and_link = "[%d](%s)" % (id, id_link)
        e.add_field(name="ID", value=id_and_link, inline=True)
        e.add_field(name="Format", value=format, inline=True)
        e.add_field(name="Tier", value=tier, inline=True)
        e.add_field(name="Created", value=f"<t:{created}:f>", inline=False)
        e.add_field(name="Verified", value=f"<t:{verified}:f>", inline=False)
        if 'deletedOn' in TableDetails.keys():
            deleted = TableDetails['deletedOn'][:19]
            deleted = datetime.datetime.strptime(deleted, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            deleted = int(deleted.timestamp())
            e.add_field(name='Deleted', value=f"<t:{deleted}:f>", inline=False)
        mmr_message = "```\n"
        names = []
        oldMMRs = []
        newMMRs = []
        deltas = []
        for team in TableDetails['teams']:
            for player in team['scores']:
                names.append(player['playerName'])
                oldMMRs.append(player['prevMmr'])
                newMMRs.append(player['newMmr'])
                deltas.append(player['delta'])
        len_names = max(map(len, names))
        len_oldMMRs = len(str(max(oldMMRs)))
        len_newMMRs = len(str(max(newMMRs)))
        len_deltas = len(str(max(deltas)))
        for i in range(12):
            mmr_message += "%s: %s --> %s (%s)\n" % (
                names[i].ljust(len_names), str(oldMMRs[i]).ljust(len_oldMMRs), str(newMMRs[i]).ljust(len_newMMRs),
                str(deltas[i]).rjust(len_deltas))
        mmr_message += "```"
        e.add_field(name="MMR Changes ", value=mmr_message, inline=True)
        e.set_image(url=self.site_creds['website_url'] + "/TableImage/%d.png" % id)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def lm(
        self,
        ctx: commands.Context,
        last: Optional[commands.Range[int, 1]] = 1,
        *,
        name: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        playerDetails = await Common.check_playerDetails(name, ctx.author.id, ctx.author.display_name, season=season)
        if playerDetails is None:
            await ctx.send("Player not found!")
            return

        tier_list, set_tier = await Common.get_tier(tiers)
        format_list = await Common.get_format(formats)

        deleted_tables_id = []

        matches = playerDetails['mmrChanges'][::-1]
        events = []
        for match in matches:
            if match['reason'] == "TableDelete":
                deleted_tables_id.append(match['changeId'])
        for match in matches:
            if match['reason'] == 'Table' and match['tier'] in tier_list and int(12/match['numTeams']) in format_list:
                if match['changeId'] in deleted_tables_id:
                    pass
                else:
                    events.append(match)

        if len(events) == 0:
            await ctx.send("You must play at least 1 match to see your lastmatch.")
            return

        if last > playerDetails['eventsPlayed']:
            await ctx.send('Input error. Number needs to be Events played or fewer.')
            return

        if last > len(events):
            last = len(events)
        id = events[-last]['changeId']
        pageURL = self.site_creds['website_url'] + '/TableDetails/%d' % id
        TableDetails = await API.get.getTable(tableID=id)
        e = discord.Embed(title="Table ID: %d" % id, url=pageURL, colour=0x1da3dd)
        format = TableDetails['format']
        tier = TableDetails['tier']
        created = TableDetails['createdOn'][:19]
        created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        created = int(created.timestamp())
        if 'verifiedOn' not in TableDetails.keys():
            await ctx.send("This table hasn't updated yet")
            return
        verified = TableDetails['verifiedOn'][:19]
        verified = datetime.datetime.strptime(verified, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        verified = int(verified.timestamp())

        message_id = TableDetails['tableMessageId']
        id_link = "https://discord.com/channels/445404006177570829/%s/%s" % (
            Common.channel_id(tier=tier), message_id)
        id_and_link = "[%d](%s)" % (id, id_link)
        e.add_field(name="ID", value=id_and_link, inline=True)
        e.add_field(name="Format", value=format, inline=True)
        e.add_field(name="Tier", value=tier, inline=True)
        e.add_field(name="Created", value=f"<t:{created}:f>", inline=False)
        e.add_field(name="Verified", value=f"<t:{verified}:f>", inline=False)
        if 'deletedOn' in TableDetails.keys():
            deleted = TableDetails['deletedOn'][:19]
            deleted = datetime.datetime.strptime(deleted, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            deleted = int(deleted.timestamp())
            e.add_field(name='Deleted', value=f"<t:{deleted}:f>", inline=False)
        mmr_message = "```\n"
        names = []
        oldMMRs = []
        newMMRs = []
        deltas = []
        for team in TableDetails['teams']:
            for player in team['scores']:
                names.append(player['playerName'])
                oldMMRs.append(player['prevMmr'])
                newMMRs.append(player['newMmr'])
                deltas.append(player['delta'])
        len_names = max(map(len, names))
        len_oldMMRs = len(str(max(oldMMRs)))
        len_newMMRs = len(str(max(newMMRs)))
        len_deltas = len(str(max(deltas)))
        for i in range(12):
            mmr_message += "%s: %s --> %s (%s)\n" % (
                names[i].ljust(len_names), str(oldMMRs[i]).ljust(len_oldMMRs), str(newMMRs[i]).ljust(len_newMMRs),
                str(deltas[i]).rjust(len_deltas))
        mmr_message += "```"
        e.add_field(name="MMR Changes ", value=mmr_message, inline=True)
        e.set_image(url=self.site_creds['website_url'] + "/TableImage/%d.png" % id)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def first(
        self,
        ctx: commands.Context,
        first: commands.Range[int, 1],
        *,
        name: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        partner_name: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        e, f = await Common.manage_playerdetails_last(ctx, season, name, first=first, tiers=tiers, formats=formats, partner_name=partner_name)
        if e == False:
            return
        if f != None:
            await ctx.send(embed=e, file=f, ephemeral=True)
        else:
            await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def last(
        self,
        ctx: commands.Context,
        last: commands.Range[int, 1],
        *,
        name: Optional[str] = None,
        tiers: Optional[str] = None,
        formats: Optional[str] = None,
        partner_name: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        e, f = await Common.manage_playerdetails_last(ctx, season, name, last=last, tiers=tiers, formats=formats, partner_name=partner_name)
        if e == False:
            return
        if f != None:
            await ctx.send(embed=e, file=f, ephemeral=True)
        else:
            await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def mid(
        self,
        ctx: commands.Context,
        mid: str,
        *,
        name: Optional[str] = None,
        season: Optional[commands.Range[int, 4, config['season']]] = config['season']
    ) -> None:
        if await Common.check_perms(ctx) == False:
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        e, f = await Common.manage_playerdetails(ctx, season, name, mid=mid)
        if e == False:
            return
        if f != None:
            await ctx.send(embed=e, file=f, ephemeral=True)
        else:
            await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def calc(self, ctx: commands.Context, *, id_or_data):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        if id_or_data.isdecimal() == True:
            table = await API.get.getTable(int(id_or_data))
            if table is False:
                await ctx.send("Table couldn't be found")
                return

            if 'updateMessageId' in table.keys():
                pageURL = self.site_creds['website_url'] + '/TableDetails/%d' % int(id_or_data)
                TableDetails = await API.get.getTable(tableID=int(id_or_data))
                e = discord.Embed(title="Table ID: %d" % int(id_or_data), url=pageURL, colour=0x1da3dd)
                format = TableDetails['format']
                tier = TableDetails['tier']
                created = TableDetails['createdOn'][:19]
                created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
                created = int(created.timestamp())
                if 'verifiedOn' not in TableDetails.keys():
                    await ctx.send("This table hasn't updated yet")
                    return
                verified = TableDetails['verifiedOn'][:19]
                verified = datetime.datetime.strptime(verified, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
                verified = int(verified.timestamp())
                message_id = TableDetails['tableMessageId']
                id_link = "https://discord.com/channels/445404006177570829/%s/%s" % (
                    Common.channel_id(tier=tier), message_id)
                id_and_link = "[%d](%s)" % (int(id_or_data), id_link)
                e.add_field(name="ID", value=id_and_link, inline=True)
                e.add_field(name="Format", value=format, inline=True)
                e.add_field(name="Tier", value=tier, inline=True)
                e.add_field(name="Created", value=f"<t:{created}:f>", inline=False)
                e.add_field(name="Verified", value=f"<t:{verified}:f>", inline=False)
                if 'deletedOn' in TableDetails.keys():
                    deleted = TableDetails['deletedOn'][:19]
                    deleted = datetime.datetime.strptime(deleted, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
                    deleted = int(deleted.timestamp())
                    e.add_field(name='Deleted', value=f"<t:{deleted}:f>", inline=False)
                mmr_message = "```\n"
                names = []
                oldMMRs = []
                newMMRs = []
                deltas = []
                for team in TableDetails['teams']:
                    for player in team['scores']:
                        names.append(player['playerName'])
                        oldMMRs.append(player['prevMmr'])
                        newMMRs.append(player['newMmr'])
                        deltas.append(player['delta'])
                len_names = max(map(len, names))
                len_oldMMRs = len(str(max(oldMMRs)))
                len_newMMRs = len(str(max(newMMRs)))
                len_deltas = len(str(max(deltas)))
                for i in range(12):
                    mmr_message += "%s: %s --> %s (%s)\n" % (
                        names[i].ljust(len_names), str(oldMMRs[i]).ljust(len_oldMMRs), str(newMMRs[i]).ljust(len_newMMRs),
                        str(deltas[i]).rjust(len_deltas))
                mmr_message += "```"
                e.add_field(name="MMR Changes ", value=mmr_message, inline=True)
                e.set_image(url=self.site_creds['website_url'] + "/TableImage/%d.png" % int(id_or_data))
                await ctx.send(embed=e, ephemeral=True)
                return

            sizes = {'FFA': 1, '2v2': 2, '3v3': 3, '4v4': 4, '6v6': 6}
            size = sizes[table['format']]
            placements = []
            names = []
            for team in table['teams']:
                placements.append(team['rank'])
                for player in team['scores']:
                    names.append(player['playerName'])

            MMR_list = []
            for name in names:
                player = await Common.check_name(name, None, None)
                if player is None:
                    await ctx.send("A player can't be found on the site!: %s" % name)
                    return
                else:
                    try:
                        MMR_list.append(int(player['mmr']))
                    except KeyError:
                        await ctx.send("Couldn't calculate expected mmr changes since there is placement player.")
                        return 

            ave_mmrlist = [sum(MMR_list[i:i+size]) / size for i in range(0,len(MMR_list),size)]
            expected_mmrdeltas = calc.MMR_calclation(size, ave_mmrlist, placements)

            check = 0
            check_expectation = 0
            len_names = max(map(len, names))
            len_MMR_lists = len(str(max(MMR_list)))
            len_deltas = len(str(max(expected_mmrdeltas)))
            msg = "```Expected MMR Changes\n\n"

            for i in range(12):
                check += 1
                mmr_before = MMR_list[i]
                mmr_add = expected_mmrdeltas[check_expectation]
                new_mmr = int(mmr_before) + int(mmr_add)
                msg += "%s: %s --> %s (%s)\n" % (
                names[i].ljust(len_names), 
                str(mmr_before).ljust(len_MMR_lists), 
                str(new_mmr),
                str(mmr_add).rjust(len_deltas))

                if check == size:
                    msg += "\n"
                    check_expectation += 1
                    check = 0

            msg += "```"

            await ctx.send(msg)
            return
        
        else:
            id_or_data = id_or_data.replace(", ", ",")
            id_or_data = id_or_data.split(",")
            if len(id_or_data) != 13:
                await ctx.send('**Type exactly 12 players to use this command.**')
                return

            def check(m):
                return m.author.id == ctx.author.id
            
            format_type = int(id_or_data[0])
            format_list = [1, 2, 3, 4, 6]
            if format_type not in format_list:
                await ctx.send('Format error. Please check your input for errors.')
                return
            names = id_or_data[1:13]

            msg2 = await ctx.send('**Type your team number or Type all team numbers in rank order.**')
            team = await self.bot.wait_for('message', check=check)
            team = team.content

            if team.replace(" ", "").isdecimal() == False:
                await ctx.send('Input error. Please check your input for errors.')
                return

            MMR_list = []
            for name in names:
                player = await API.get.getPlayer(name, config['season'])
                if player is None:
                    await ctx.send('Name error. Please check name list.')
                    return
                else:
                    try:
                        MMR_list.append(int(player['mmr']))
                    except KeyError:
                        await ctx.send("Couldn't calculate expected mmr changes since there is placement player.")
                        return 

            ave_mmrlist = [sum(MMR_list[i:i+format_type]) / format_type for i in range(0,len(MMR_list), format_type)]

            if len(team.split()) == 1:
                if format_type == 6:
                    expected_mmrdeltas = []
                    ave_mmrlist = [sum(MMR_list[i:i+format_type]) / format_type for i in range(0,len(MMR_list), format_type)]
                    My_mmr = ave_mmrlist.pop(int(team)-1)
                    expected_mmrdeltas.append(calc.calc(My_mmr, ave_mmrlist[0], format_type))
                    expected_mmrdeltas.append(calc.calc(ave_mmrlist[0], My_mmr, format_type))
                    msg = "```Expected MMR Changes\n\n"
                    msg += "1st: %d\n" % expected_mmrdeltas[0]
                    msg += "2nd: -%d```" % expected_mmrdeltas[1]
                    await ctx.send(msg)
                    return

                expected_mmrdeltas = calc.MMR_calclation2(format_type, ave_mmrlist, int(team) - 1)
                if expected_mmrdeltas == False:
                    await ctx.send('Input error.')
                    return

                msg = "```Expected MMR Changes\n\n"
                msg += "1st: %d\n" % expected_mmrdeltas.pop(0)
                for i in range(int(12 / format_type) - 2):
                    if i == 0:
                        msg += "2nd: %d - %d\n" % (expected_mmrdeltas.pop(0), expected_mmrdeltas.pop(0))
                    elif i == 1:
                        msg += "3rd: %d - %d\n" % (expected_mmrdeltas.pop(0), expected_mmrdeltas.pop(0))
                    else:
                        msg += "%dth: %d - %d\n" % (i + 2, expected_mmrdeltas.pop(0), expected_mmrdeltas.pop(0))
                
                if format_type == 4:
                    msg += "%drd: %d```" % (int(12 / format_type), expected_mmrdeltas.pop(0))
                else:
                    msg += "%dth: %d```" % (int(12 / format_type), expected_mmrdeltas.pop(0))

                await ctx.send(msg)
                return

            else:
                rank_list = team.split()
                name_list = []
                for rank in rank_list:
                    for i in range(format_type):
                        name_list.append(names[int(rank)*format_type - 1 - i])
                MMR_list = []
                for name in name_list:
                    player = await API.get.getPlayer(name, config['season'])
                    if player is None:
                        await ctx.send("A player can't be found on the site!: %s" % name)
                        return
                    else:
                        try:
                            MMR_list.append(int(player['mmr']))
                        except KeyError:
                            await ctx.send("Couldn't calculate expected mmr changes since there is placement player.")
                            return 

                ave_mmrlist = [sum(MMR_list[i:i+format_type]) / format_type for i in range(0,len(MMR_list), format_type)]
                rank_list = [1, 2, 3, 4, 5, 6]
                expected_mmrdeltas = calc.MMR_calclation(format_type, ave_mmrlist, rank_list)

                len_names = max(map(len, name_list))
                len_oldMMRs = len(str(max(MMR_list)))
                len_deltas = len(str(max(expected_mmrdeltas)))

                msg = "```Expected MMR Changes\n\n"
                for i in range(int(12 / format_type)):
                    for i1 in range(format_type):
                        mmr_before = int(MMR_list[i*format_type + i1])
                        mmr_add = int(expected_mmrdeltas[i])
                        new_mmr = mmr_before + mmr_add
                        msg += "%s: %s --> %s (%s)\n" % (
                            name_list[i*format_type + i1].ljust(len_names), 
                            str(mmr_before).ljust(len_oldMMRs), 
                            str(new_mmr),
                            str(mmr_add).rjust(len_deltas))
                    msg += "\n"

                msg += "```"

                await ctx.send(msg)
                return

    @is_allowed_server()
    @commands.hybrid_command()
    async def table(self, ctx: commands.Context, id:int):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        pageURL = self.site_creds['website_url'] + '/TableDetails/%d' % id
        TableDetails = await API.get.getTable(tableID=id)
        if TableDetails == False:
            await ctx.send("Table not found.")
        e = discord.Embed(title="Table ID: %d" % id, url=pageURL, colour=0x1da3dd)
        format = TableDetails['format']
        tier = TableDetails['tier']
        created = TableDetails['createdOn'][:19]
        created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        created = int(created.timestamp())
        if 'verifiedOn' not in TableDetails.keys():
            await ctx.send("This table hasn't updated yet")
            return
        verified = TableDetails['verifiedOn'][:19]
        verified = datetime.datetime.strptime(verified, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        verified = int(verified.timestamp())
        message_id = TableDetails['tableMessageId']
        id_link = "https://discord.com/channels/445404006177570829/%s/%s" % (Common.channel_id(tier=tier), message_id)
        id_and_link = "[%d](%s)" % (id, id_link)
        e.add_field(name="ID", value=id_and_link, inline=True)
        e.add_field(name="Format", value=format, inline=True)
        e.add_field(name="Tier", value=tier, inline=True)
        e.add_field(name="Created", value=f"<t:{created}:f>", inline=False)
        e.add_field(name="Verified", value=f"<t:{verified}:f>", inline=False)
        if 'deletedOn' in TableDetails.keys():
            deleted = TableDetails['deletedOn'][:19]
            deleted = datetime.datetime.strptime(deleted, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            deleted = int(deleted.timestamp())
            e.add_field(name='Deleted', value=f"<t:{deleted}:f>", inline=False)
        mmr_message = "```\n"
        names = []
        oldMMRs = []
        newMMRs = []
        deltas = []
        for team in TableDetails['teams']:
            for player in team['scores']:
                names.append(player['playerName'])
                oldMMRs.append(player['prevMmr'])
                newMMRs.append(player['newMmr'])
                deltas.append(player['delta'])
        len_names = max(map(len, names))
        len_oldMMRs = len(str(max(oldMMRs)))
        len_newMMRs = len(str(max(newMMRs)))
        len_deltas = len(str(max(deltas)))
        for i in range(12):
            mmr_message += "%s: %s --> %s (%s)\n" % (
                names[i].ljust(len_names), str(oldMMRs[i]).ljust(len_oldMMRs), str(newMMRs[i]).ljust(len_newMMRs),
                str(deltas[i]).rjust(len_deltas))
        mmr_message += "```"
        e.add_field(name="MMR Changes ", value=mmr_message, inline=True)
        e.set_image(url=self.site_creds['website_url'] + "/TableImage/%d.png" % id)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def maketable(self, ctx: commands.Context, id: int):
        await ctx.defer(ephemeral=False)
        TableDetails = await API.get.getTable(tableID=id)
        if TableDetails == False:
            await ctx.send("Table not found.")
            return

        tier = TableDetails['tier']
        sizes = {'FFA': 1, '2v2': 2, '3v3': 3, '4v4': 4, '6v6': 6}
        size = sizes[TableDetails['format']]

        m_content = '!submit %d %s\n' % (size, tier)

        for team in TableDetails['teams']:
            for player in team['scores']:
                m_content += "%s %s\n" % (player['playerName'], player['score'])

        await ctx.send(m_content)

    @is_allowed_server()
    @commands.hybrid_command()
    async def strikes(self, ctx: commands.Context, *, name: Optional[str] = None):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        player = await Common.check_name(name, ctx.author.id, ctx.author.display_name)
        if player == None:
            await ctx.send("Player not found!")
            return

        recentStrikes = await API.get.getStrikes(player['name'])
        if len(recentStrikes) == 0:
            await ctx.channel.send("Strikes for player %s could not be found" % player['name'])
            return
        last3 = recentStrikes[::-1][0:3]
        strikeStr = ""
        if len(last3) < 0:
            await ctx.channel.send("Player %s has 0 strikes" % name)
            return
        for pen in last3:
            strikeDate = pen["awardedOn"][:19]
            strikeDate = datetime.datetime.strptime(strikeDate, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            strikeDate = int(strikeDate.timestamp())
            strikeStr += f"<t:{strikeDate}:f>\n"
        e = discord.Embed(title="Strikes")
        e.add_field(name="Player", value=last3[0]["playerName"], inline=False)
        e.add_field(name="Strikes", value="%d/3" % len(last3), inline=False)
        e.add_field(name="Strike Dates", value=strikeStr)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def lt(self, ctx: commands.Context, *, lineup):
        await ctx.defer(ephemeral=False)
        lineup = lineup[lineup.find("!scoreboard"):]
        index = lineup.find("Decide")
        if index != -1:
            lineup = lineup[:lineup.find("Decide")]
            lineup = lineup[:-2]
        lineup = lineup[14:]
        members = lineup.replace("`", "").replace(", ", ",").split(",")

        if len(members) != 12:
            await ctx.send(f'There are only {len(members)} players, please check your input.')


        m_content = "!submit size tier\n"

        for member in members:
            m_content += f'{member} 0\n'

        await ctx.send(m_content)

    @is_allowed_server()
    @commands.hybrid_command()
    async def fc(self, ctx: commands.Context, *, name: Optional[str] = None):
        await ctx.defer(ephemeral=False)
        player = await Common.check_name(name, ctx.author.id, ctx.author.display_name)
        if player is None:
            await ctx.send("This player can't be found on the site!")
            return

        if 'switchFc' in player.keys():
            fc = player['switchFc']
        else:
            fc = "Looks like you don't have an fc."

        try:
            if 'discordId' in player.keys() and ctx.guild.id == config['server']:
                guild = self.bot.get_guild(int(config['server']))
                member = guild.get_member(player['discordId'])
                
                role_list = []
                for role in member.roles:
                    role_list.append(role.id)
                
                if config["hostban"] in role_list:
                    await ctx.send('This player is not allowed to host any events in this server.')
        except:
            pass

        await ctx.send(fc)

    @is_allowed_server()
    @commands.hybrid_command()
    async def leaderboard(self, ctx: commands.Context):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        test = await API.get.getLeaderboard(season=config['season'])
        rank_list = []
        name_list = []
        MMR_list = []
        id_list = []
        for player in test['data']:
            rank_list.append(player['overallRank'])
            name_list.append(player['name'])
            MMR_list.append(player['mmr'])
            id_list.append(player['id'])

        len_rank = 2        
        content = ''
        for i in range(len(rank_list)):
            content += '%s: [%s](https://www.mk8dx-lounge.com/PlayerDetails/%d)\n' % (str(rank_list[i]).ljust(len_rank), name_list[i], id_list[i])

        embed=discord.Embed(title='Top 10 Leaderboard', description=content, url=self.site_creds['website_url'] + "/Leaderboard")
        await ctx.send(embed=embed, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def site(self, ctx: commands.Context):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)        
        e = discord.Embed(title="Leaderboards")
        e.add_field(name="Season1 Leaderboard", value="[S1 Leaderboard](%s)" % (
            'https://docs.google.com/spreadsheets/d/14HP9KgvFKvK-dkM4pgzGjwUqh6pb-B8ub67hkGW0744/edit?usp=sharing'),
                    inline=False)
        e.add_field(name="Season2 Leaderboard", value="[S2 Leaderboard](%s)" % (
            'https://docs.google.com/spreadsheets/d/1ttVRcfqmUqDoU_Lbw58M5MBVYT7XRHnY1UOo5kdgIqY/edit?usp=sharing'),
                    inline=False)
        e.add_field(name="Season3 Leaderboard", value="[S3 Leaderboard](%s)" % (
            'https://docs.google.com/spreadsheets/d/1IPGK_kCgdqSLwcFjzgeLsRW7qV3MLCgcSBABdZHtK4o/edit?usp=sharing'),
                    inline=False)
        e.add_field(name="Season4-1 Leaderboard", value="[S4-1 Leaderboard](%s)" % (
            'https://docs.google.com/spreadsheets/d/1GDX4zY3BE2YkU5_Uw2MdtzSagHT9mpaXFPRRZ21Ds4Q/edit?usp=sharing'),
                    inline=False)
        e.add_field(name="Season4-2 Leaderboard", value="[S4-2 Leaderboard](%s)" % (
            self.site_creds['website_url'] + '/Leaderboard?season=4&sortBy=Mmr'), inline=False)
        e.add_field(name="Season5 Leaderboard", value="[S5 Leaderboard](%s)" % (
            self.site_creds['website_url'] + '/Leaderboard?season=5&sortBy=Mmr'), inline=False)
        e.add_field(name="Season6 Leaderboard", value="[S6 Leaderboard](%s)" % (
            self.site_creds['website_url'] + '/Leaderboard?season=6&sortBy=Mmr'), inline=False)
        e.add_field(name="Season7 Leaderboard", value="[S7 Leaderboard](%s)" % (
            self.site_creds['website_url'] + '/Leaderboard?season=7&sortBy=Mmr'), inline=False)


        e.add_field(name="Lounge Server Link", value="[150cc Lounge](%s)" % (
            'https://discord.gg/revmGkE'), inline=False)
        await ctx.send(embed=e, ephemeral=True)

    @is_allowed_server()
    @commands.hybrid_command()
    async def hostban(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        try:
            if ctx.guild.id != config['server']:
                await ctx.send("You can't use this command in this server.")
                return
        except:
            await ctx.send("You can't use this command in this server.")
        test = ctx.guild.get_role(config["hostban"])
        nick_list = []
        name_list = []
        for member in test.members:
            nick_list.append(member.nick)
            name_list.append(member.name)
        message = '**The following players are not allowed to host any events:**\n'
        for i in range(len(nick_list)):
            if nick_list[i] == None:
                message += '- ' + name_list[i] + '\n'
            else:
                message += '- ' + nick_list[i] + '\n'
        
        await ctx.send(message)

    @is_allowed_server()
    @commands.hybrid_command()
    async def overallinfo(self, ctx: commands.Context, *, season: Optional[commands.Range[int, 4, config['season']]] = config['season']):
        if await Common.check_perms(ctx) == False:
            if ctx.interaction == None:
                await ctx.send('You cannot use this command in this channel.')
                return
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)
        mmr_list = []
        if season == '':
            season = config['season']
        allplayers = await API.get.getAllplayer(season)
        allplayers = allplayers["players"]
        for player in allplayers:
            if 'mmr' in player.keys() and player['eventsPlayed'] > 0:
                mmr_list.append(player['mmr'])
            else:
                break

        img = await plotting.create_overall_histogram(mmr_list, int(season))
        num_list = img[0]
        sum_num_list = [int(sum(num_list[i:i+10])) for i in range(0,len(num_list),10)]
        sum_num_list.reverse()
        percent_list = [i / sum(sum_num_list) * 100 for i in sum_num_list]

        e = discord.Embed(title="S%d Overall Info" % int(season), color=0x0084ff)
        e.add_field(name="Total Players", value=len(mmr_list), inline=False)
        avg_mmr = round((sum(mmr_list)/len(mmr_list)), 1)
        e.add_field(name="Average MMR", value=avg_mmr, inline=True)
        median = statistics.median(mmr_list)
        e.add_field(name="Median MMR", value=median, inline=True)
        stdev = statistics.pstdev(mmr_list)
        e.add_field(name="Standard Deviation", value="%.1f" % stdev, inline=True)
        f = discord.File(img[1], filename='distribution.png')
        e.set_image(url="attachment://distribution.png")
        await ctx.send(embed=e, file=f, ephemeral=True)


async def setup(bot):
    await bot.add_cog(
        Stats(bot)
    )