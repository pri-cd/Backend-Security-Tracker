import os
import json
import redis
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends

from security import verify_signature
from models import EventPayload

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

RedisCLI = redis.Redis(host="localhost", port=6379, decode_responses=True)
GuardAPI = FastAPI(title="Guard API", description="Multi-tenant risk deterrent engine")


@GuardAPI.post('/events', status_code=201, dependencies=[Depends(verify_signature)])
# Receives an event, evaluate fraud roles, saves to DB, and returns the score..
async def create_event(payload: EventPayload):

    event_data = payload.model_dump()
    event_json = json.dumps(event_data)

    RedisCLI.lpush("event_queue", event_json)
    response = {
        "status": "accepted",
        "message": "Event queue for processing",
        "event_id": payload.sess_id
    }   

    print(f"Response: {json.dumps(response, indent=4)}")

    return response
