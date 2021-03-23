FROM python:3.8-slim-buster

WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY src/DataGenerator.py DataGenerator.py

RUN pip3 install pipenv
RUN pipenv install --system --deploy

CMD ["python3", "DataGenerator.py"]