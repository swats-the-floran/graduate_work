FROM python:3.10 as base

WORKDIR /opt/src

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GID=auth-service \
    UID=auth-service

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY src .

EXPOSE 8080

RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt
USER ${UID}

ENTRYPOINT [ "bash", "entry.sh" ]
