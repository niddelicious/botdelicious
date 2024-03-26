import json
import logging

from dotmap import DotMap
from AsyncioThread import AsyncioThread

from Modules.BotdeliciousModule import BotdeliciousModule
from Controllers.ConfigController import ConfigController
from Helpers.Enums import ModuleStatus
from Modules.EventModule import EventModule


class VJModule(BotdeliciousModule):
    _status = ModuleStatus.IDLE



