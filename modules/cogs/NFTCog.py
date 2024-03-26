import logging
import random
import yaml
import requests
from twitchio.ext import commands

from Helpers.SessionData import SessionData
from Helpers.Timer import Timer
from Helpers.Utilities import Utilities
from Modules.EventModule import EventModule
from Modules.OpenaiModule import OpenaiModule
from Helpers.Enums import (
    Status,
    StableDiffusionStyles,
    VideoBeeple,
    VideoYule,
    VideoTrippy,
)


class NFTCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        logging.debug(f"Adding NFT/cogs")
        self.bot = bot
        self.create_shoutouts("modules/cogs/shoutouts.yml")
        self._image_generator_status = Status.ENABLED

    @commands.command(name="help", aliases=["available", "commands"])
    async def help(self, ctx: commands.Context):
        await ctx.send(
            f"Available commands: "
            f"!shoutout !mint | "
            f"Or if you just want to chat or ask a question, "
            f"message me directly in chat 🤖"
        )

    @commands.command(name="echo")
    async def echo(self, ctx: commands.Context):
        await ctx.send(f"Echo echo echo echo....")

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

            async def func(self, ctx: commands.Context, username=name, message=message):
                avatar_url = await self.bot.fetch_user_avatar(username)
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

    async def generic_shoutout(self, ctx, username):
        shoutout_variations = [
            f"@{username} is worthy of a shoutout, hence worthy of your time. "
            f"How about you drop in on them and see what's up? "
            f"https://twitch.tv/{username}",
            f"Have you checked out @{username} yet? It won't take you long, "
            f"and if they're not your thing you can just ignore it."
            f"If they are, give them a follow: https://twitch.tv/{username}",
            f"Look, @{ctx.author.name} took the time to do a shoutout for "
            f"@{username}. Are you really gonna be all rude and not give them "
            f"your attention? https://twitch.tv/{username}",
            f"https://twitch.tv/{username} | "
            f"What? You were expecting something?"
            f"You're an adult, you know how this works.",
        ]
        message = random.choice(shoutout_variations)
        avatar_url = await self.bot.fetch_user_avatar(username)
        await ctx.send(message)
        await EventModule.queue_event(
            event="shoutout",
            username=username,
            message=message,
            avatar_url=avatar_url,
        )

    async def not_found_shoutout(self, ctx: commands.Context):
        await ctx.send(
            f"I wish I knew who @{ctx.author.name} wanted me to shout out, "
            f"but they didn't supply a name. #feelsbadman"
        )

    @commands.command(name="aiso", aliases=["aishoutout", "so", "shoutout"])
    async def aiso(self, ctx: commands.Context):
        (
            success,
            username,
            message,
            avatar_url,
        ) = await OpenaiModule.shoutout(
            content=ctx.message.content, author=ctx.author.name
        )
        if success:
            await EventModule.queue_event(
                event="shoutout",
                username=username,
                message=message,
                avatar_url=avatar_url,
            )
        if message:
            await self.bot.chat(ctx.channel.name, message)
        else:
            await self.fallback_shoutout(ctx)

    @commands.command(name="lurk", aliases=["lurking", "lurker", "wurk", "wurking"])
    async def lurk(self, ctx: commands.Context):
        reply = await OpenaiModule.command_intepretor(
            ctx.message.content, ctx.author.name
        )

        await ctx.send(reply)

    async def fallback_shoutout(self, ctx: commands.Context):
        username = Utilities.find_username(ctx.message.content)
        if username:
            await self.generic_shoutout(ctx, username)
        else:
            await self.not_found_shoutout(ctx)

    @commands.command(name="hug", aliases=["squeeze", "pounce"])
    async def hug(self, ctx: commands.Context):
        reply = await OpenaiModule.command_intepretor(
            content=ctx.message.content, author=ctx.author.name
        )
        await ctx.send(reply)

    @commands.command(
        name="imagine",
        aliases=[
            "aiphoto",
            "aiimage",
            "aiimg",
            "aiart",
            "sd",
            "stable",
            "diffusion",
            "stablediffusion",
            "mint",
        ],
    )
    async def imagine(self, ctx: commands.Context):
        if self._image_generator_status == Status.DISABLED:
            await ctx.send(f"Sorry, the image generation is currently disabled")
            return

        words = ctx.message.content.split()
        style = None
        prompt_words = []
        for word in words[1:]:
            if word.startswith("--"):
                possible_style = word[2:].upper()
                if possible_style == "HELP":
                    await ctx.send(
                        f"To mint an NFT just write what you hope to see. You can also try a style by adding --[style] in your prompt. ( "
                        f"{', '.join([style.lower() for style in StableDiffusionStyles.__members__.keys()])}"
                        f" )"
                    )
                    return
                if (
                    style is None
                    and possible_style in StableDiffusionStyles.__members__
                ):
                    style = StableDiffusionStyles[possible_style].value
            else:
                prompt_words.append(word)
        if len(prompt_words) == 0:
            await ctx.send(f"You need to supply a prompt. Example: !mint cat in a hat")
            return
        prompt = " ".join(prompt_words)
        if style is None:
            style = ""
        await EventModule.queue_event(
            event="sd_generate_image",
            author=ctx.author.name,
            prompt=prompt,
            style=style,
        )

    @commands.command(name="enableimage", aliases=["imageon", "imageenable"])
    async def enableimage(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            self._image_generator_status = Status.ENABLED
            await ctx.send(f"Image generator enabled")

    @commands.command(name="disableimage", aliases=["imageoff", "imagedisable"])
    async def disableimage(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            self._image_generator_status = Status.DISABLED
            await ctx.send(f"Image generator disabled")
