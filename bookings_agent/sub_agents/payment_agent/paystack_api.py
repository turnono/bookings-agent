import os
import requests
import hashlib
import hmac
import json

IS_DEV_MODE = os.environ.get("ENV", "development").lower() == "development"

if IS_DEV_MODE:
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SANDBOX_SECRET_KEY")
else:
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY")

PAYSTACK_BASE_URL = "https://api.paystack.co"

class PaystackAPI:
    @staticmethod
    def initialize_transaction(amount, email, metadata, callback_url=None):
        url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "amount": amount,  # amount in kobo
            "email": email,
            "metadata": metadata,
        }
        if callback_url:
            payload["callback_url"] = callback_url
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def verify_transaction(reference):
        url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def verify_webhook_signature(request_body, signature):
        computed = hmac.new(
            PAYSTACK_SECRET_KEY.encode(),
            msg=request_body,
            digestmod=hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed, signature) 