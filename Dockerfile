FROM python:3 as builder
WORKDIR /app
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-dev # Установка без зависимостей для разработки