.PHONY: install setup clean

install:
	pip3 install -r requirements.txt

setup:
	@echo "Остановка и удаление старого сервиса..."
	@-sudo systemctl stop vk-spambot 2>/dev/null || true
	@-sudo systemctl disable vk-spambot 2>/dev/null || true
	@-sudo userdel -r spambot 2>/dev/null || true
	
	@echo "Копирование файлов..."
	sudo mkdir -p /opt/vk-spambot
	sudo cp -r . /opt/vk-spambot
	sudo chown -R spambot:spambot /opt/vk-spambot
	
	@echo "Настройка сервиса..."
	sudo cp deploy/vk-spambot.service /etc/systemd/system/
	sudo cp deploy/vk-spambot.conf /etc/default/
	sudo useradd -r -s /bin/false spambot
	sudo systemctl daemon-reload
	sudo systemctl enable vk-spambot
	@echo "Сервис установлен. Запустите: sudo systemctl start vk-spambot"

clean:
	@-sudo systemctl stop vk-spambot 2>/dev/null || true
	sudo rm -rf /opt/vk-spambot
	sudo rm -f /etc/systemd/system/vk-spambot.service
	sudo rm -f /etc/default/vk-spambot
	@-sudo userdel -r spambot 2>/dev/null || true
	@echo "Очистка завершена" 