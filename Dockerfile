FROM python:buster

COPY / .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app

CMD ["python", "-u", "main.py"]