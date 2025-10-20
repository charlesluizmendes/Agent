from pydantic import BaseModel


class NewsInputModel(BaseModel):
    topic: str
    
class NewsOutputModel(BaseModel):
    content: str