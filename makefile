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
	FIRESTORE_EMULATOR_HOST=localhost:8081 firebase emulators:start --only firestore --project ${GOOGLE_CLOUD_PROJECT}

dev:
	FIRESTORE_EMULATOR_HOST=localhost:8081 adk web

delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}
