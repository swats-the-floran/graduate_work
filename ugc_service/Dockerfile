FROM python:3.11 as base

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GID=fast-api \
    UID=fast-api

COPY requirements.txt ./

FROM base as dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

FROM dependencies as development
COPY /src .
EXPOSE 8889
RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt
USER ${UID}
ENTRYPOINT [ "uvicorn", "main:app" ,"--host",  "0.0.0.0", "--port",  "8889" ]


FROM dependencies as production
COPY /src .
EXPOSE 8889
RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt
USER ${UID}
# ENTRYPOINT [ "sleep", "10000" ]
ENTRYPOINT [ "uvicorn", "main:app" ,"--host",  "0.0.0.0", "--port",  "8889" ]
# ENTRYPOINT [ "gunicorn", "main:app" ,"--bind",  "0.0.0.0:8889", "-w", "4", "-k", "uvicorn.workers.UvicornWorker" ]
