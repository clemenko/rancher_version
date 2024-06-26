FROM alpine
RUN apk -U upgrade && apk add --no-cache py3-pip curl  &&\
    pip3 install --no-cache-dir --upgrade pip --break-system-packages &&\
    pip3 install --no-cache-dir flask requests --break-system-packages &&\
    rm -rf /var/cache/apk/*

WORKDIR /code
ADD . /code
EXPOSE 5000

CMD ["python3", "app.py"]
