from pydantic import BaseModel, constr, Field
from typing import List, Dict, Any

class DescriptionContent(BaseModel):
    text: str
    type: str

class Description(BaseModel):
    content: List[List[DescriptionContent]]  # Nested list structure
    type: str
    version: int

class Fields(BaseModel):
    issuetype: Dict[str, Any]  # Keeping it generic to allow any structure
    priority: Dict[str, Any]    # Keeping it generic to allow any structure
    description: Description
    assignee: Dict[str, Any]     # Keeping it generic to allow any structure
    project: Dict[str, Any]      # Keeping it generic to allow any structure
    summary: constr(min_length=1) # Ensures summary is not empty
    created: str                  # Created date as string (ISO 8601 format)

class CreateTicketModel(BaseModel):
    fields: Fields
    update: Dict[str, Any] = Field(default={})  # Initialize update to an empty dict
