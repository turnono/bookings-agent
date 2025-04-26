include .env
export 

deploy:
	gcloud run deploy ${AGENT_SERVICE_NAME} \
	--source . \
	--region ${GOOGLE_CLOUD_LOCATION} \
	--project ${GOOGLE_CLOUD_PROJECT} \
	--allow-unauthenticated \
	--port 8080 \
	--service-account ${AGENT_SERVICE_ACCOUNT} \
	--set-env-vars="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI},GOOGLE_API_KEY=${GOOGLE_API_KEY}"

# Start the Firestore emulator in one terminal:
#   make firestore-emulator
# Then run the app in another terminal:
#   make dev
firestore-emulator:
	FIRESTORE_EMULATOR_HOST=localhost:8085 firebase emulators:start --only firestore --project ${GOOGLE_CLOUD_PROJECT}

dev:
	FIRESTORE_EMULATOR_HOST=localhost:8085 adk web

delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}

(.venv) (base) MacBook-Pro-3:bookings-agent abdullah$ GOOGLE_APPLICATION_CREDENTIALSOkay, so, seems everything is working at least for now. The issue with the service account I resolved with by using the Google application credentials in my terminal. So we need to make a note of that in the readme to set the Google application credentials with the path to the service account.