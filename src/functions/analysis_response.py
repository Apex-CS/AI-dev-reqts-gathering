from src.functions.work_items import NewWorkItem
from pydantic import BaseModel, Field

class AnalysisResponse:
    def __init__(self, response):
        self.response = response
        self.pending_items = []
        
    def to_dict(self):
        return {
            "response": self.response,
            "pending_items": [item.to_dict() for item in self.pending_items]
            
        }
        
        
class AnalysisResponseBase(BaseModel):
    """AnalysisResponse represents the response from an analysis operation."""
    response: str = Field(..., description="The response from the analysis operation.")
    pending_items: list[NewWorkItem] = Field(
        default_factory=list, description="List of new work items pending creation."
    )
    

    @classmethod
    def from_dict(cls, data):
        """Create an AnalysisResponse instance from a dictionary."""
        return cls(
            response=data.get("response", ""),
            pending_items=[NewWorkItem.from_dict(item) for item in data.get("pending_items", [])]
        )