import logging
import random
from twitchio.ext import commands

from Helpers.Enums import TwinklyEffect, TwinklyReact
from Modules.OpenaiModule import OpenaiModule
from Modules.TwinklyModule import TwinklyModule


class LightsCog(commands.Cog):
    def __init__(self):
        logging.debug(f"Adding lights/cogs")

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
                react = TwinklyReact.id(react_id)
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
        elif splits[1] == "ai":
            colors = await OpenaiModule.rgb_intepretor(ctx.message.content)
            if colors is not None:
                await TwinklyModule.color(
                    red=colors["red"],
                    green=colors["green"],
                    blue=colors["blue"],
                )
        else:
            await ctx.send(
                f"Available lights: "
                f"react [1-12] | "
                f"effect [1-5] | "
                f"color [0-255] [0-255] [0-255] | "
                f"ai [name or description]"
            )
