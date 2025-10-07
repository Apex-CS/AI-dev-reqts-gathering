from pydantic import BaseModel, Field
import json

class workItems(BaseModel):
    work_item_id: int
    title: str
    description: str
    state: str
    assigned_to: str
    acceptance_criteria: str
    tags: list[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.tags = [tag.strip() for tag in self.tags if tag.strip()]  # Clean up tags

    def to_dict(self):
        return {
            "id": self.work_item_id,
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "assigned_to": self.assigned_to,
            "acceptance_criteria": self.acceptance_criteria,
            "tags": ", ".join(self.tags) if self.tags else None
        }
        
class ImprovedWorkItem(BaseModel):
    """ImprovedWorkItem represents the result of an improvement process on a work item."""
    work_item_id: int = Field(
        ...,
        description="ID of the work item being improved."
    )
    explanation_changes: str = Field(
        ...,
        description="Explanation of Detailed analysis and improvement suggestions of the work item."
    )
    improved_description: str = Field(
        ...,
        description="Improved description of the work item, making it clearer and more actionable."
    )
    improved_title: str = Field(
        ...,
        description="Improved title of the work item, making it more descriptive and relevant."
    )
    improved_acceptance_criteria: str = Field(
        ...,
        description="Improved acceptance criteria of the work item, ensuring it is clear and testable."
    )
    
    def from_content(cls, content: str):
        """Parse the content string to create an ImprovedWorkItem instance."""
        try:
            data = json.loads(content)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content: {e}")
        except TypeError as e:
            raise ValueError(f"Invalid data format: {e}")
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create an ImprovedWorkItem instance from a dictionary."""
        return cls(
            work_item_id=data.get("id"),
            explanation_changes=data.get("explanation_changes"),
            improved_description=data.get("improved_description"),
            improved_title=data.get("improved_title"),
            improved_acceptance_criteria=data.get("improved_acceptance_criteria")
        )
        
    
    def to_dict(self):
        return {
            "id": self.work_item_id,
            "explanation_changes": self.explanation_changes,
            "improved_description": self.improved_description,
            "improved_title": self.improved_title,
            "improved_acceptance_criteria": self.improved_acceptance_criteria
        }

class NewWorkItem(BaseModel):
    """NewWorkItem represents a new work item to be created."""
    new_title: str = Field(..., description="Title of the new work item.")
    new_description: str = Field(..., description="Description of the new work item.")
    new_acceptance_criteria: str = Field(..., description="Acceptance criteria for the new work item.")
    
    def to_dict(self):
        return {
            "new_title": self.new_title,
            "new_description": self.new_description,
            "new_acceptance_criteria": self.new_acceptance_criteria
        }
        
    def extract_json_blocks(text):
        """Extract JSON blocks from the given text."""
        pattern = r'```json\s*(\{.*?\})\s*```'
        return [json.loads(match) for match in re.findall(pattern, text, re.DOTALL)]

    @classmethod
    def from_dict(cls, data: dict):
        """Create a NewWorkItem instance from a dictionary."""
        return cls(
            new_title=data.get("title"),
            new_description=data.get("description"),
            new_acceptance_criteria=data.get("acceptance_criteria")
        )
        
    