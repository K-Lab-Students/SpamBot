.PHONY: install setup clean

install:
	pip install -r requirements.txt

setup:
	sudo cp deploy/vk-spambot.service /etc/systemd/system/
	sudo cp deploy/vk-spambot.conf /etc/default/
	sudo useradd -r -s /bin/false spambot
	sudo systemctl daemon-reload
	sudo systemctl enable vk-spambot

clean:
	sudo systemctl stop vk-spambot
	sudo rm -rf /opt/vk-spambot
	sudo rm /etc/systemd/system/vk-spambot.service
	sudo rm /etc/default/vk-spambot
	sudo userdel spambot 