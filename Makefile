VENV = venv
PYTHON = $(VENV)/bin/python3
SERVICE_NAME = vk-spambot

.PHONY: install venv setup clean configure

venv:
	python3 -m venv $(VENV) || (echo "Установите python3-venv: sudo apt install python3.12-venv" && exit 1)
	@echo "Виртуальное окружение создано"

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Зависимости установлены"

configure:
	@if [ ! -f "bot/vk_apis/.env" ]; then \
		echo "Создаем .env файл..."; \
		mkdir -p bot/vk_apis; \
		touch bot/vk_apis/.env; \
		nano bot/vk_apis/.env; \
	else \
		echo ".env файл уже существует"; \
	fi

setup: install configure
	@echo "Остановка старого сервиса..."
	@-sudo systemctl stop $(SERVICE_NAME) 2>/dev/null || true
	
	@echo "Копирование файлов..."
	sudo mkdir -p /opt/$(SERVICE_NAME)
	sudo cp -r . /opt/$(SERVICE_NAME)
	sudo chown -R spambot:spambot /opt/$(SERVICE_NAME)
	
	@echo "Настройка сервиса..."
	sudo cp deploy/$(SERVICE_NAME).service /etc/systemd/system/
	sudo cp deploy/$(SERVICE_NAME).conf /etc/default/
	sudo systemctl daemon-reload
	sudo systemctl enable $(SERVICE_NAME)
	@echo "Сервис установлен. Запустите: sudo systemctl start $(SERVICE_NAME)"

clean:
	@-sudo systemctl stop $(SERVICE_NAME) 2>/dev/null || true
	sudo rm -rf /opt/$(SERVICE_NAME)
	sudo rm -f /etc/systemd/system/$(SERVICE_NAME).service
	sudo rm -f /etc/default/$(SERVICE_NAME).conf
	@-sudo userdel -r spambot 2>/dev/null || true
	@-rm -rf $(VENV)
	@echo "Очистка завершена" 