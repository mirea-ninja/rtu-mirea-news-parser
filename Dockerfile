FROM python:buster

COPY / .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Spacy model
RUN python -m spacy download ru_core_news_md

WORKDIR /app

CMD ["python", "-u", "main.py"]