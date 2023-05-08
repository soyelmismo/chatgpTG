FROM bitnami/minideb:latest

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN install_packages python3 python3-pip
#RUN install_packages ffmpeg
WORKDIR /
ADD . /
COPY config/api.example.yml config/api.yml
COPY config/chat_mode.example.yml config/chat_mode.yml
COPY config/model.example.yml config/model.yml
RUN pip3 install -r requirements.txt
CMD ["python3", "bot/bot.py"]
