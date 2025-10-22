from pydantic import BaseModel
from typing import Optional

class LeadBase(BaseModel):
    name: str
    location: str
    potential: str
    status: str
    contact: str

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int

    class Config:
        from_attributes = True
