from pydantic import BaseModel, Field


class Alert(BaseModel):
    id: int = Field(..., description="Unique identifier for the alert")
    status: str = Field(..., description="Current status of the alert")
    created_at: str = Field(..., description="Timestamp when the alert was created")
    updated_at: str = Field(..., description="Timestamp when the alert was last updated")
    severity: str = Field(..., description="Severity level of the alert")
    description: str = Field(..., description="Detailed description of the alert")