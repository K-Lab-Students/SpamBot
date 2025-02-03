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

## Установка и настройка ⚙️

### Требования
- Python 3.9+
- Systemd (для сервиса)
- Nano или другой текстовый редактор

### Быстрый старт
```bash
# Клонирование репозитория
git clone https://github.com/K-Lab-Students/SpamBot.git
cd SpamBot

# Создание виртуального окружения и установка зависимостей
make venv install

# Настройка конфигурации (откроется редактор nano)
make configure

# Установка и запуск сервиса
sudo make setup
sudo systemctl start vk-spambot
```

### Конфигурация .env
Файл настроек автоматически создается при выполнении:
```bash
make configure
```

Пример содержимого:
```ini
GROUP_TOKEN=ваш_токен_группы
GROUP_ID=id_вашей_группы
RIDDLES=[["Сколько ног у паука?", "8"], ["Столица России?", "Москва"]]
GREETING_MESSAGE="Добро пожаловать!"
BAN_MESSAGE="Вы забанены!"
MAX_ATTEMPTS=2
WAIT_TIME=300
```

### Управление сервисом
```bash
# Запуск/остановка
sudo systemctl start vk-spambot
sudo systemctl stop vk-spambot

# Просмотр логов
journalctl -u vk-spambot -f

# Перезагрузка после изменений
sudo systemctl restart vk-spambot
```

### Обновление версии
```bash
git pull origin main
sudo make setup
sudo systemctl restart vk-spambot
```

### Очистка
```bash
# Полное удаление сервиса и временных файлов
sudo make clean
```

## Структура проекта 🗃️
```
.
├── bot/                 # Исходный код бота
├── deploy/              # Конфигурации для развертывания
├── venv/                # Виртуальное окружение (автосоздается)
├── Makefile             # Управление проектом
└── requirements.txt     # Зависимости Python
```

## Зависимости

- python-dotenv
- vk-api
- requests

## Лицензия

MIT License
