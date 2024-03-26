import logging
import asyncio
from twitchio.ext import commands
from Helpers.Enums import ModuleStatus


class AdminCog(commands.Cog):
    def __init__(self):
        logging.debug(f"Adding commands/cogs")

    @commands.command(name="restart", aliases=["start", "boot", "reboot"])
    async def restart(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            splits = ctx.message.content.split()
            from Controllers.ModulesController import ModulesController

            if splits[1] in ModulesController.list_modules():
                module = splits[1]
                status = ModulesController.get_module_status(module)
                logging.debug(f"Restarting module: {module}")
                await ctx.send(f"Restarting {splits[1]}")
                if status == ModuleStatus.RUNNING:
                    ModulesController.stop_module(module_name=module)
                    await asyncio.sleep(5)
                ModulesController.start_module(module_name=module)

            else:
                await ctx.send(f"Module {splits[1]} not found")

    @commands.command(name="stop", aliases=["kill", "end", "terminate"])
    async def stop(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            splits = ctx.message.content.split()
            from Controllers.ModulesController import ModulesController

            if splits[1] in ModulesController.list_modules():
                module = splits[1]
                status = ModulesController.get_module_status(module)
                logging.debug(f"Restarting module: {module}")
                await ctx.send(f"Restarting {splits[1]}")
                if status == ModuleStatus.RUNNING:
                    ModulesController.stop_module(module_name=module)
                    await asyncio.sleep(5)
            else:
                await ctx.send(f"Module {splits[1]} not found")
