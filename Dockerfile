FROM bitnami/minideb:latest

ENV PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/bot:/config:/static \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update

#all in a shot
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
        python3 \
        python3-pip \
        ffmpeg \
        tesseract-ocr \
        python3-opencv \
        tesseract-ocr-spa \
        tesseract-ocr-ara \
        tesseract-ocr-eng \
        tesseract-ocr-jpn \
        tesseract-ocr-jpn-vert \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-sim-vert \
        tesseract-ocr-chi-tra \
        tesseract-ocr-chi-tra-vert \
        tesseract-ocr-deu \
        tesseract-ocr-fra \
        tesseract-ocr-rus \
        tesseract-ocr-por \
        tesseract-ocr-ita \
        tesseract-ocr-nld && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY bot/ /bot
COPY static/ /static
COPY requirements.txt /requirements.txt
COPY config/api.example.yml config/api.yml
COPY config/chat_mode.example.yml config/chat_mode.yml
COPY config/model.example.yml config/model.yml
COPY config/lang.yml config/lang.yml
COPY config/openai_completion_options.example.yml config/openai_completion_options.yml

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "bot"]
