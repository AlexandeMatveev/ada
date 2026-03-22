FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/* /app/

#COPY alembic.ini /app/
#COPY alembic /app/alembic

# Проверка установки
RUN python -c "import uvicorn; print('Uvicorn installed successfully')"

# Создаём таблицы при первом запуске
RUN alembic upgrade head || true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
