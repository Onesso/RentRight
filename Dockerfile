FROM python:3.9-alpine3.13
LABEL maintainer="https://onesso.github.io/frankwere.github.io/"

ENV PYTHONUNBUFFERED=1


COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

#the line below is supposed to be add during this commit
ARG DEV=false 
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    #adding dependencies that will be used to install the pycopg2 package(adaptor)
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    #---end
    /py/bin/pip install -r /tmp/requirements.txt && \
    #running a shell condtion at this point of commit 
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    #this is the end of the condition
    rm -rf /tmp && \
    apk del .tmp-build-deps && \ 
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

        
ENV PATH="/py/bin:$PATH"

USER django-user