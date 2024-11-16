from pydantic import BaseModel

from models.Issues import Issues
from typing import List


class JiraResponse(BaseModel):
    expand:str
    startAt:int
    maxResults:int
    total:int
    issues:List[Issues]
