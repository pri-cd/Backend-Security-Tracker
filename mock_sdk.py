import requests
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv

URL = "http://127.0.0.1:8000/events"

load_dotenv()
SECRET_KEY = os.getenv("HMAC_API_SECURE_KEY")


def generate_signature(payload_bytes: bytes) -> str:
    """Simulates the SDK, signing the exact bytes sent in the request."""
    signature = hmac.new(
        key=SECRET_KEY.encode('utf-8'),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    return signature


def test_good_payload():
    print("===== Test 1: Legitimate Request (Correct Signature) =====")
    legit_payld = {
        "tenant_id": "tenant_lg_id",
        "device_id": "dev_legit_id",

        "user_id": "usr_legit_X_id",
        "sess_id": "session_Bxg_id",
        "event_type": "login"
    }

    """
        1. Sort the payload, 
        2. Calculate the signature on "sorted payload" 
        3. Add the signature under header: "X-Signature" 
        4. Add the payload (not the legit_payld. But, the sorted, converted payload_bytes)
    """
    payload_bytes = json.dumps(legit_payld, sort_keys=True).encode("utf-8")
    sig = generate_signature(payload_bytes)
    headers = {
        "X-Signature": sig,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url=URL,
        data=payload_bytes,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4)}")


def test_bad_payload():
    print("===== Test 2: Non-Legitimate Request =====")
    legit_payld = {
        "tenant_id": "tenant_lg_id",
        "device_id": "dev_legit_id",

        "user_id": "usr_legit_X_id",
        "sess_id": "session_Bxg_id",
        "event_type": "login"
    }

    """
        1. Sort the payload, 
        2. Calculate the signature on "sorted payload" 
    """
    payload_bytes = json.dumps(legit_payld, sort_keys=True).encode("utf-8")
    sig = generate_signature(payload_bytes)
    headers = {
        "X-Signature": sig,
        "Content-Type": "application/json"
    }

    """ Simulate the payload being hacked, change the payload values.. """
    hacker_payld = legit_payld.copy()
    hacker_payld["tenant_id"] = "tenant_hked_id_inject"
    hacker_payld_bytes = json.dumps(hacker_payld, sort_keys=True).encode("utf-8")

    response = requests.post(
        url=URL,
        data=hacker_payld_bytes,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4)}")


if __name__ == "__main__":    
    test_good_payload()
    test_bad_payload()

