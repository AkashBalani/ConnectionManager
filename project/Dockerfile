FROM python:3.8

COPY /project/techtrends /app
WORKDIR /app

RUN python init_db.py
RUN pip install -r requirements.txt

EXPOSE 3111

CMD [ "python", "app.py" ]