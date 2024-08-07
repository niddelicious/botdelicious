import asyncio
import base64
import json
import os
import shutil
from pathlib import Path
import subprocess
import logging
from PIL import Image
from datetime import datetime
import httpx
import psutil
from Controllers.ConfigController import ConfigController

from Modules.BotdeliciousModule import BotdeliciousModule
from Modules.EventModule import EventModule
from Modules.ChatModule import ChatModule
from Helpers.Enums import ModuleStatus
from Helpers.FTPClient import FTPClient
from Helpers.DiscordBot import DiscordBot
from Helpers.Utilities import Utilities


class StableDiffusionModule(BotdeliciousModule):
    _api_url = "http://127.0.0.1:42069/sdapi/v1"
    _awaiting_images = False
    _httpx = httpx.AsyncClient(timeout=None)

    def __init__(self):
        super().__init__()
        self.directory = Path(os.getcwd())
        self.working_directory = self.directory / "external" / "stable-diffusion-webui"
        self.executable = ["api.bat"]
        self.process = None

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.console()
        EventModule.update_sd_module(self)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        if self.process:
            try:
                # Use psutil to find and terminate the process tree
                parent_pid = self.process.pid
                parent = psutil.Process(parent_pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.terminate()
                parent.terminate()
                gone, still_alive = psutil.wait_procs([parent] + children, timeout=5)
                for p in still_alive:
                    p.kill()
            except Exception as e:
                logging.error(f"Error while stopping subprocess: {e}")
            finally:
                self.process = None
        self.set_status(ModuleStatus.IDLE)

    def listen(self):
        subprocess.run(self.executable)

    def console(self):
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = (
                subprocess.SW_HIDE
            )  # Prevents a console window from being created

            # Save the current working directory
            old_cwd = os.getcwd()
            # Change the working directory to the directory of the batch file
            os.chdir(self.working_directory)
            self.process = subprocess.Popen(
                self.executable,
                close_fds=True,
                startupinfo=si,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True,
            )
            # Change the working directory back to the original directory
            os.chdir(old_cwd)
        except Exception as e:
            logging.error(f"Failed to start subprocess: {e}")
            self.process = None

    @classmethod
    async def generate_image(cls, prompt, style, author):
        progress_task = asyncio.create_task(cls.get_progress())
        await cls.get_image(prompt, style, author)
        await progress_task
        return True

    @classmethod
    async def get_image(cls, prompt, style, author):
        sd_config = ConfigController.get_config_file("sd-config.yml")
        txt2img_url = f"{cls._api_url}/txt2img"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "negative_prompt": sd_config.negative_prompt,
            "styles": ["Default_Negative", "Default_Negative (sfw)", style],
            "width": sd_config.width,
            "height": sd_config.height,
            "steps": sd_config.steps,
            "sampler_name": sd_config.sampler_name,
            "cfg_scale": sd_config.cfg_scale,
            "send_images": True,
            "save_images": True,
            "hr_scale": sd_config.hr_scale,
            "hr_upscaler": sd_config.hr_upscaler,
            "hr_sampler_name": sd_config.hr_sampler_name,
            "enable_hr": sd_config.enable_hr,
            "denoising_strength": sd_config.denoising_strength,
        }

        cls._awaiting_images = True
        try:
            response = await cls._httpx.post(
                txt2img_url, headers=headers, data=json.dumps(data)
            )
            response.raise_for_status()
            logging.debug(f"A111 response: {response.json()}")
        except httpx.RequestError as e:
            logging.error(f"An error occurred while requesting {e.request.url!r}.")
        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error response {e.response.status_code} while requesting {e.request.url!r}."
            )

        cls._awaiting_images = False
        response_data = response.json()
        base64_image = response_data["images"][0]
        image_data = base64.b64decode(base64_image)
        with open("stable-diffusion.png", "wb") as f:
            f.write(image_data)

        if await Utilities.check_file_size("./stable-diffusion.png") > 10000:
            await cls.save_images(prompt, author)

        return True

    @classmethod
    async def get_progress(cls):
        progress_url = f"{cls._api_url}/progress"
        while cls._awaiting_images:
            response = await cls._httpx.get(progress_url)
            if not cls._awaiting_images:
                break
            if response.status_code == 200:
                response_data = response.json()
                print(f"Progress: {response_data['progress']}")

                if response_data["current_image"]:
                    image_data = base64.b64decode(response_data["current_image"])
                    with open("stable-diffusion.png", "wb") as f:
                        f.write(image_data)
                await EventModule.direct_event(
                    event="sd_progress",
                    percent=f"{round(response_data['progress']*100)}%",
                    steps=f"{response_data['state']['sampling_step']} / {response_data['state']['sampling_steps']}",
                    eta=f"{round(response_data['eta_relative'])}sec",
                )
            if not cls._awaiting_images:
                break
            await asyncio.sleep(3)

    @classmethod
    async def save_images(cls, prompt, author):
        sd_config = ConfigController.get_config_file("sd-config.yml")
        if not sd_config.upload:
            return
        new_filename = datetime.now().strftime("%Y%m%d-%H%M%S")

        with Image.open("stable-diffusion.png") as img:
            img.save(f"stable-diffusion.jpg", "JPEG", quality=60)
            img.thumbnail((128, 128))
            img.save(f"stable-diffusion-th.jpg", "JPEG", quality=60)

        if sd_config.upload_site:
            if FTPClient.upload(new_filename):
                await ChatModule.send_message(
                    f"{author} ordered a '{prompt}': {sd_config.site_url}/{new_filename}"
                )
        if sd_config.upload_discord:
            discord_url = await DiscordBot.upload(
                filename=new_filename, prompt=prompt, author=author
            )
            if discord_url:
                await ChatModule.send_message(
                    f"{author} ordered a '{prompt}': {discord_url}"
                )
        if sd_config.upload_gallery:
            destination_directory = "C:/Users/micro/Pictures/SD Chat"
            destination_path_orig = (
                f"{destination_directory}/Original/{new_filename}.png"
            )
            destination_path_lossy = (
                f"{destination_directory}/Compressed/{new_filename}.jpg"
            )
            destination_path_thumb = (
                f"{destination_directory}/Thumbnails/{new_filename}.jpg"
            )
            shutil.copy("stable-diffusion.png", destination_path_orig)
            shutil.copy("stable-diffusion.jpg", destination_path_lossy)
            shutil.copy("stable-diffusion-th.jpg", destination_path_thumb)
