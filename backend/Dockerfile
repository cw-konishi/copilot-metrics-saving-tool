FROM python:3.13-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

WORKDIR /app

COPY requirements.txt requirements.txt

#ENV http_proxy=${HTTP_PROXY}
#ENV https_proxy=${HTTPS_PROXY}
#ENV no_proxy=${NO_PROXY}
#ENV HTTP_PROXY=${HTTP_PROXY}
#ENV HTTPS_PROXY=${HTTPS_PROXY}
#ENV NO_PROXY=${NO_PROXY}

RUN apt-get update && apt-get install -y \
    postgresql-server-dev-all \
    libyaml-dev \
    cython3 \
    build-essential \
    python3-dev 

#RUN pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install -r requirements.txt
RUN pip install -r requirements.txt
COPY app app
COPY config.yaml config.yaml
COPY main.py main.py

CMD ["python", "-m", "main"]