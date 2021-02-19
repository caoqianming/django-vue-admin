FROM python:3.8-slim
WORKDIR /code
ADD . .
RUN apt-get update && apt-get install -y gcc libpq-dev &&\
    apt-get clean && rm -rf /var/lib/apt/lists/* &&\
    pip install supervisor &&\
    pip install -r ./requirements.txt
EXPOSE 80
ENTRYPOINT ["/bin/bash","-C","/code/start.sh"]