FROM python:3.11.6-alpine3.18

# Por alguna razón, si se elimina PYTHONUNBUFFERED, no se imprimen algunos mensajes de error o información relevante...
ENV PYTHONUNBUFFERED=1

WORKDIR /

RUN mkdir -p /database

COPY bot/ /bot
COPY static/ /static
COPY requirements.txt /requirements.txt
COPY config/api.example.json config/api.json
COPY config/chat_mode.example.json config/chat_mode.json
COPY config/model.example.json config/model.json
COPY locales/ /locales
COPY config/openai_completion_options.example.json config/openai_completion_options.json

# Instalar dependencias
RUN apk update && \
    apk add --no-cache --virtual .build-deps \
        alpine-sdk \
        python3-dev \
        py3-pip && \
    apk add --no-cache \
        sox \
        tesseract-ocr \
        tesseract-ocr-data-spa \
        tesseract-ocr-data-ara \
        tesseract-ocr-data-eng \
        tesseract-ocr-data-jpn \
        tesseract-ocr-data-chi_sim \
        tesseract-ocr-data-chi_tra \
        tesseract-ocr-data-deu \
        tesseract-ocr-data-fra \
        tesseract-ocr-data-rus \
        tesseract-ocr-data-por \
        tesseract-ocr-data-ita \
        tesseract-ocr-data-nld && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && apk del rustup && \
    rm -rf /var/cache/apk/*

CMD ["python", "-m", "bot"]
