import os
import subprocess
import logging

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus


class DJctl(BotdeliciousModule):
    _status = ModuleStatus.IDLE

    def __init__(self):
        super().__init__()
        self.directory = os.getcwd()
        self.executable = [
            f"{self.directory}\external\djctl\djctl.exe",
            "start",
            "--conf",
            f"{self.directory}\external\djctl\conf.yaml",
        ]

    async def start(self):
        self._status = ModuleStatus.RUNNING
        self.console()

    def _status(self):
        return self._status

    async def stop(self):
        pass

    def listen(self):
        subprocess.run(self.executable)

    def console(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NEW_CONSOLE
        )
        subprocess.Popen(self.executable, close_fds=True, startupinfo=si)
