import logging
from twitchio.ext import commands
import yaml

from modules.Event import EventModule


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
            event="show_track_id",
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
                message_to_send = message
                await ctx.send(message_to_send)
                await EventModule.queue_event(
                    event="shoutout",
                    username=username,
                    message=message,
                    avatar_url=avatar_url,
                )

            func.__name__ = name
            func = commands.command(name=name, aliases=aliases)(func)
            setattr(self, name, func)
