FROM python:3.11

WORKDIR /usr/app/

COPY ./app.py .
COPY ./db.py .
COPY ./kong.py .
COPY ./requirements.txt .

# Install Dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN wget -O /bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /bin/wait-for-it.sh

EXPOSE 5000

CMD [ "python","app.py" ]
