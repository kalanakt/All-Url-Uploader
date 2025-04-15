FROM python:3.9

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install ffmpeg -y

WORKDIR .
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
