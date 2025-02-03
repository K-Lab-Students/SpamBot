.PHONY: install deploy setup clean

# Установка зависимостей
install:
    pip install -r requirements.txt

# Деплой на сервер
deploy:
    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "sudo systemctl stop vk-spambot"
    rsync -avz --exclude='.git' --exclude='.env' ./ ${DEPLOY_USER}@${DEPLOY_HOST}:/opt/vk-spambot/
    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "sudo systemctl start vk-spambot"

# Первоначальная настройка сервиса
setup:
    sudo cp deploy/vk-spambot.service /etc/systemd/system/
    sudo cp deploy/vk-spambot.conf /etc/default/
    sudo useradd -r -s /bin/false spambot
    sudo systemctl daemon-reload
    sudo systemctl enable vk-spambot

# Очистка
clean:
    sudo systemctl stop vk-spambot
    sudo rm -rf /opt/vk-spambot
    sudo rm /etc/systemd/system/vk-spambot.service
    sudo rm /etc/default/vk-spambot
    sudo userdel spambot 