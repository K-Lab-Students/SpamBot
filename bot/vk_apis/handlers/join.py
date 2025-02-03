import time
import random
import logging
from .base import BaseHandler
from vk_api.bot_longpoll import VkBotEventType

logger = logging.getLogger(__name__)


class JoinHandler(BaseHandler):
    def __init__(self, bot):
        super().__init__(bot)

    def handle(self, event):
        if event.type != VkBotEventType.GROUP_JOIN:
            return

        user_id = event.object.user_id
        peer_id = event.object.peer_id
        self.bot.handle_new_member(user_id, peer_id)

    def _send_riddle(self, peer_id, user_id):
        riddle, answer = random.choice(self.bot.config.riddles)
        self.bot.client.send_message(peer_id, riddle)
        self.bot.checking_members[user_id] = {
            'peer_id': peer_id,
            'correct_answer': answer,
            'attempts': 0,
            'timestamp': time.time()
        }
        logger.info(f"Sent riddle to {user_id} in {peer_id}")
