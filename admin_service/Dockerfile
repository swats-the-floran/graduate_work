FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UWSGI_PROCESSES=1 \
    UWSGI_THREADS=16 \
    UWSGI_HARAKIRI=240 \
    DJANGO_SETTINGS_MODULE="config.settings" \
    GID=web-data \
    UID=web-data

RUN apt update -y \
    && apt install netcat-openbsd -y \
    && apt install gettext -y \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/app/static/ \
    && mkdir -p /opt/app/media/

COPY Pipfile* ./

RUN pip install --upgrade pip \
    && pip install pipenv==2023.6.2 \
    && pipenv install --system --deploy

COPY . .

COPY entrypoint.sh entrypoint.sh
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN chmod u+x entrypoint.sh

EXPOSE 8000

RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt

USER ${UID}

ENTRYPOINT [ "./entrypoint.sh" ]
