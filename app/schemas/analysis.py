from pydantic import BaseModel
from typing import Optional

class AnalysisBase(BaseModel):
    address: str
    energy_consumption: float
    roof_type: str

class AnalysisCreate(AnalysisBase):
    pass

class Analysis(AnalysisBase):
    id: int
    # Add other fields that would be returned after an analysis is performed
    # For example:
    # solar_potential: float
    # cost_savings: float
    # co2_reduction: float

    class Config:
        from_attributes = True
