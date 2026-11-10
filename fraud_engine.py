import redis
from enum import Enum

class ReasonCodes(Enum):
    RC_HIGH_VELOCITY = "HIGH_VELOCITY_001"
    RC_NEW_DEVICE = "NEW_DEVICE_002"

class ResultValues(Enum): 
    RV_TRUST_SCORE = "trust_score"
    RV_REASON_CODE = "reason_codes"

redis_cl = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Apply velocity rules
def apply_velocity_rule(tenant_id: str, user_id: str, trust_score: int, reason_codes: list) -> int:
    """
    Rule -> 1:
    > Velocity Check (Lot of events in short window..)
    > Create a unique key for this specific user AND tenant, to Make sure Bank A's entries don't mess with Bank B's entry.
    """
    velocity_key = f"velocity:{tenant_id}:{user_id}"
    current_count = redis_cl.incr(velocity_key)

    if (current_count == 1):
        redis_cl.expire(velocity_key, 60)
        print(f"New user session, will expire in {redis_cl.ttl(velocity_key)}")

    if (current_count > 3):
        print(f"User exceeded the input count {user_id}")
        reason_codes.append(ReasonCodes.RC_HIGH_VELOCITY.value)
        trust_score -= 50

    return trust_score

# Check if the device is new or, old.
def apply_device_rule(tenant_id: str, user_id: str, trust_score: int, reason_codes: list) -> int:
    """
    Rule -> 2: 
    > New device check (Simulated)
    > Create a unique key for this specific user AND tenant, to Make sure Bank A's entries don't mess with Bank B's entry.
    """
    is_known_device = False

    if not is_known_device:
        reason_codes.append(ReasonCodes.RC_NEW_DEVICE.value)
        trust_score -= 20

    return trust_score

# Evaluate Incoming data against our rules..
def evaluate_fraud_rules(tenant_id: str, user_id: str, device_id: str) -> dict:
    """ From the start we'll assume the user is 'trusted'. """
    trust_score = 100
    reason_codes = []

    trust_score = apply_velocity_rule(tenant_id, user_id, trust_score, reason_codes)
    trust_score = apply_device_rule(tenant_id, user_id, trust_score, reason_codes)
    trust_score = max(0, trust_score)

    return {
        ResultValues.RV_TRUST_SCORE.value: trust_score,
        ResultValues.RV_REASON_CODE.value: reason_codes
    }
