import discord
from discord.ext import commands
from discord import app_commands
import datetime
from dateutil.relativedelta import relativedelta
import json
from typing import Optional
import time

import API.get
import cogs.Common as Common

with open('config.json', 'r') as cjson:
    config = json.load(cjson)

class Staff(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.site_creds = bot.site_creds

    def is_allowed_server():
        def predicate(ctx):
            allowed_server = ctx.guild.id in config['server']
            return allowed_server
        return commands.check(predicate)

    #commands in this file are not public

    #example of staff command
    @is_allowed_server()
    @commands.hybrid_command()
    @app_commands.guilds(config['150cc_Lounge_server'])
    @app_commands.default_permissions(view_audit_log = True)
    @commands.has_any_role("Administrator", "Admin", "MKCentral Staff", "Site Administrator", "Site Moderator", "Updater", "Lounge Staff")
    async def command_name(self, ctx: commands.Context, *, name: Optional[str] = None):
        await ctx.defer()

async def setup(bot):
    await bot.add_cog(
        Staff(bot)
    )