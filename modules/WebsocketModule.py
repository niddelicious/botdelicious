from websocket_server import WebsocketServer
import threading
import json
import logging

from Modules.BotdeliciousModule import BotdeliciousModule
from Controllers.ConfigController import ConfigController
from Helpers.Enums import ModuleStatus


class WebsocketModule(BotdeliciousModule):
    websocket_server = None

    def __init__(self):
        super().__init__()
        self.setup_websocket_server()

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        threading.Thread(target=self.websocket_server.run_forever).start()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.websocket_server.server_close()
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def setup_websocket_server(cls):
        cls.websocket_server = WebsocketServer(port=9011, host="127.0.0.1")
        cls.websocket_server.set_fn_new_client(cls.new_client)
        cls.websocket_server.set_fn_client_left(cls.client_left)

    @classmethod
    def stop_websocket_server(cls):
        cls.websocket_server.server_close()

    @classmethod
    def new_client(self, client, server):
        logging.info(f"New client connected and was given id {client['id']}")

    @classmethod
    def client_left(self, client, server):
        logging.info(f"Client({client['id']}) disconnected")

    @classmethod
    async def send_websocket_message(cls, message):
        cls.websocket_server.send_message_to_all(json.dumps(message))
