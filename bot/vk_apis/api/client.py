import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import random
from ..utils.logger import logger


class VkClient:
    def __init__(self, group_token, group_id):
        self.session = vk_api.VkApi(token=group_token)
        self.api = self.session.get_api()
        self.longpoll = VkBotLongPoll(self.session, group_id)
        self.group_id = group_id
        self.tracking_messages = {}

    def send_message(self, peer_id, text):
        try:
            random_id = int(random.randint(1, int(1e9)))
            response = self.api.messages.send(
                peer_ids=[peer_id],
                message=text,
                random_id=random_id,
                v='5.199'
            )
            if peer_id not in self.tracking_messages:
                self.tracking_messages[peer_id] = []
            self.tracking_messages[peer_id].append(response[0]["conversation_message_id"])
            logger.info(f"Sent message to {peer_id}: {text}")
            return response
        except Exception as e:
            logger.error(f"Send message error: {e}")

    def delete_message(self, peer_id, message_id):
        try:
            self.api.messages.delete(
                cmids=message_id,
                peer_id=peer_id,
                delete_for_all=1
            )
            logger.info(f"Deleted message {message_id} in {peer_id}")
        except Exception as e:
            logger.error(f"Delete message error: {e}")

    def delete_user_messages(self, peer_id):
        try:
            for message_id in self.tracking_messages.get(peer_id, []):
                self.delete_message(peer_id, message_id)
            self.tracking_messages[peer_id] = []
        except Exception as e:
            logger.error(f"Error deleting user messages: {e}")

    def kick_user(self, chat_id, user_id):
        try:
            self.api.messages.removeChatUser(
                chat_id=chat_id,
                user_id=user_id
            )
            logger.info(f"Kicked user {user_id} from chat {chat_id}")
        except Exception as e:
            logger.error(f"Kick user error: {e}")

    def get_bot_user_id(self):
        return -self.group_id

    def is_conversation_admin(self, peer_id, user_id):
        try:
            response = self.api.messages.getConversationMembers(
                peer_id=peer_id
            )
            for member in response.get("items", []):
                if member.get("member_id") == user_id:
                    return member.get("is_admin", False)
            return False
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            return False

    def listen(self):
        return self.longpoll.listen()