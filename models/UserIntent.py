from pydantic import BaseModel


class UserIntent(BaseModel):
    intent: str
    parameters: dict
    original_text: str