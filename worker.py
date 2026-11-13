from fraud_engine import evaluate_fraud_rules
from fraud_engine import ResultValues as RV


import json
import redis
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
RedisCLI = redis.Redis(host="localhost", port=6379, decode_responses=True)

print("Worker started! -> Working for events..")

while True:
    result = RedisCLI.brpop("event_queue", timeout = 5)

    if result:
        _, event_json = result
        event_data = json.loads(event_json)

        print(f"Processing event for user: {event_data['user_id']}.")
        """
        1. Evaluate Fraud:
            Validated Data from Pydantic -> Redis-Powered Engine
        """
        fraud_res = evaluate_fraud_rules(
            tenant_id=event_data['tenant_id'],
            user_id=event_data['user_id'],
            device_id=event_data['device_id']
        )
    
        trust_score = fraud_res[RV.RV_TRUST_SCORE.value]
        reason_codes = fraud_res[RV.RV_REASON_CODE.value]
    
        """ 
        2. Save to Database:
            We prepare the exact dictionary structure that matches our "supabase" events tab.
            Self Note: supabase converts the 'db_record' directly -> to json. Refer: https://supabase.com/docs/reference/python/insert
        """
        db_record = {
            "tenant_id": event_data['tenant_id'],
            "device_id": event_data['device_id'],
            "user_id": event_data['user_id'],
            "event_type": event_data['event_type'],
            "ip_address": event_data['ip_address'],
            "trust_score": fraud_res[RV.RV_TRUST_SCORE.value],
            "reason_codes": fraud_res[RV.RV_REASON_CODE.value]
        }
    
        try:
            supabase.table('events').insert(db_record).execute()
            print(f"✅ Saved to DB. Score: {fraud_res['trust_score']}")
        except Exception as e:
            print(f"❌ DB Error: {e}")

    else:
        print("... Queue is empty. Waiting ...")