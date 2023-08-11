FROM python:alpine3.18
COPY .  /root
WORKDIR /root
RUN python3 -m pip install --upgrade pip  && pip3 install aiohttp && apk add --update openssl &&  pip install -r requirements.txt
ENTRYPOINT ["python3", "main.py"]