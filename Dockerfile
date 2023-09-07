FROM python:3.10
LABEL authors="artem.troshkin"

COPY requirements.txt /code/

WORKDIR /code/

RUN pip install --no-cache-dir -r requirements.txt && apt-get update -y

COPY . /code/

CMD ["python", "main.py"]