"""
Compliance API schemas
"""
from pydantic import BaseModel
from typing import Optional, Literal

Tier = Literal["none", "basic_15", "expert_39"]


class AssessmentOut(BaseModel):
    assessment_id: str
    user_id: Optional[str] = None
    unlocked_tier: Tier = "none"
    stripe_session_id: Optional[str] = None

    class Config:
        from_attributes = True

