import discord
from discord.ext import commands
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

initial_extensions = ['cogs.Stats', 'cogs.Staff']

class StatsBot(commands.AutoShardedBot):

    def __init__(self, command_prefix=commands.when_mentioned_or("^"), *, intents: discord.Intents = intents) -> None:
        super().__init__(command_prefix, intents=intents)

    async def setup_hook(self) -> None:
        await bot.tree.sync()

bot = StatsBot(intents=intents)        

with open('config.json', 'r') as cjson:
    bot.config = json.load(cjson)

with open('credentials.json', 'r') as cjson:
    bot.site_creds = json.load(cjson)

@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    await bot.change_presence(
        activity=discord.Activity(status=discord.Status.online, type=discord.ActivityType.watching,
                                  name=f"{len(bot.guilds)} servers"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await(await ctx.send("Your command is missing an argument: `%s`" %
                       str(error.param))).delete(delay=10)
        return
    if isinstance(error, commands.CommandOnCooldown):
        await(await ctx.send("This command is on cooldown; try again in %.0fs"
                       % error.retry_after)).delete(delay=5)
        return
    if isinstance(error, commands.MissingAnyRole):
        await(await ctx.send("You need one of the following roles to use this command: `%s`"
                             % (", ".join(error.missing_roles)))
              ).delete(delay=10)
        return
    if isinstance(error, commands.BadArgument):
        await(await ctx.send("BadArgument Error: `%s`" % error.args)).delete(delay=10)
        return
    if isinstance(error, commands.BotMissingPermissions):
        await(await ctx.send("I need the following permissions to use this command: %s"
                       % ", ".join(error.missing_perms))).delete(delay=10)
        return
    if isinstance(error, commands.NoPrivateMessage):
        await(await ctx.send("You can't use this command in DMs!")).delete(delay=5)
        return
    if isinstance(error, commands.CheckFailure):
        return
    raise error

async def main():
    async with bot:
        for extension in initial_extensions:
            await bot.load_extension(extension)
        await bot.start(bot.config["token"])

asyncio.run(main())