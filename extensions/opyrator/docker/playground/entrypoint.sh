appfile="/resources/opyrator-app.py"
if [[ ! -z "$OPYRATOR_FILE_KEY" ]]; then
    wget --header="Authorization: Bearer $CONTAXY_API_TOKEN" $CONTAXY_API_ENDPOINT/projects/$CONTAXY_PROJECT_ID/files/$OPYRATOR_FILE:download -O $appfile
elif [[ ! -z "$OPYRATOR_FILE_DATA" ]]; then
    echo $OPYRATOR_FILE_DATA | base64 --decode > $appfile
else
    echo "No Opyrator file provided"
    exit
fi

cd /resources
opyrator launch-ui opyrator-app:call --port 8080
