# Dockerfile

# base image with Python 3.10
FROM python:3.10

# create & set working directory
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/data
RUN mkdir -p /usr/src/app/logs
WORKDIR /usr/src/app

# copy source files
COPY ./*.py /usr/src/app
COPY ./pages /usr/src/app/pages
COPY ./assets /usr/src/app/assets
COPY ./requirements.txt /usr/src/app
COPY ./.env /usr/src/app

# install dependencies
RUN cd /usr/src/app
RUN pip install -r requirements.txt

# start app
CMD ["python3", "index.py"]
