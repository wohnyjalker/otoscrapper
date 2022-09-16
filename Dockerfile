FROM python:3.10.7-slim-buster

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    mkdir /server

COPY . /server

ENTRYPOINT ["python", "-u", "/server/server.py"]
