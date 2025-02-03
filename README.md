# SpamBot

Бот для проверки сообщений на спам в сообществах ВКонтакте.

## Управление сервисом 🛠️

### Установка
```bash
# Клонируем репозиторий
git clone https://github.com/yourusername/vk-spambot.git
cd vk-spambot

# Установка зависимостей и сервиса
make install
sudo make setup
```

### Основные команды
```bash
# Запуск
sudo systemctl start vk-spambot

# Остановка
sudo systemctl stop vk-spambot

# Статус
sudo systemctl status vk-spambot

# Логи
journalctl -u vk-spambot -f
```

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
