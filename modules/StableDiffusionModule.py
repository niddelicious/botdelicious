import asyncio
import base64
import json
import os
from pathlib import Path
import subprocess
import logging

import httpx

from Modules.BotdeliciousModule import BotdeliciousModule
from Modules.EventModule import EventModule
from Helpers.Enums import ModuleStatus


class StableDiffusionModule(BotdeliciousModule):
    _api_url = "http://127.0.0.1:42069/sdapi/v1"
    _awaiting_images = False
    _httpx = httpx.AsyncClient(timeout=None)

    def __init__(self):
        super().__init__()
        self.directory = Path(os.getcwd())
        self.working_directory = (
            self.directory / "external" / "stable-diffusion-webui"
        )
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
        si.dwFlags = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NEW_CONSOLE
        )
        # Save the current working directory
        old_cwd = os.getcwd()
        # Change the working directory to the directory of the batch file
        os.chdir(self.working_directory)
        self.process = subprocess.Popen(
            self.executable, close_fds=True, startupinfo=si
        )
        # Change the working directory back to the original directory
        os.chdir(old_cwd)

    @classmethod
    async def generate_image(cls, prompt, style):
        progress_task = asyncio.create_task(cls.get_progress())
        await cls.get_image(prompt, style)
        await progress_task
        return True

    @classmethod
    async def get_image(cls, prompt, style):
        txt2img_url = f"{cls._api_url}/txt2img"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "styles": [
                "Default_Negative",
                "Default_Negative (sfw)",
                style,
            ],
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "send_images": True,
            "save_images": True,
        }

        cls.awaiting_images = True
        response = await cls._httpx.post(
            txt2img_url, headers=headers, data=json.dumps(data)
        )

        cls.awaiting_images = False
        response_data = response.json()
        base64_image = response_data["images"][0]
        image_data = base64.b64decode(base64_image)
        with open("stable-diffusion.png", "wb") as f:
            f.write(image_data)
        return True

    @classmethod
    async def get_progress(cls):
        progress_url = f"{cls._api_url}/progress"
        while cls.awaiting_images:
            response = await cls._httpx.get(progress_url)
            if not cls.awaiting_images:
                break
            if response.status_code == 200:
                response_data = response.json()
                print(f"Progress: {response_data['progress']}")

                if response_data["current_image"]:
                    image_data = base64.b64decode(
                        response_data["current_image"]
                    )
                    with open("stable-diffusion.png", "wb") as f:
                        f.write(image_data)
                await EventModule.direct_event(
                    event="sd_progress",
                    percent=f"{round(response_data['progress']*100)}%",
                    steps=f"{response_data['state']['sampling_step']} / {response_data['state']['sampling_steps']}",
                    eta=f"{round(response_data['eta_relative'])}sec",
                )
            if not cls.awaiting_images:
                break
            await asyncio.sleep(2)
