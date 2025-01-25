# telegram_bot/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy your requirements for the telegram bot
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy your bot code into the image
COPY telegram_bot.py /app/

CMD ["python", "telegram_bot.py"]

