FROM ubuntu:20.04

# Install python3 and pip
RUN \
    apt-get update \
    && apt-get install -y python3.8 python3-pip \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip

RUN \
    apt-get update \
    && apt-get install -y wget

RUN \
    pip install opyrator

COPY entrypoint.sh /resources/entrypoint.sh

ENTRYPOINT ["/bin/bash"]
CMD ["/resources/entrypoint.sh"]
