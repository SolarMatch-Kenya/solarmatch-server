from pydantic import BaseModel
from datetime import date

class ReportBase(BaseModel):
    customer_name: str
    address: str
    report_date: date
    status: str
    score: int

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: str  # Assuming ID can be a string based on the mock data 'r1', 'r2'

    class Config:
        from_attributes = True
