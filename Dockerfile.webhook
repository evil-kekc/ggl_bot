FROM python:3.10-slim-buster
LABEL authors="artem.troshkin"
WORKDIR /code/
COPY requirements.txt /code/
COPY . /code/

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update -y && \
    alembic upgrade head

EXPOSE 5000
CMD ["python", "main.py"]