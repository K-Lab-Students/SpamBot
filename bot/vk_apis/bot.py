import time
import logging
from threading import Thread, Event
from .config import Config
from .api.client import VkClient
from .handlers import JoinHandler, MessageHandler
from .utils.logger import logger
from vk_api.bot_longpoll import VkBotEventType
import random


class VkBot:
    def __init__(self):
        self.config = Config()
        self.client = VkClient(
            self.config.group_token,
            self.config.group_id
        )
        self.handlers = {
            VkBotEventType.MESSAGE_NEW: MessageHandler(self),
            VkBotEventType.GROUP_JOIN: JoinHandler(self)
        }
        self.checking_members = {}
        self.shutdown_event = Event()

    def run(self):
        Thread(target=self._moderation_task, daemon=True).start()
        logger.info("Bot started")
        for event in self.client.longpoll.listen():
            self._route_event(event)

    def _route_event(self, event):
        handler = self.handlers.get(event.type)
        if handler:
            try:
                handler.handle(event)
            except Exception as e:
                logger.error(f"Error handling event: {e}", exc_info=True)
        else:
            logger.debug(f"No handler for event type: {event.type}")

    def handle_new_member(self, user_id, peer_id):
        if user_id in self.checking_members:
            return

        riddle, answer = random.choice(self.config.riddles)
        self.client.send_message(peer_id, riddle)
        self.checking_members[user_id] = {
            'peer_id': peer_id,
            'correct_answer': answer,
            'attempts': 0,
            'timestamp': time.time()
        }
        logger.info(f"New member {user_id} added to verification")

    def _moderation_task(self):
        while not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                for user_id in list(self.checking_members.keys()):
                    data = self.checking_members[user_id]
                    if (
                        current_time - data['timestamp'] > self.config.wait_time
                    ):
                        self._ban_user(user_id, data['peer_id'])
                        del self.checking_members[user_id]
                
                time.sleep(5)
            except Exception as e:
                logger.error(f"Moderation error: {e}")

    def _ban_user(self, user_id, peer_id):
        chat_id = peer_id - 2000000000
        self.client.kick_user(chat_id, user_id)
        self.client.delete_user_messages(peer_id)
        self.client.send_message(peer_id, self.config.ban_message)
        logger.warning(f"Banned user {user_id} by timeout")


if __name__ == "__main__":
    bot = VkBot()
    bot.run()
