FROM python:latest
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt 
RUN python -m spacy download en_core_web_sm
EXPOSE 8000
CMD [ "python", "/app/app.py" ]
