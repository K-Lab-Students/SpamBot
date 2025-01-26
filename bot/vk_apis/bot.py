import os
import random
import time
import logging
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

GROUP_TOKEN = os.getenv('GROUP_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))
RIDDLES = eval(os.getenv('RIDDLES'))  
GREETING_MESSAGE = os.getenv('GREETING_MESSAGE')
BAN_MESSAGE = os.getenv('BAN_MESSAGE')

logging.info("Переменные окружения загружены")
logging.debug(f"GROUP_ID: {GROUP_ID}")
logging.debug(f"RIDDLES: {RIDDLES}")

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
logging.info("VK API сессия успешно инициализирована")

CHECKING_MEMBERS = {}

def send_message(peer_id, text):
    """Отправка сообщения пользователю"""
    try:
        vk.messages.send(peer_id=peer_id, message=text, random_id=random.randint(1, 1e6))
        logging.info(f"Сообщение отправлено: {text} -> peer_id: {peer_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

def kick_user(chat_id, user_id):
    """Удаление пользователя из беседы"""
    try:
        vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
        logging.info(f"Пользователь {user_id} удалён из беседы {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя {user_id}: {e}")
def delete_user_messages(peer_id, user_id):
    """Удаление всех сообщений пользователя в указанном чате"""
    try:
        # Получаем все сообщения пользователя в чате
        all_messages = []
        offset = 0
        if peer_id < 2000000000:
                logging.warning("Удаление сообщений доступно только в беседах")
                return
                
        chat_info = vk.messages.getChat(chat_id=peer_id - 2000000000)
        if not chat_info.get('admin_id'):
            logging.error("Бот не является администратором чата")
            return
        while True:
            
            response = vk.messages.getHistory(
                peer_id=peer_id,
                user_id=user_id,
                count=200,
                offset=offset,
                rev=0 
            )
            messages = response.get('items', [])
            if not messages:
                break
                
            all_messages.extend(messages)
            offset += len(messages)
            time.sleep(0.3)  
        message_ids = [msg['id'] for msg in all_messages if msg['from_id'] == user_id]
        
        for i in range(0, len(message_ids), 100):
            batch = message_ids[i:i+100]
            vk.messages.delete(
                message_ids=','.join(map(str, batch)),
                delete_for_all=1,
                spam=0
            )
            logging.info(f"Удалено {len(batch)} сообщений от {user_id}")
            time.sleep(0.5)

    except Exception as e:
        logging.error(f"Ошибка при удалении сообщений: {e}")

def handle_new_member(event):
    """Обработка нового участника группы или чата"""
    try:
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.get("message", {})
            action = message.get("action", {})
            if action.get("type") in ["chat_invite_user", "chat_invite_user_by_link"]:
                user_id = action.get("member_id", message.get("from_id"))
                peer_id = message.get("peer_id")
            else:
                logging.warning("Неизвестное действие в событии MESSAGE_NEW")
                return
        elif event.type == VkBotEventType.GROUP_JOIN:
            user_id = event.object.get("user_id")
            peer_id = event.object.get("peer_id", 0)
        else:
            logging.warning("Неподдерживаемый тип события в handle_new_member")
            return

        if not user_id or not peer_id:
            logging.error(f"Некорректные user_id ({user_id}) или peer_id ({peer_id}) в событии")
            return

        logging.info(f"Обработка нового участника: user_id={user_id}, peer_id={peer_id}")

        riddle, correct_answer = random.choice(RIDDLES)
        send_message(peer_id, riddle)

        CHECKING_MEMBERS[user_id] = {
            'peer_id': peer_id,
            'correct_answer': correct_answer,
            'attempts': 0,
            'timestamp': time.time()
        }
        logging.debug(f"Добавлен пользователь в CHECKING_MEMBERS: {CHECKING_MEMBERS[user_id]}")

    except Exception as e:
        logging.error(f"Ошибка в handle_new_member: {e}")

def check_user_response(event):
    """Проверка ответа пользователя"""
    user_id = event.object.message['from_id']
    peer_id = event.object.message['peer_id']
    text = event.object.message['text']

    logging.info(f"Получен ответ от user_id={user_id}: {text}")

    if user_id not in CHECKING_MEMBERS:
        logging.debug(f"Пользователь {user_id} не в списке проверяемых")
        return

    member_info = CHECKING_MEMBERS[user_id]
    correct_answer = member_info['correct_answer']
    normalized_text = text.strip().lower()
    normalized_answer = correct_answer.strip().lower()

    logging.debug(f"Сравнение ответов: '{normalized_text}' == '{normalized_answer}'")

    if normalized_text == normalized_answer:
        send_message(peer_id, GREETING_MESSAGE)
        logging.info(f"Пользователь {user_id} дал правильный ответ")
        del CHECKING_MEMBERS[user_id]
    else:
        member_info['attempts'] += 1
        if member_info['attempts'] >= 2:
            kick_user(peer_id - 2000000000, user_id)
            send_message(peer_id, BAN_MESSAGE)
            logging.warning(f"Пользователь {user_id} заблокирован после 2 попыток")
            del CHECKING_MEMBERS[user_id]
        else:
            send_message(peer_id, "Неправильный ответ. Попробуйте снова.")
            member_info['timestamp'] = time.time()
            logging.info(f"Пользователю {user_id} предоставлена ещё одна попытка")


for event in longpoll.listen():
    try:
        logging.debug(f"Получено событие: {event}")
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.get("message", {})
            action = message.get("action", {})
            if action.get("type") == "chat_invite_user_by_link" or action.get("type") ==  "chat_invite_user":
                logging.info(f"Пользователь присоединился через ссылку: {message}")
                handle_new_member(event)
            else:
                check_user_response(event)
        elif event.type == VkBotEventType.GROUP_JOIN:
            handle_new_member(event)

        current_time = time.time()
        logging.info(f"Начинается проверка")

        for user_id in list(CHECKING_MEMBERS.keys()):
            logging.info(f"Мы дошли до проверки пользователя {user_id}")
            member_info = CHECKING_MEMBERS[user_id]
            if current_time - member_info['timestamp'] > 60:
                delete_user_messages(member_info['peer_id'], user_id)
                kick_user(member_info['peer_id'] - 2000000000, user_id)
                send_message(member_info['peer_id'], BAN_MESSAGE)
                logging.warning(f"Пользователь {user_id} удалён за истечение времени")
                del CHECKING_MEMBERS[user_id]
    except Exception as e:
        logging.error(f"Ошибка в основном цикле: {e}")
