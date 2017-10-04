FROM python:3.6

COPY . /slack/bot/

RUN pip install slackclient

EXPOSE 80

CMD ["python", "/slack/bot/ichibot.py"]
