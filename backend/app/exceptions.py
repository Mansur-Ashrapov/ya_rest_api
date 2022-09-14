from typing import Any
from pydantic import BaseModel

class ValidationError(BaseModel):
    code: int
    message: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        __pydantic_self__.code = 400
        __pydantic_self__.message = 'Validation Failed'