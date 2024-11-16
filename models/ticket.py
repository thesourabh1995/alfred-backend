from pydantic import BaseModel
from typing import List, Optional

from models.Issues import User, Status, Priority, Project


class Ticket(BaseModel):
    id: str
    key: str
    summary: str
    assignee: str
    creator: str
    reporter: str
    status: str
    priority: str
    created: str
    updated: str
