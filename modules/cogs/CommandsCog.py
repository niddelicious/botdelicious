import logging
import random
import yaml
from twitchio.ext import commands
from Helpers.Enums import TwinklyEffect, TwinklyReact

from Helpers.SessionData import SessionData
from Helpers.Utilities import Utilities
from Modules.EventModule import EventModule
from Modules.OpenaiModule import OpenaiModule
from Modules.TwinklyModule import TwinklyModule


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
        name="lurk", aliases=["lurking", "lurker", "wurk", "wurking"]
    )
    async def lurk(self, ctx: commands.Context):
        lurk_variations = [
            f"@{ctx.author.name} is here, but they're not here; know what I mean?",
            f"If you happen to see @{ctx.author.name}, do not disturb them, they're lurking",
            f"Is it worth it? Let me lurk it. @{ctx.author.name} put their thing down, flip it and reverse it",
            f"'verb | be or remain hidden so as to wait in ambush for someone or something.' So, @{ctx.author.name}, who's the lucky one?",
            f"@{ctx.author.name} likes this so much they've decided to start twerking! No, wait, I read that wrong...",
        ]

        await ctx.send(random.choice(lurk_variations))

    @commands.command(
        name="lights", aliases=["l", "light", "twink", "twinkly"]
    )
    async def lights(self, ctx: commands.Context):
        splits = ctx.message.content.split()
        if splits[1] == "effect" and splits[2].isnumeric():
            effect_id = int(splits[2]) - 1
            if 0 <= effect_id < len(TwinklyEffect):
                effect = TwinklyEffect(effect_id)
            else:
                effect = random.choice(list(TwinklyEffect))
            await TwinklyModule.effect(effect=effect)
        elif splits[1] == "react" and splits[2].isnumeric():
            react_id = int(splits[2]) - 1
            if 0 <= react_id < len(TwinklyReact):
                react = TwinklyReact(react_id)
            else:
                react = random.choice(list(TwinklyReact))
            await TwinklyModule.react(react)
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

    @commands.command(name="fire", aliases=["flame", "flames", "lit"])
    async def fire(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="fire",
        )

    @commands.command(name="tune", aliases=["tune", "jam"])
    async def tune(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="tune",
        )

    @commands.command(name="home", aliases=["primary", "back", "dj"])
    async def home(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="switch_scene",
            scene_name="Scene: Main",
        )

    @commands.command(name="collab", aliases=["duo", "collaboration", "duet"])
    async def home(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="switch_scene",
            scene_name="Scene: Collab",
        )

    @commands.command(name="midjourney", aliases=["aiphoto", "mj", "imagine"])
    async def midjourney(self, ctx: commands.Context):
        await EventModule.queue_event(
            event="switch_scene",
            scene_name="Scene: Midjourney",
        )

    @commands.command(name="video", aliases=["v", "beeple", "beeple_crap"])
    async def video(self, ctx: commands.Context):
        video_id = False
        splits = ctx.message.content.split()
        if len(splits) > 1:
            video_id = (
                int(splits[1])
                if len(splits) > 1 and splits[1].isnumeric()
                else False
            )

        vj_loop_list = [
            "beeple/24K.mp4",  # 0
            "beeple/Angular.mp4",
            "beeple/Aquahall.mp4",
            "beeple/Bokk.mp4",
            "beeple/Breath Ctrl.mp4",
            "beeple/Brokchrd.mp4",
            "beeple/Built.ee.mp4",
            "beeple/Cleanroom.mp4",
            "beeple/Crysblast.mp4",
            "beeple/Crystmounts.mov",
            "beeple/Cuttt.mp4",  # 10
            "beeple/Dark Valley.mp4",
            "beeple/Darknet.mov",
            "beeple/Dirty Ribbon.mp4",
            "beeple/Dvde.mp4",
            "beeple/Exhaust.mov",
            "beeple/Fiber Optical.mp4",
            "beeple/Flufff.mp4",
            "beeple/Glass Ladder.mp4",
            "beeple/Glaubox.mov",
            "beeple/Gobo.v1.mp4",  # 20
            "beeple/Hexxx.mp4",
            "beeple/Homie.mp4",
            "beeple/Kewbic Flow.mov",
            "beeple/Lightgrid.mov",
            "beeple/Milkcave.mp4",
            "beeple/Moonvirus.mp4",
            "beeple/Octmesh.mp4",
            "beeple/Okkkk.mp4",
            "beeple/Out-B.mp4",
            "beeple/P-Crawl.mp4",  # 30
            "beeple/Pink Vynil.mov",
            "beeple/Poxels.mov",
            "beeple/Quicksilver.mp4",
            "beeple/Rebalance.mp4",
            "beeple/Redgate.v1.mp4",
            "beeple/Redgate.v2.mp4",
            "beeple/Setting Sun.mp4",
            "beeple/Signal Barrel.mov",
            "beeple/Steps.mp4",
            "beeple/Strt.mp4",  # 40
            "beeple/T-Hawk.mp4",
            "beeple/Tech.fux.mp4",
            "beeple/Tendril.mp4",
            "beeple/Unplug.mp4",
            "beeple/Winter Feels.mp4",
            "beeple/Wormhole.mov",
            "beeple/Wrmmm.mp4",
        ]
        if video_id is not False and video_id < len(vj_loop_list):
            video_file = vj_loop_list[video_id]
        else:
            video_id = random.choice(range(len(vj_loop_list)))
            video_file = vj_loop_list[video_id]

        await EventModule.queue_event(
            event="change_video",
            video=video_file,
        )

    @commands.command(name="tokens", aliases=["openai", "ticks", "tick"])
    async def tokens(self, ctx: commands.Context):
        token_count = SessionData.tokens_count()
        token_cost = token_count * 0.000002
        display_cost = max(token_cost, 0.01) if token_cost > 0 else 0.0
        await ctx.send(
            f"This session has used {token_count} tokens (${display_cost:.2f})"
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

    async def fallback_shoutout(self, ctx: commands.Context):
        username = Utilities.find_username(ctx.message.content)
        if username:
            await self.generic_shoutout(ctx, username)
        else:
            await self.not_found_shoutout(ctx)

    @commands.command(name="hug", aliases=["squeeze", "pounce"])
    async def hug(self, ctx: commands.Context):
        target = Utilities.find_username(ctx.message.content)
        if target:
            hug_variations = [
                f"🤗 Hey @{target}, @{ctx.author.name} is sending you a warm virtual hug! Embrace the love and pass it on to someone else in chat! 💕",
                f"Awww, @{ctx.author.name} wants to give you a cozy hug, @{target}! 🥰 Don't forget to return the favor and share some positive vibes in the chat! 🌟",
                f"😊 Look at that, @{target}! @{ctx.author.name} is wrapping their virtual arms around you for a big ol' hug! Feel the love and keep the good times rolling! 🎉",
                f"@{target}, you've just been hugged by @{ctx.author.name}! 🤗 Enjoy the embrace and remember, it's a hug-it-forward kind of day in chat! 💖",
                f"What a lovely moment, @{ctx.author.name} just sent a warm hug your way, @{target}! 🥰 Cherish the kindness and make sure to spread it around! ✨",
            ]

            await ctx.send(random.choice(hug_variations))
        else:
            await ctx.send(
                f"🤗 @{ctx.author.name} wraps their arms around themselves 🤗"
            )

    @commands.command(name="lick", aliases=["lickitylick"])
    async def lick(self, ctx: commands.Context):
        target = self.bot.findUsername(ctx.message.content)
        if target:
            lickVariations = [
                f"👅 @{ctx.author.name} puts their tongue on @{target}. Yuck.",
                f"@{ctx.author.name} is cosplaying 🐶, and @{target} gets a slobbering",
                f"Are we sure @{target} consents to @{ctx.author.name} licking them 🤔",
                f"Don't ask us why, but @{ctx.author.name} is trying to taste @{target} 😝",
            ]
            await ctx.send(random.choice(lickVariations))
        else:
            await ctx.send(
                f"@{ctx.author.name} just wants a taste. Best we can offer is themselves. Knock yourself out."
            )
