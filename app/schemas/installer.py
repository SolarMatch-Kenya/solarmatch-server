from pydantic import BaseModel, EmailStr
from typing import Optional, List

class InstallerBase(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    service_areas: str  # This could be a List[str] if the frontend sends an array

class InstallerCreate(InstallerBase):
    pass

class Installer(InstallerBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

class InstallerUpdate(InstallerBase):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    service_areas: Optional[str] = None
    is_active: Optional[bool] = None
