wget --header="Authorization: Bearer $CONTAXY_API_TOKEN" $CONTAXY_API_ENDPOINT/projects/$CONTAXY_PROJECT_ID/files/$OPYRATOR_FILE:download -O /resources/opyrator-app.py
cd /resources
opyrator launch-ui opyrator-app:call --port 8080
