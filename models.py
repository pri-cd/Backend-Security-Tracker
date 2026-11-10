from pydantic import BaseModel, Field
from typing import Optional


class EventPayload(BaseModel):
    """ This model defines the EXACT shape of the JSON, that's expected to receive. """
    tenant_id: str = Field(..., description="The ID of client/bank sending the event")
    device_id: str = Field(..., description="The UID of a device")

    user_id: str = Field(..., description="Internal ID of user")
    sess_id: str = Field(..., description="Current session Identifier")

    event_type: str = Field(..., description="e.g., 'login', 'register', 'transfer'")
    ip_address: Optional[str] = None
