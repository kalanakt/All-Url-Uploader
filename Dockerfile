FROM python:3.9

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install ffmpeg -y
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR .
COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py"]
