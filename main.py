from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from app.router.user_router import router as user_router
from app.router.club_router import router as club_router
from app.router.club_activity_router import router as challenge_activity_router

app = FastAPI()

app.include_router(user_router)
app.include_router(club_router)
app.include_router(challenge_activity_router)


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "Internal Server Error",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)