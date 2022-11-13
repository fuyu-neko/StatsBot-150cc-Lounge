import discord
from discord.ext import commands
import pandas as pd

import API.get
import cogs.Common as Common
from constants import getRank, getRankdata
import plotting


class Previous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.site_creds = bot.site_creds

    async def check_name(name, id, display_name):
        if name == None:
            name_data = await API.get.getPlayerFromDiscord(id)
            if name_data is None:
                name = display_name
            else:
                name = name_data['name']
        else:
            if name.isdecimal():
                name_data = await API.get.getPlayerFromDiscord(name)
                if name_data is None:
                    name = None
                else:
                    name = name_data['name']
            else:
                name = name
        return name

    async def mmr(self, ctx: commands.Context, name, season):
        if ctx.interaction == None and await Common.check_perms(ctx) == False:
            await ctx.send('You cannot use this command in this channel.')
            return

        name = await Previous.check_name(name, ctx.author.id, ctx.author.display_name)
        if name is None:
            await ctx.send("This id can't be found on the site!", ephemeral=True)
            return

        names = name.split(',')

        if len(names) == 1:
            df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
            data = \
            df_ninkaen[['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                        'Events Played', 'Largest Gain', 'Largest Loss']][
                df_ninkaen["Player"].str.lower().isin([name.lower()])].values

            if len(data) == 0:
                await ctx.send("The specified player wasn't found. Please check your input for errors.", ephemeral=True)
                return

            Player_name = data[0][1]
            MMR = data[0][2]

            mmrRank = getRank(MMR, season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            embed = discord.Embed(title="Season%d MMR" % season, color=rankColor)
            embed.add_field(name=Player_name, value='%d' % int(MMR), inline=False)

        else:
            embed = discord.Embed(title="Season%d MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
                data = \
                df_ninkaen[['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                            'Events Played', 'Largest Gain', 'Largest Loss']][
                    df_ninkaen["Player"].str.lower().isin([name.lower()])].values

                if len(data) == 0:
                    embed.add_field(name=name, value='name error', inline=True)
                    continue

                Player_name = data[0][1]
                MMR = data[0][2]

                embed.add_field(name=Player_name, value='%d' % int(MMR), inline=True)
                MMR_list.append(int(MMR))

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                pass
            else:
                embed.add_field(name="**MMR Avg.**", value="%.1f" % average, inline=False)
        await ctx.send(embed=embed, ephemeral=True)

    async def peak(self, ctx: commands.Context, name, season):
        if ctx.interaction == None and await Common.check_perms(ctx) == False:
            await ctx.send('You cannot use this command in this channel.')
            return

        name = await Previous.check_name(name, ctx.author.id, ctx.author.display_name)
        if name is None:
            await ctx.send("This id can't be found on the site!", ephemeral=True)
            return

        names = name.split(',')

        if len(names) == 1:
            df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
            data = \
            df_ninkaen[['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                        'Events Played', 'Largest Gain', 'Largest Loss']][
                df_ninkaen["Player"].str.lower().isin([name.lower()])].values

            if len(data) == 0:
                await ctx.send("The specified player wasn't found. Please check your input for errors.", ephemeral=True)
                return

            Player_name = data[0][1]
            Peak_MMR = data[0][3]

            mmrRank = getRank(Peak_MMR, season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)

            embed = discord.Embed(title="Season%d MMR" % season, color=rankColor)
            embed.add_field(name=Player_name, value='%d' % int(Peak_MMR), inline=False)

        else:
            embed = discord.Embed(title="Season%d Peak MMR" % season)
            MMR_list = []
            for name in names:
                name = name.strip()
                df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
                data = \
                df_ninkaen[['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                            'Events Played', 'Largest Gain', 'Largest Loss']][
                    df_ninkaen["Player"].str.lower().isin([name.lower()])].values

                if len(data) == 0:
                    embed.add_field(name=name, value='name error', inline=True)
                    continue

                Player_name = data[0][1]
                Peak_MMR = data[0][3]

                embed.add_field(name=Player_name, value='%d' % int(Peak_MMR), inline=True)
                MMR_list.append(int(Peak_MMR))

            average = Common.average(sum(MMR_list), len(MMR_list))
            if average == False:
                pass
            else:
                embed.add_field(name="**Peak MMR Avg.**", value="%.1f" % average, inline=False)
        await ctx.send(embed=embed, ephemeral=True)

    async def stats(self, ctx: commands.Context, name, season):
        if ctx.interaction == None and await Common.check_perms(ctx) == False:
            await ctx.send('You cannot use this command in this channel.')
            return

        name = await Previous.check_name(name, ctx.author.id, ctx.author.display_name)
        if name is None:
            await ctx.send("This id can't be found on the site!", ephemeral=True)
            return

        if 0 < season <= 3:
            df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
            data = \
            df_ninkaen[['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                        'Events Played', 'Largest Gain', 'Largest Loss']][
                df_ninkaen["Player"].str.lower().isin([name.lower()])].values

            if len(data) == 0:
                await ctx.send("The specified player wasn't found. Please check your input for errors.", ephemeral=True)
                return

            Rank = data[0][0]
            Player_name = data[0][1]
            MMR = data[0][2]
            Peak_MMR = data[0][3]
            Win_rate = data[0][4]
            W_L = data[0][5]
            Gain_Loss = data[0][6]
            Events_played = data[0][7]
            Largest_Gain = data[0][8]
            Largest_Loss = data[0][9]

            mmrRank = getRank(MMR, season)
            ranks = getRankdata(season)
            rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
            rankURL = ranks[mmrRank]["url"]

            embed = discord.Embed(title='Season %d Stats' % season, description=Player_name, color=rankColor)
            embed.set_thumbnail(url=rankURL)
            embed.add_field(name="Rank", value=str(Rank), inline=True)
            embed.add_field(name="MMR", value='%d' % int(MMR), inline=True)
            embed.add_field(name="Peak MMR", value='%d' % int(Peak_MMR), inline=True)
            embed.add_field(name="Win Rate", value=Win_rate, inline=True)
            embed.add_field(name="W-L (Last 10)", value=W_L, inline=True)
            embed.add_field(name="Gain/Loss (Last 10)", value='%d' % int(Gain_Loss), inline=True)
            embed.add_field(name="Events Played", value='%d' % int(Events_played), inline=True)
            embed.add_field(name="Largest Gain", value=Largest_Gain, inline=True)
            embed.add_field(name="Largest Loss", value=Largest_Loss, inline=True)
            await ctx.send(embed=embed, ephemeral=True)
            return

        elif season == 4:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("You can't use this command in DMs!")
                return

            playerDetails = await API.get.getPlayerInfo(name, season=season)
            if playerDetails is None:
                e = discord.Embed(title="Season 4-2 Stats", description='name error')
                mmrHistory = [0]
                img = await plotting.create_plot(mmrHistory, season=4)
                f = discord.File(fp=img, filename='stats.png')
            else:
                mmr = playerDetails['mmr']
                mmrHistory = []
                scores = []
                partnerscores = []
                deltas = []
                changeId = []
                if 'maxMmr' in playerDetails.keys():
                    peakMMR = playerDetails['maxMmr']
                else:
                    peakMMR = 'N/A'

                matches = playerDetails['mmrChanges'][::-1]
                for match in matches:
                    if match['reason'] == 'Placement':
                        mmrHistory.append(match['newMmr'])
                    if match['reason'] == 'Table':
                        scores.append(match['score'])
                        for partner in match['partnerScores']:
                            partnerscores.append(partner)
                        deltas.append(match['mmrDelta'])
                        mmrHistory.append(match['newMmr'])
                        changeId.append(match['changeId'])

                if len(scores) == 0:
                    await ctx.send("You must play at least 1 match to see your stats", ephemeral=True)
                    return

                playerURL = self.site_creds['website_url'] + '/PlayerDetails/%d' % playerDetails['playerId']

                playerNameAndURL = "[%s](%s)" % (playerDetails['name'], playerURL)

                mmrRank = getRank(mmr, season)
                ranks = getRankdata(season)
                rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
                rankURL = ranks[mmrRank]["url"]

                if mmrHistory[-1] != mmr:
                    mmrHistory.append(mmr)

                if max(deltas) <= 0:
                    largestGain = "-"
                else:
                    tableURL = self.site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(max(deltas))]
                    largestGain = "[%s](%s)" % (playerDetails['largestGain'], tableURL)

                if min(deltas) >= 0:
                    largestLoss = "-"
                else:
                    tableURL = self.site_creds['website_url'] + "/TableDetails/%d" % changeId[deltas.index(min(deltas))]
                    largestLoss = "[%s](%s)" % (playerDetails['largestLoss'], tableURL)
                img = await plotting.create_plot(mmrHistory, season=4)
                f = discord.File(fp=img, filename='stats.png')
                e = discord.Embed(title="Season 4-2 Stats", description=playerNameAndURL, colour=rankColor)
                e.set_image(url="attachment://stats.png")
                try:
                    e.add_field(name="Rank", value=playerDetails['overallRank'])
                except KeyError:
                    e.add_field(name="Rank", value='null')
                e.add_field(name="MMR", value=mmr)
                e.add_field(name="Peak MMR", value=peakMMR)
                winRate = str(round(playerDetails['winRate'] * 100, 1))
                e.add_field(name="Win Rate", value=winRate)
                e.add_field(name="W-L (Last 10)", value=playerDetails['winLossLastTen'])
                e.add_field(name="+/- (Last 10)", value=playerDetails['gainLossLastTen'])
                aveScore = str(round(playerDetails['averageScore'], 1))
                e.add_field(name="Avg. Score", value=aveScore)
                scoreURL = self.site_creds['website_url'] + "/TableDetails/%d" % changeId[scores.index(max(scores))]
                Top_score = "[%s](%s)" % (max(scores), scoreURL)
                e.add_field(name="Top Score", value=Top_score)
                e.add_field(name="Partner Avg.", value=round(playerDetails['partnerAverage'], 1))
                e.add_field(name="Events Played", value=playerDetails['eventsPlayed'])
                e.add_field(name="Largest Gain", value=largestGain)
                e.add_field(name="Largest Loss", value=largestLoss)
                e.set_thumbnail(url=rankURL)
                e.set_image(url="attachment://stats.png")

            df_ninkaen = pd.read_csv('spreadsheet/Leaderboard%d.csv' % season, encoding='cp932')
            data = \
                df_ninkaen[
                    ['Rank', 'Player', 'MMR', 'Peak MMR', 'Win Rate', 'W - L(Last 10)', 'Gain/Loss (Last 10)',
                        'Events Played', 'Largest Gain', 'Largest Loss']][
                    df_ninkaen["Player"].str.lower().isin([name.lower()])].values

            if len(data) == 0:
                embed = discord.Embed(title='Season 4-1 Stats', description='name error')
            else:
                Rank = data[0][0]
                Player_name = data[0][1]
                MMR = data[0][2]
                Peak_MMR = data[0][3]
                Win_rate = data[0][4]
                W_L = data[0][5]
                Gain_Loss = data[0][6]
                Events_played = data[0][7]
                Largest_Gain = data[0][8]
                Largest_Loss = data[0][9]

                mmrRank = getRank(MMR, season)
                ranks = getRankdata(season)
                rankColor = int("0x%s" % (ranks[mmrRank]["color"][1:]), 16)
                rankURL = ranks[mmrRank]["url"]

                embed = discord.Embed(title='Season 4-1 Stats', description=Player_name, color=rankColor)
                embed.set_thumbnail(url=rankURL)
                embed.add_field(name="Rank", value=str(Rank), inline=True)
                embed.add_field(name="MMR", value='%d' % int(MMR), inline=True)
                if pd.isnull(Peak_MMR):
                    embed.add_field(name="Peak MMR", value='N/A', inline=True)
                else:
                    embed.add_field(name="Peak MMR", value='%d' % int(Peak_MMR), inline=True)
                embed.add_field(name="Win Rate", value=Win_rate, inline=True)
                embed.add_field(name="W-L (Last 10)", value=W_L, inline=True)
                embed.add_field(name="Gain/Loss (Last 10)", value='%d' % int(Gain_Loss), inline=True)
                embed.add_field(name="Events Played", value='%d' % int(Events_played), inline=True)
                embed.add_field(name="Largest Gain", value=Largest_Gain, inline=True)
                embed.add_field(name="Largest Loss", value=Largest_Loss, inline=True)

            page1 = e
            page2 = embed

            message2 = await ctx.send(embed=page1, file=f)
            await message2.add_reaction('◀')
            await message2.add_reaction('▶')

            reaction = None

            def check(reaction, user):
                return user == ctx.author

            while True:
                if str(reaction) == '◀':
                    await message2.edit(embed=page1)
                elif str(reaction) == '▶':
                    await message2.edit(embed=page2)

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    await message2.remove_reaction(reaction, user)
                except:
                    break
            try:
                await message2.clear_reactions()
            except:
                pass
        else:
            return


async def setup(bot):
    await bot.add_cog(
        Previous(bot)
    )