FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь код приложения
COPY src/. /code/src/.
COPY .env /code/.env

# Копируем данные и модели
COPY data/. /code/data/.
COPY models/. /code/models/.

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["fastapi", "run", "src/main.py", "--port", "8000", "--workers", "1"]
