import logging
import time
from vk_api.bot_longpoll import VkBotEvent, VkBotEventType
from .base import BaseHandler
from ..utils.logger import logger


class MessageHandler(BaseHandler):
    def __init__(self, bot):
        super().__init__(bot)
        self.handled_actions = {
            'chat_invite_user': self._handle_invite,
            'chat_invite_user_by_link': self._handle_invite
        }

    def handle(self, event):
        if event.type != VkBotEventType.MESSAGE_NEW:
            return
        message = event.object.message
        action = message.get('action', {})
        if action.get('type') in self.handled_actions:
            self.handled_actions[action['type']](event)
        else:
            self._check_response(event)

    def _handle_invite(self, event):
        message = event.object.message
        try:
            user_id = message['action']['member_id']
        except:
            user_id = message['from_id']
        peer_id = event.object.message['peer_id']
        self.bot.handle_new_member(user_id, peer_id)

    def _check_response(self, event):
        message = event.object.message
        user_id = message['from_id']
        peer_id = message['peer_id']
        text = message['text']
        if user_id not in self.bot.checking_members:
            return
        member_info = self.bot.checking_members[user_id]
        correct_answer = member_info['correct_answer']
        if text.strip().lower() == correct_answer.strip().lower():
            self._handle_correct_answer(user_id, peer_id)
        else:
            self._handle_wrong_answer(user_id, peer_id, message['conversation_message_id'])

    def _handle_correct_answer(self, user_id, peer_id):
        self.bot.client.delete_user_messages(peer_id)
        self.bot.client.send_message(peer_id, self.bot.config.greeting_message)
        del self.bot.checking_members[user_id]
        logger.info(f"User {user_id} passed verification")

    def _handle_wrong_answer(self, user_id, peer_id, message_id):
        member_info = self.bot.checking_members[user_id]
        member_info['attempts'] += 1
        self.bot.client.delete_message(peer_id, message_id)
        if member_info['attempts'] >= self.bot.config.max_attempts:
            self._ban_user(user_id, peer_id)
        else:
            remaining = self.bot.config.max_attempts - member_info['attempts']
            self.bot.client.send_message(
                peer_id,
                f"Неправильно! Осталось попыток: {remaining}"
            )
            member_info['timestamp'] = time.time()

    def _ban_user(self, user_id, peer_id):
        chat_id = peer_id - 2000000000
        self.bot.client.kick_user(chat_id, user_id)
        self.bot.client.delete_user_messages(peer_id)
        self.bot.client.send_message(peer_id, self.bot.config.ban_message)
        del self.bot.checking_members[user_id]
        logger.warning(f"Banned user {user_id} in chat {chat_id}")
