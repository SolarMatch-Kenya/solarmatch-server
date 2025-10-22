from pydantic import BaseModel
from datetime import datetime

class ContractBase(BaseModel):
    signature: str  # Base64 encoded image of the signature
    signed_at: datetime
    ip_address: str

class ContractCreate(ContractBase):
    pass

class Contract(ContractBase):
    id: int
    user_id: int  # Assuming a foreign key to the user/installer who signed the contract

    class Config:
        from_attributes = True
