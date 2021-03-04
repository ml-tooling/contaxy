FROM mltooling/build-environment:0.6.9

# Install Java
ENV JAVA_HOME="/usr/lib/jvm/java-1.14.0-openjdk-amd64"
RUN \
    add-apt-repository ppa:openjdk-r/ppa \
    && apt-get update \
    && apt-get install -y openjdk-14-jdk \
    && dpkg-query -l
