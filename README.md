# SpamBot

Бот для проверки сообщений на спам в сообществах ВКонтакте.

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

## Production Deployment 🚀

### Server Requirements
- Ubuntu 22.04 LTS
- Python 3.9+
- 512MB RAM minimum

### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/yourusername/vk-spambot.git
cd SpamBot

# 2. Install dependencies
make install

# 3. Setup system service
sudo make setup

# 4. Deploy to production
make deploy DEPLOY_USER=user DEPLOY_HOST=your.server.com
```

### Service Management
```bash
# Start/Stop
sudo systemctl start vk-spambot
sudo systemctl stop vk-spambot

# View logs
journalctl -u vk-spambot -f

# Update config
sudo nano /etc/default/vk-spambot
sudo systemctl restart vk-spambot
```
