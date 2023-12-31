import pysftp
import os

import logging

from Controllers.ConfigController import ConfigController


class FTPClient:
    ConfigController.get_config()
    config = ConfigController.get("sftp")
    sfpt_host = config.host
    sfpt_username = config.username
    sfpt_password = config.password
    sfpt_port = config.port
    sftp_root_dir = config.root_dir

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    @classmethod
    def upload(cls, filename: str = None):
        try:
            with pysftp.Connection(
                cls.sfpt_host,
                username=cls.sfpt_username,
                password=cls.sfpt_password,
                port=cls.sfpt_port,
                cnopts=cls.cnopts,
            ) as sftp:
                source = "stable-diffusion"
                original = f"{source}.png"
                lossy = f"{source}.jpg"
                thumbnail = f"{source}-th.jpg"

                destination = f"{filename}"

                sftp.put(original, f"{cls.sftp_root_dir}/sd-img/{destination}.png")
                logging.info(
                    f"Uploaded {original} to {cls.sftp_root_dir}/sd-img/{destination}.png"
                )
                sftp.put(lossy, f"{cls.sftp_root_dir}/sd-lossy/{destination}.jpg")
                logging.info(
                    f"Uploaded {lossy} to {cls.sftp_root_dir}/sd-lossy/{destination}.jpg"
                )
                sftp.put(thumbnail, f"{cls.sftp_root_dir}/sd-thumbs/{destination}.jpg")
                logging.info(
                    f"Uploaded {thumbnail} to {cls.sftp_root_dir}/sd-img/{destination}.jpg"
                )
            return True
        except Exception as e:
            logging.error(f"FTPClient.upload: {e}")
