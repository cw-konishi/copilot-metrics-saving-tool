FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY config.yaml config.yaml

CMD ["python", "app/main.py"]