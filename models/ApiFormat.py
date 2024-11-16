from pydantic import BaseModel


class ApiFormat(BaseModel):
    url:str
    method:str
    payload:object