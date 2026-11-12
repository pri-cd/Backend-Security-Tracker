from fastapi import FastAPI, HTTPException, Depends
from supabase import create_client, Client
from dotenv import load_dotenv
import os

from models import EventPayload
from fraud_engine import evaluate_fraud_rules
from fraud_engine import ReasonCodes as RC
from fraud_engine import ResultValues as RV
from security import verify_signature

load_dotenv()

GuardAPI = FastAPI(title="Guard API",
                   description="Multi-tenant risk deterrent engine")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(
    supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)


@GuardAPI.post('/events', status_code=201, dependencies=[Depends(verify_signature)])
# Receives an event, evaluate fraud roles, saves to DB, and returns the score..
async def create_event(payload: EventPayload):
    """
    1. Evaluate Fraud:
        Validated Data from Pydantic -> Redis-Powered Engine
    """
    fraud_res = evaluate_fraud_rules(
        tenant_id=payload.tenant_id,
        user_id=payload.user_id,
        device_id=payload.device_id
    )

    trust_score = fraud_res[RV.RV_TRUST_SCORE.value]
    reason_codes = fraud_res[RV.RV_REASON_CODE.value]

    """ 
    2. Save to Database:
        We prepare the exact dictionary structure that matches our "supabase" events tab.
        Self Note: supabase converts the 'db_record' directly -> to json. Refer: https://supabase.com/docs/reference/python/insert
    """
    db_record = {
        "tenant_id": payload.tenant_id,
        "device_id": payload.device_id,
        "user_id": payload.user_id,
        "event_type": payload.event_type,
        "ip_address": payload.ip_address,
        "trust_score": trust_score,
        "reason_codes": reason_codes
    }

    try:
        response = supabase.table('events').insert(db_record).execute()
        inserted_id = response.data[0]['id']
        print(response.model_dump_json(indent=4))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database Error: {str(e)}")

    return {
        "status": "success",
        "event_id": inserted_id,
        "trust_score": trust_score,
        "reason_codes": reason_codes
    }
