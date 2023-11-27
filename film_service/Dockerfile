FROM python:3.10 as base

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GID=fast-api \
    UID=fast-api

COPY Pipfile Pipfile.lock ./

FROM base as dependencies
RUN pip install --upgrade pip \
    && pip install pipenv==2023.6.2 \
    && pipenv install --system --deploy

FROM dependencies as development
RUN pipenv install --dev --system --deploy
COPY /src .
EXPOSE 8888
RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt
USER ${UID}
ENTRYPOINT [ "uvicorn", "main:app" ,"--host",  "0.0.0.0", "--port",  "8888" ]


FROM dependencies as production
COPY /src .
EXPOSE 8888
RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt
USER ${UID}
ENTRYPOINT [ "gunicorn", "main:app" ,"--bind",  "0.0.0.0:8888", "-w", "4", "-k", "uvicorn.workers.UvicornWorker" ]
