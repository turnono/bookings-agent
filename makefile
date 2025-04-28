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
	@echo "[Firestore Emulator] Starting Firestore emulator. Run this in its own terminal window!"
	FIRESTORE_EMULATOR_HOST=localhost:8086 firebase emulators:start --only firestore --project $(GOOGLE_CLOUD_PROJECT)

dev:
	@echo "[Dev Server] Starting ADK web server. Run this in a separate terminal after the emulator is running!"
	FIRESTORE_EMULATOR_HOST=localhost:8086 adk web

delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}

ngrok:
	@echo "[ngrok] Launching tunnel to smart-earwig-completely.ngrok-free.app:8000. Run this in its own terminal!"
	ngrok http --url=smart-earwig-completely.ngrok-free.app 8000
	

