from pydantic import BaseModel


class FormInput(BaseModel):
    issuetype: str
    priority: str
    description: str
    assignee: str
    project: str
    summary: str
    created: str