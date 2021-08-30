FROM python:3.8-slim-buster
COPY . /trAnalyze-api
WORKDIR /trAnalyze-api
RUN apt-get update
RUN pip install -r requirements.txt
RUN pip install uwsgi
RUN ./run_app_prod.sh