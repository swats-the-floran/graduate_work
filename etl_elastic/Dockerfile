FROM python:3.10 as base

WORKDIR /opt/src

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GID=auth-service \
    UID=auth-service

COPY pyproject.toml poetry.lock ./

RUN apt update -y \
    && apt upgrade -y \
    && apt install -y \
    netcat-traditional


RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY src .

EXPOSE 8080

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "bash", "entrypoint.sh" ]


