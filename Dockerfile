FROM python:3.10.5

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev

COPY . /app
