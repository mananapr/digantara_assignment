FROM python:3.11.9-alpine3.19
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev && pip install psycopg2 && mkdir /digantara
WORKDIR /digantara
COPY 1_init.py .
COPY 2_sql_query.py .
COPY start.sh .
CMD ./start.sh
