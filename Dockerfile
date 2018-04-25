# Dockerfile for Parasol monitoring scripts

FROM ubuntu:xenial

RUN apt-get update
RUN apt-get -y install python python-pip

RUN pip install pip --upgrade
RUN pip install prometheus_client

RUN mkdir /parasol-monitoring

ADD parasol_monitoring/deps /parasol-monitoring/deps/
ADD parasol_monitoring/export_sunny.py /parasol-monitoring/

EXPOSE 9100/tcp

CMD python /parasol-monitoring/export_sunny.py --webbox_address $WEBBOX_ADDRESS --listen_port 9100
