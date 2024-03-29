# Dockerfile for Parasol monitoring scripts

FROM ubuntu:xenial

RUN apt-get update
RUN apt-get -y install python python-pip

RUN pip install pip --upgrade
RUN pip install prometheus_client numpy minimalmodbus pymodbus six

ADD parasol_monitoring /parasol_monitoring_install/parasol_monitoring
ADD setup.py /parasol_monitoring_install/

#RUN pip install -e /parasol_monitoring
RUN bash -c 'cd /parasol_monitoring_install && python setup.py install'
