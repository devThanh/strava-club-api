from pydantic import BaseModel

class CreateClubRequest(BaseModel):
    name: str
    is_public: bool