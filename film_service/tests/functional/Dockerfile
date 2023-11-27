FROM python:3.10

WORKDIR /app/tests/functional/

ENV PYTHONPATH=/app/

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY settings.py conftest.py entry.sh __init__.py ./
COPY src src
COPY testdata testdata
COPY utils utils

ENTRYPOINT [ "bash", "entry.sh" ]
