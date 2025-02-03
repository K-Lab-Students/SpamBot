from abc import ABC, abstractmethod
from vk_api.bot_longpoll import VkBotEvent


class BaseHandler(ABC):
    def __init__(self, bot):
        self.bot = bot

    @abstractmethod
    def handle(self, event: VkBotEvent):
        pass 