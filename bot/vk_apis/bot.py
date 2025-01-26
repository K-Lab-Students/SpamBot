import os
import random
import time
import logging
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from threading import Thread
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
MAX_ATTEMPTS = os.getenv('MAX_ATTEMPTS')
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


def is_conversation_admin(vk, peer_id, user_id):
    """Проверяет, является ли пользователь администратором беседы."""
    try:
        response = vk.messages.getConversationMembers(peer_id=peer_id)
        for member in response.get("items", []):
            if member.get("member_id") == user_id:
                return member.get("is_admin", False)
    except vk_api.exceptions.ApiError as e:
        logging.error(f"Ошибка при проверке администратора: {e}")
    return False

def delete_message(vk, peer_id, user_id, message_id):
    """Удалить сообщение, если пользователь не админ."""
    is_admin = is_conversation_admin(vk, peer_id, user_id)
    logging.debug(
        f"Проверка пользователя {user_id} на администратора в беседе {peer_id}: {is_admin}"
    )
    if not is_admin:
        try:
            vk.messages.delete(
                cmids=message_id,  # conversation_message_id
                peer_id=peer_id,
                delete_for_all=1
            )
            logging.info(
                f"Сообщение (ID: {message_id}) удалено из беседы {peer_id} "
                f"пользователем {user_id}."
            )
        except vk_api.exceptions.ApiError as e:
            logging.error(
                f"Не удалось удалить сообщение (ID: {message_id}) в беседе {peer_id}: {e}",
                exc_info=True
            )
    else:
        logging.debug(
            f"Сообщение (ID: {message_id}) не удалено, так как пользователь {user_id} "
            f"является администратором."
        )

def get_bot_user_id():
    try:
        group_info = vk.groups.getById()
        if group_info:
            group_id = group_info[0]['id']
            bot_user_id = -group_id
            return bot_user_id
        else:
            print("Не удалось получить информацию о группе.")
            return None
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при получении информации о группе: {e}")
        return None
    

def delete_user_messages(peer_id, user_id):
    """Удаление сообщений пользователя и бота за последний час в указанном чате."""
    try:
        bot_id = get_bot_user_id()
        if peer_id < 2000000000:
            logging.warning("Удаление сообщений доступно только в беседах")
            return

        # Проверяем, что бот является администратором беседы
        chat_info = vk.messages.getChat(chat_id=peer_id - 2000000000)
        if not chat_info.get('admin_id'):
            logging.error("Бот не является администратором чата")
            return

        # Получаем timestamp за последний час
        current_time = int(time.time())
        one_hour_ago = current_time - 3600

        offset = 0
        all_messages = []

        while True:
            response = vk.messages.getHistory(
                peer_id=peer_id,
                count=200,
                offset=offset,
                rev=0  # Сортировка от новых к старым
            )
            messages = response.get('items', [])
            if not messages:
                break

            for msg in messages:
                if msg['date'] >= one_hour_ago and (msg['from_id'] == user_id or msg['from_id'] == bot_id):
                    all_messages.append(msg)

            offset += len(messages)
            time.sleep(0.3)  # Задержка для предотвращения блокировки API

        for msg in all_messages:
            delete_message(vk, peer_id, msg['from_id'], msg['conversation_message_id'])

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
        # ГОВНО код
        riddle, correct_answer = random.choice(RIDDLES)
        send_message(peer_id, riddle)
        time.sleep(0.3)

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
        if member_info['attempts'] >= MAX_ATTEMPTS:
            kick_user(peer_id - 2000000000, user_id)
            delete_user_messages(peer_id, member_info['attempts'])
            send_message(peer_id, BAN_MESSAGE)
            logging.warning(f"Пользователь {user_id} заблокирован после 2 попыток")
            del CHECKING_MEMBERS[user_id]
        else:
            send_message(peer_id, f"Неправильный ответ. Попробуйте снова. Осталось попыток {MAX_ATTEMPTS - member_info['attempts']}")
            member_info['timestamp'] = time.time()
            logging.info(f"Пользователю {user_id} предоставлена ещё одна попытка")

def moderation_task():
    """Периодическая проверка участников из CHECKING_MEMBERS."""
    while True:
        try:
            current_time = time.time()
            for user_id in list(CHECKING_MEMBERS.keys()):
                logging.info(f"Проверка пользователя {user_id}")
                member_info = CHECKING_MEMBERS[user_id]
                if current_time - member_info['timestamp'] > 60:
                    delete_user_messages(member_info['peer_id'], user_id)
                    kick_user(member_info['peer_id'] - 2000000000, user_id)
                    send_message(member_info['peer_id'], BAN_MESSAGE)
                    logging.warning(f"Пользователь {user_id} удалён за истечение времени")
                    del CHECKING_MEMBERS[user_id]

        except Exception as e:
            logging.error(f"Ошибка в процессе модерации: {e}")
        time.sleep(5)  

def main():

    Thread(target=moderation_task, daemon=True).start()

    for event in longpoll.listen():
        try:
            logging.debug(f"Получено событие: {event}")

            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object.get("message", {})
                action = message.get("action", {})
                if action.get("type") in ["chat_invite_user_by_link", "chat_invite_user"]:
                    logging.info(f"Пользователь присоединился через ссылку: {message}")
                    handle_new_member(event)
                else:
                    check_user_response(event)

            elif event.type == VkBotEventType.GROUP_JOIN:
                handle_new_member(event)

        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")


if __name__ == "__main__":
    main()