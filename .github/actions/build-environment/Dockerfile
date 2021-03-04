FROM mltooling/build-environment:0.6.9

# Install Java
ENV JAVA_HOME="/usr/lib/jvm/java-1.14.0-openjdk-amd64"
RUN \
    add-apt-repository ppa:openjdk-r/ppa \
    && apt-get update \
    && apt-get install -y openjdk-14-jdk \
    && dpkg-query -l

# Install kind for Kubernetes testing
RUN \
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.9.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && mv ./kind /usr/bin/kind
COPY kind-config.yaml /kind-config.yaml

COPY extended-entrypoint.sh /extended-entrypoint.sh

RUN chmod +x /extended-entrypoint.sh

ENTRYPOINT ["/tini", "-g", "--", "/extended-entrypoint.sh"]
