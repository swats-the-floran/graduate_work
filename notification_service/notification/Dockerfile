FROM python:3.9-alpine3.15

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev

COPY ./requirements.txt /app
RUN python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./app/ .

RUN addgroup -S web && adduser -S web -G web \
    && chown web:web -R /app
USER web

ENTRYPOINT ["/app/entrypoint.sh"]