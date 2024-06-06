import os
from pathlib import Path
import subprocess
import logging
import psutil

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Enums import ModuleStatus


class DJctlModule(BotdeliciousModule):
    def __init__(self):
        super().__init__()
        self.directory = Path(os.getcwd())
        self.executable = [
            str(self.directory / "external" / "djctl" / "djctl.exe"),
            "start",
            "--conf",
            str(self.directory / "external" / "djctl" / "conf.yaml"),
        ]
        self.process = None

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.process = self.console()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        if self.process:
            try:
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
            si.wShowWindow = subprocess.SW_HIDE

            return subprocess.Popen(
                self.executable,
                close_fds=True,
                startupinfo=si,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True,
            )
        except Exception as e:
            logging.error(f"Failed to start subprocess: {e}")
            return None
