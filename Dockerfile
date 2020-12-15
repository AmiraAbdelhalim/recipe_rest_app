FROM python:3.7-alpine

#doesn't allow python to buffer the output
ENV PYTHONUNBUFFERED 1

#copy the project requirements into the docker image
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#create empty dir in docker image
RUN mkdir /app
#switch to it and make it the default dir
WORKDIR /app
#copy from local machine app dir to our image
COPY ./app /app

#create a user to run the application only for security purpose
#if not specified the docker uses by default root user
RUN adduser -D user
USER user