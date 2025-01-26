import logging
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import os
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Пусть это ваш путь к модели
model_path = "RUSpam/spam_deberta_v4"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Ваши данные
GROUP_ID = '79'
ACCESS_TOKEN = 'Bg'

# Пусть для хранения данных мы будем использовать JSON-файл
DATA_FILE = "data.json"

def load_data(file=DATA_FILE):
    """
    Загрузка данных из локального JSON-файла.
    Если файл не существует, возвращаем пустой словарь.
    Если файл есть, но повреждён, также возвращаем пустой словарь.
    """
    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Ошибка чтения JSON-файла. Начинаем с пустого словаря.")
            return {}
    return {}

def save_data(data, file=DATA_FILE):
    """Сохранение данных в локальный JSON-файл."""
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_spam(message):
    """
    Проверка сообщения на спам с помощью модели.
    Возвращает True, если спам, иначе False.
    """
    inputs = tokenizer(message, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    return predicted_class == 1

class VkBot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        
        # Загружаем данные из локального файла (словарь)
        self.data_store = load_data()
        # Убедимся, что в self.data_store есть список под ключом "messages"
        if "messages" not in self.data_store:
            self.data_store["messages"] = []
        
        logger.info(f"Инициализация бота для группы {group_id}")

    def run(self):
        logger.info("Бот запущен и готов к работе!")
        for event in self.longpoll.listen():
            try:
                if event.type == VkBotEventType.MESSAGE_NEW:
                    logger.debug(f"Новое событие MESSAGE_NEW: {event.object}")

                    message = event.object['message']
                    user_id = message["from_id"]
                    peer_id = message["peer_id"]
                    message_id = message["conversation_message_id"]
                    text = message["text"]

                    logger.info(
                        f"Получено сообщение (ID: {message_id}) от пользователя {user_id} "
                        f"в беседе {peer_id}: '{text}'"
                    )

                    # Проверка на спам
                    spam_flag = is_spam(text)  # True/False

                    # Сохраняем все входящие сообщения (включая спам)
                    self.store_message(
                        peer_id=peer_id,
                        user_id=user_id,
                        message_id=message_id,
                        text=text,
                        is_spam=spam_flag
                    )

                    # Если это групповая беседа (peer_id > 2_000_000_000) и сообщение — спам
                    if peer_id > 2_000_000_000 and spam_flag:
                        logger.warning(
                            f"Обнаружено спам-сообщение от пользователя {user_id}: '{text}'"
                        )
                        self.delete_message(peer_id=peer_id, user_id=user_id, message_id=message_id)
                    else:
                        logger.debug("Сообщение не является спамом или не из групповой беседы.")

            except Exception as e:
                logger.error(f"Ошибка при обработке события: {e}", exc_info=True)

    def store_message(self, peer_id, user_id, message_id, text, is_spam):
        """
        Сохраняет данные о любом входящем сообщении в локальном JSON-файле.
        Храним: peer_id, user_id, message_id, текст, отметку спам/не спам и время.
        """
        # Создаём структуру для нового сообщения
        msg_data = {
            "peer_id": peer_id,
            "user_id": user_id,
            "message_id": message_id,
            "text": text,
            "is_spam": is_spam,
            "timestamp": time.time()
        }

        # Добавляем в список сообщений
        self.data_store["messages"].append(msg_data)
        # Сохраняем сразу в файл
        save_data(self.data_store)
        logger.debug(f"Сообщение {peer_id}_{message_id} сохранено в data.json.")

    def delete_message(self, peer_id, user_id, message_id):
        """Удалить сообщение, если пользователь не админ."""
        is_admin = self.is_conversation_admin(peer_id=peer_id, user_id=user_id)
        logger.debug(
            f"Проверка пользователя {user_id} на администратора в беседе {peer_id}: {is_admin}"
        )
        if not is_admin:
            try:
                self.vk.messages.delete(
                    cmids=message_id, 
                    peer_id=peer_id, 
                    delete_for_all=1
                )
                logger.info(
                    f"Сообщение (ID: {message_id}) удалено из беседы {peer_id} "
                    f"пользователем {user_id}."
                )
            except Exception as e:
                logger.error(
                    f"Не удалось удалить сообщение (ID: {message_id}) в беседе {peer_id}: {e}",
                    exc_info=True
                )
        else:
            logger.debug(
                f"Сообщение (ID: {message_id}) не удалено, так как пользователь {user_id} "
                f"является администратором."
            )

    def is_conversation_admin(self, peer_id, user_id):
        """Проверка пользователя на администратора беседы."""
        try:
            members = self.vk.messages.getConversationMembers(peer_id=peer_id)
            for member in members['items']:
                if member['member_id'] == user_id:
                    return member.get('is_admin', False)
        except Exception as e:
            logger.error(
                f"Ошибка при получении списка участников беседы {peer_id}: {e}",
                exc_info=True
            )
        return False

# Запуск бота
if __name__ == "__main__":
    bot = VkBot(GROUP_ID, ACCESS_TOKEN)
    bot.run()
