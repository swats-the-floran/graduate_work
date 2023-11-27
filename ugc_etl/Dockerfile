FROM python:3.10

WORKDIR /etl

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY etl.py etl.py

ENTRYPOINT ["python", "etl.py"]

