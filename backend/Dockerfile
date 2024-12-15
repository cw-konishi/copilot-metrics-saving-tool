FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y \
    postgresql-server-dev-all \
    libyaml-dev \
    cython3 \
    build-essential \
    python3-dev 

RUN pip install -r requirements.txt

COPY app app
COPY config.yaml config.yaml
COPY main.py main.py

CMD ["python", "-m", "main"]