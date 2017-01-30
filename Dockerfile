FROM ubuntu:16.04


# Install dependencies
RUN apt-get install -y build-essential wget git
RUN apt-get install -y python3-pip python3-cffi

# Get newest pip and setuptools version
RUN pip3 install -U pip setuptools

RUN git clone https://github.com/smartshark/mailingSHARK /root/mailingshark