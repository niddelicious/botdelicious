import logging
import random
import re
from twitchio.ext import commands
import yaml

from modules.Event import EventModule
from modules.Twinkly import TwinklyModule


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        logging.debug(f"Adding commands/cogs")
        self.bot = bot
        self.create_shoutouts("modules/cogs/shoutouts.yml")

    @commands.command(name="echo")
    async def echo(self, ctx: commands.Context):
        await ctx.send(f"Echo echo echo echo....")

    @commands.command(name="id", aliases=["track"])
    async def id(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="show_big_track_id",
        )

    @commands.command(name="check", aliases=["debug"])
    async def check(self, ctx: commands.Context):
        logging.debug(self)

    def create_shoutouts(self, yaml_file):
        with open(yaml_file, "r") as stream:
            commands_data = yaml.safe_load(stream)
        for command_data in commands_data:
            name = command_data["name"]
            aliases = command_data.get("aliases", [])
            message = command_data["message"]

            async def func(
                self, ctx: commands.Context, username=name, message=message
            ):
                avatar_url = await self.bot.fetch_user_info(username)
                await ctx.send(message)
                await EventModule.queue_event(
                    event="shoutout",
                    username=username,
                    message=message,
                    avatar_url=avatar_url,
                )

            func.__name__ = name
            func = commands.command(name=name, aliases=aliases)(func)
            setattr(self, name, func)

    @commands.command(name="shoutout", aliases=["so", "shout"])
    async def shoutout(self, ctx: commands.Context):
        username = self.bot.find_username(ctx.message.content)
        if not username:
            await self.not_found_shoutout(ctx)
        else:
            await self.generic_shoutout(ctx, username)

    async def generic_shoutout(self, ctx, username):
        shoutout_variations = [
            f"@{username} is worthy of a shoutout, hence worthy of your time. How about you drop in on them and see what's up? https://twitch.tv/{username}",
            f"Have you checked out @{username} yet? It won't take you long, and if they're not your thing you can just ignore it. If they are, give them a follow: https://twitch.tv/{username}",
            f"Look, @{ctx.author.name} took the time to do a shoutout for @{username}. Are you really gonna be all rude and not give them your attention? https://twitch.tv/{username}",
            f"https://twitch.tv/{username} | What? You were expecting something? You're an adult, you know how this works.",
        ]
        message = random.choice(shoutout_variations)
        avatar_url = await self.bot.fetch_user_info(username)
        await ctx.send(message)
        await EventModule.queue_event(
            event="shoutout",
            username=username,
            message=message,
            avatar_url=avatar_url,
        )

    async def not_found_shoutout(self, ctx: commands.Context):
        await ctx.send(
            f"I wish I knew who @{ctx.author.name} wanted me to shout out, but they didn't supply a name. #feelsbadman"
        )

    @commands.command(
        name="lights", aliases=["l", "light", "twink", "twinkly"]
    )
    async def lights(self, ctx: commands.Context):
        splits = ctx.message.content.split()
        if splits[1] == "effect" and splits[2].isnumeric():
            await TwinklyModule.effect(effect_id=int(splits[2]))
        elif splits[1] == "react" and splits[2].isnumeric():
            await TwinklyModule.react(react_id=int(splits[2]))
        elif (
            (splits[1] == "color" or splits[1] == "colour")
            and splits[2].isnumeric()
            and splits[3].isnumeric()
            and splits[4].isnumeric()
        ):
            await TwinklyModule.color(
                red=int(splits[2]), green=int(splits[3]), blue=int(splits[4])
            )
        elif splits[1] == "white":
            await TwinklyModule.color(red=255, green=178, blue=105)
        elif splits[1] == "black":
            await TwinklyModule.color(red=0, green=0, blue=0)
        else:
            await ctx.send(
                f"Available lights: react [1-12] | effect [1-5] | color [0-255] [0-255] [0-255]"
            )
