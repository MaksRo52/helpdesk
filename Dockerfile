FROM python
COPY pyproject.toml ./
RUN pip install poetry && poetry install --only main --no-root --no-directory
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*
COPY . .