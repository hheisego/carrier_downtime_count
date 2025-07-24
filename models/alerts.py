from pydantic import BaseModel, Field


class Alert(BaseModel):
    
    alertId: str = Field(..., description="Unique identifier for the alert")
    duration: float = Field(..., description="Duration of the alert in seconds")

    agents: list = Field(..., description="List of agents affected by the alert")

    testId: str = Field(..., description="Test ID associated with the alert")
    testName: str = Field(..., description="Name of the test associated with the alert")
    labels: list = Field(..., description="Labels associated with the alert")

    ruleName: str = Field(..., description="Name of the rule that triggered the alert")
    ruleId: str = Field(..., description="ID of the rule that triggered the alert")


    """
    1. Fetch active alerts from the API
    2. Pa sacar agentes afectados tenemos que sacar-- alertDetails -- alert["_links"]["self"]["href"]
    3. Sacar los tests asociados a cada alerta -- alert["_links"]["self"]["test"] pero le tenemos que poner aid y expand = label
    4. Sacar el ruleName -- alert["_links"]["self"]["rule"]
    """