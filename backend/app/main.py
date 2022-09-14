from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db.database import database
from app.routes import (
    basic_router, additional_routes
)
from app.exceptions import ValidationError

app = FastAPI()


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return JSONResponse(content=jsonable_encoder({"code": 400, 'message': 'Validation Failed'}),
#                         status_code=status.HTTP_400_BAD_REQUEST)


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

app.include_router(basic_router)
app.include_router(additional_routes)
