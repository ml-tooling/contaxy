FROM ubuntu:20.04

# Install python3 and pip
RUN \
    apt-get update \
    && apt-get install -y python3.8 python3-pip \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip

# Install lib required for psycopg2
RUN \
  apt-get update \
  && apt-get install -y libpq-dev

# Install gunicorn and uvicorn to run FastAPI optimized
RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn fastapi faker

RUN \
    mkdir /resources

# Install Contaxy
COPY docker/contaxy /resources/contaxy
WORKDIR /resources/contaxy
RUN pip install .

COPY src/ /resources/app

COPY ./docker/entrypoint.sh /resources/entrypoint.sh
RUN chmod +x /resources/entrypoint.sh

WORKDIR /resources/app

ENTRYPOINT ["/bin/bash"]
CMD ["/resources/entrypoint.sh"]
