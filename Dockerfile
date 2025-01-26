FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r req.txt

COPY . /app/

WORKDIR /app/bot/vk_apis

CMD ["python", "bot.py"]
