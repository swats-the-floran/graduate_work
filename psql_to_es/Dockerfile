FROM --platform=linux/amd64 python:3.11-buster

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GID=etl-pipeline \
    UID=etl-pipeline

COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip \
    && pip install pipenv==2023.6.2 \
    && pipenv install --system --deploy

COPY . .

RUN groupadd -r ${GID} \
    && useradd -d /home/${UID} -r -g ${GID} ${UID} \
    && chown ${UID}:${UID} -R /opt

USER ${UID}

ENTRYPOINT ["python", "etl.py"]