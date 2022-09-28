FROM python:3.9-slim
WORKDIR /usr/src/app

#RUN pip3 install --upgrade --no-cache-dir Flask
#RUN pip3 install --upgrade --no-cache-dir gunicorn
#RUN pip3 install --upgrade --no-cache-dir mariadb
RUN pip3 install --upgrade --no-cache-dir google-auth-httplib2
RUN pip3 install --upgrade --no-cache-dir google-auth-oauthlib
RUN pip3 install --upgrade --no-cache-dir google-api-python-client
RUN pip3 install --upgrade --no-cache-dir apscheduler

ENV PYTHONUNBUFFERED=1
ENV TZ="Europe/Luxembourg"

WORKDIR /deploy/app

COPY ./app /deploy/app
CMD ["python", "/deploy/app/app.py"]