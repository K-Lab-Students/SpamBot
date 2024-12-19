import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_path = "RUSpam/spam_deberta_v4"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
GROUP_ID = 'your_group_id' 
ACCESS_TOKEN = 'your_access_token'
THRESHOLD_REACTIONS = 3 

def is_spam(message):
    inputs = tokenizer(message, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    return True if predicted_class == 1 else False

# Основной класс бота
class VkBot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.message_reactions = {} 
    def run(self):
        print("Бот запущен!")
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object['message']
                user_id = message["from_id"]
                peer_id = message["peer_id"]
                message_id = message["conversation_message_id"]
                text = message["text"]

                if peer_id > 2_000_000_000 and is_spam(text):
                    print(f"Обнаружено спам-сообщение: {text}")
                    self.delete_message(peer_id=peer_id, user_id=user_id, message_id=message_id)
                    

    def delete_message(self, peer_id, user_id, message_id):
        """Удалить сообщение"""
        if not self.is_conservation_admin(peer_id=peer_id, user_id=user_id):
            self.vk.messages.delete(cmids=message_id, peer_id=peer_id)

    def is_conservation_admin(self, peer_id, user_id):
        """Проверка пользователя на администратора беседы."""
        members = self.vk.messages.getConversationMembers(peer_id=peer_id)
        for member in members['items']:
            if member['member_id'] == user_id:
                return member['is_admin']
        return False

# Запуск бота
if __name__ == "__main__":
    bot = VkBot(GROUP_ID, ACCESS_TOKEN)
    bot.run()
