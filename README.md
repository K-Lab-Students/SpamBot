# VK AntiSpam Bot 🔒

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Бот для автоматической модерации сообществ ВКонтакте с системой проверки новых участников через загадки.

## Особенности ✨
- Защита от ботов с помощью капчи-загадок
- Автоматический бан при превышении лимита попыток
- Гибкая система конфигурации через `.env`
- Логирование всех действий
- Поддержка нескольких типов событий (вступление в группу, сообщения)

## Установка ⚙️

```bash
git clone https://github.com/K-Lab-Students/SpamBot.git
cd SpamBot
make install
sudo make setup
```

### Основные команды
```bash
# Запуск
sudo systemctl start vk-spambot

# Проверка статуса
sudo systemctl status vk-spambot

# Просмотр логов
journalctl -u vk-spambot -f

### Обновление
```bash
git pull origin main
sudo systemctl restart vk-spambot
```

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Создайте файл `.env` и добавьте в него:
   ```
    VK_TOKEN=ваш_токен_вк
    GROUP_ID=id_группы
    RIDDLES=[["загадка 1", "ответ 1"], ["загадка 2", "ответ 2"]]
    GREETING_MESSAGE="текст приветствия"
    BAN_MESSAGE="текст бана"
    MAX_ATTEMPTS=количество попыток ответа
    WAIT_TIME=время ожидания в секундах
   ```

## Использование

1. Запустите бота: `python main.py`
2. Бот будет автоматически проверять новые сообщения в сообществе на наличие спама

## Зависимости

- python-dotenv
- vk-api
- requests

## Лицензия

MIT License
