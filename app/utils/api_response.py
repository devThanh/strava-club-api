from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class SuccessResponse:
    @staticmethod
    def response(data=None, message="Success", status_code=200):

        if isinstance(data, BaseModel):
            data = data.model_dump()

        if isinstance(data, list):
            data = [
                item.model_dump() if isinstance(item, BaseModel) else item
                for item in data
            ]

        content = {
            "status": status_code,
            "message": message,
        }

        if data is not None:
            content["data"] = data

        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(content)  # 🔥 FIX HERE
        )