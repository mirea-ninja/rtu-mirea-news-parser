FROM python:buster

WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5050

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050"]