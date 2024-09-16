# Extend python image
FROM python:3.8.5

# Default ingress port to 5000
EXPOSE 5000

# Set working dir in container
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
COPY . .
CMD [ "python", "./app.py" ]