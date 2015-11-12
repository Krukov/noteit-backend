FROM python:3.5
ENV PYTHONUNBUFFERED 1
VOLUME ["/code"]
WORKDIR /code


ADD requirements/ /tmp
RUN pip install --upgrade pip && \
    pip install -r /tmp/prod.txt && \
    rm -rf /tmp/*
