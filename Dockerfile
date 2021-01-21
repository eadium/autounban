FROM ubuntu:20.04

ENV WORK /opt/autounban
WORKDIR $WORK

ENV DEBIAN_FRONTEND 'noninteractive'
RUN echo 'Europe/Moscow' > '/etc/timezone'

RUN apt-get -y update
RUN apt-get -y install curl wget python3-pip ssh 

ADD ./requirements.txt $WORK/
RUN pip3 install -r /opt/autounban/requirements.txt

ADD . $WORK/

EXPOSE 8000

CMD python3 /opt/autounban/autounban/manage.py runserver --insecure 0.0.0.0:8000
