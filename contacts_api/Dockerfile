FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "contacts_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
