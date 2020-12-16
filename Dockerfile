FROM python:3.7-alpine

#doesn't allow python to buffer the output
ENV PYTHONUNBUFFERED 1

#copy the project requirements into the docker image
COPY ./requirements.txt /requirements.txt
#add some postgres requirements before installing requirements
#--no-cache option for not to add many files and dependencies in the dockerfile
RUN apk add --update --no-cache postgresql-client
# --virtual , adds an alias (tmp-build-deps) for dependencies to make it easy to remove them later
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
# deletes temperory requirements
RUN apk del .tmp-build-deps

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