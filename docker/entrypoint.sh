

# Create / copy certificates (has to be done here as the setup container in Kubernetes mode setups the ssl certificate)
if [[ "${SERVICE_SSL_ENABLED}" == true ]]; then
    /resources/setup-certs.sh;
fi

# ${LAB_ACTION,,} is the lower-cased LAB_ACTION variable
if [[ "${LAB_ACTION,,}" != serve ]]; then
    # TODO: run the setup script / container
    echo "";
fi

# Configure variables in nginx
lab_namespace=${LAB_NAMESPACE}
lab_base_url=${LAB_BASE_URL}
service_suffix="''"
resolver=127.0.0.11
if [[ "${SERVICES_RUNTIME,,}" == k8s || "${SERVICES_RUNTIME,,}" == kubernetes ]]; then
    service_suffix="${cat /var/run/secrets/kubernetes.io/serviceaccount/namespace}.svc.cluster.local";
    resolver="kube-dns.kube-system.svc.cluster.local valid=10s"
fi
sed -s -i "s/\${LAB_NAMESPACE}/${lab_namespace}/g" /etc/nginx/*.conf;
sed -s -i "s/\${LAB_BASE_URL}/${lab_base_url}/g" /etc/nginx/*.conf;
sed -s -i "s@\${SERVICE_SUFFIX}@${service_suffix}@g" /etc/nginx/*.conf;
sed -s -i "s/\${RESOLVER}/${resolver}/g" /etc/nginx/*.conf;

# Configure SSL variables in nginx
# When SSL is enabled, the Stream port is used as the entry port and for the main port ssl is enabled (the stream port forwards https to the ssl-enabled main port and ssh traffic to the OpenSSH server). In this case, switch the ports so that the user does not have to consider this.
main_port=8091
stream_port=8092
if [[ "${SERVICE_SSL_ENABLED,,}" == true ]]; then
    temp=$stream_port
    stream_port=$main_port
    main_port="$temp; ssl"

    sed -i "s/# ssl_certificate \${SSL_CERTIFICATE_PATH}/${_SSL_PATH}/cert.crt/g" /etc/nginx/nginx.conf;
    sed -i "s/# ssl_certificate_key \${SSL_CERTIFICATE_KEY_PATH}/${_SSL_PATH}/cert.key/g" /etc/nginx/nginx.conf;
fi
sed -i "s/\${MAIN_PORT}/$main_port/g" /etc/nginx/nginx.conf;
sed -i "s/\${STREAM_PORT}/$stream_port/g" /etc/nginx/nginx.conf;

# Start nginx
nginx -c /etc/nginx/nginx.conf

export PORT=8090
# Start the backend server
/resources/start.sh