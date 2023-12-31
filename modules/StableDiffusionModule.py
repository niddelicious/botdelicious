import asyncio
import base64
import json
import os
from pathlib import Path
import subprocess
import logging
from PIL import Image
from datetime import datetime
import httpx
from Controllers.ConfigController import ConfigController

from Modules.BotdeliciousModule import BotdeliciousModule
from Modules.EventModule import EventModule
from Helpers.Enums import ModuleStatus
from Helpers.FTPClient import FTPClient
from Helpers.DiscordBot import DiscordBot


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
        self.process.kill()
        self.set_status(ModuleStatus.IDLE)

    def listen(self):
        subprocess.run(self.executable)

    def console(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NEW_CONSOLE
        # Save the current working directory
        old_cwd = os.getcwd()
        # Change the working directory to the directory of the batch file
        os.chdir(self.working_directory)
        self.process = subprocess.Popen(self.executable, close_fds=True, startupinfo=si)
        # Change the working directory back to the original directory
        os.chdir(old_cwd)

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
        response = await cls._httpx.post(
            txt2img_url, headers=headers, data=json.dumps(data)
        )

        cls._awaiting_images = False
        response_data = response.json()
        base64_image = response_data["images"][0]
        image_data = base64.b64decode(base64_image)
        with open("stable-diffusion.png", "wb") as f:
            f.write(image_data)

        new_filename = datetime.now().strftime("%Y%m%d-%H%M%S")

        with Image.open("stable-diffusion.png") as img:
            img.save(f"stable-diffusion.jpg", "JPEG", quality=60)
            img.thumbnail((128, 128))
            img.save(f"stable-diffusion-th.jpg", "JPEG", quality=60)

        FTPClient.upload(new_filename)
        await DiscordBot.upload(filename=new_filename, prompt=prompt, author=author)

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
