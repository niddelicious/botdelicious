import os
from pathlib import Path
import subprocess
import logging

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Enums import ModuleStatus


class DJctlModule(BotdeliciousModule):
    def __init__(self):
        super().__init__()
        self.directory = Path(os.getcwd())
        self.executable = [
            self.directory / "external" / "djctl" / "djctl.exe",
            "start",
            "--conf",
            self.directory / "external" / "djctl" / "conf.yaml",
        ]

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.process = self.console()

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
        return subprocess.Popen(
            self.executable, close_fds=True, startupinfo=si
        )
