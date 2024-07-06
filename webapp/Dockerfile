# Используем образ Python slim в качестве базы
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .

RUN pip install -r requirements.txt


# Копируем app.py в контейнер
COPY . .
# Команда для запуска приложения
CMD ["python", "app.py"]
