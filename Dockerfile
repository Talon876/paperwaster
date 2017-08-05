FROM python:2.7-alpine
MAINTAINER talondaniels@gmail.com

ENV INSTALL_PATH /pw
WORKDIR $INSTALL_PATH

RUN apk update && apk add build-base python-dev jpeg-dev zlib-dev

COPY requirements-web.txt requirements-web.txt
RUN pip install -r requirements-web.txt

COPY . .
RUN pip install -e .

CMD gunicorn -b 0.0.0.0:5000 --access-logfile - "paperwaster.web.app:create_app('config.yaml')"
