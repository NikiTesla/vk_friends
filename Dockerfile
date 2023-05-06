FROM python:3.11.2

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN python3 manage.py makemigrations

CMD python3 manage.py migrate; python3 manage.py runserver 0.0.0.0:8000