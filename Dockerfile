FROM bitnami/minideb:latest

#por alguna razon si se elimina esta variable, no se imprimen algunos mensajes de error o informacion relevante...
ENV PYTHONUNBUFFERED=1

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
COPY config/api.example.json config/api.json
COPY config/chat_mode.example.json config/chat_mode.json
COPY config/model.example.json config/model.json
COPY config/locales/ /config/locales
COPY config/props.json config/props.json
COPY config/openai_completion_options.example.json config/openai_completion_options.json

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["python3", "-m", "bot"]
#