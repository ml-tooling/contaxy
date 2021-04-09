FROM ubuntu:20.04

# Install python3 and pip
RUN \
    apt-get update \
    && apt-get install -y python3.8 python3-pip \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip

# Install gunicorn and uvicorn to run FastAPI optimized
# RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn fastapi faker

# Install Contaxy
# TODO: copy contaxy into this directory to build the image
RUN pip install .

RUN \
    mkdir /resources

COPY src/ /resources/app

COPY ./docker/entrypoint.sh /resources/entrypoint.sh
RUN chmod +x /resources/entrypoint.sh


ENTRYPOINT ["/bin/bash"]
CMD ["/resources/entrypoint.sh"]
