FROM python:3.11.8-slim-bookworm
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install gunicorn --upgrade
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()", "--workers", "4"]
