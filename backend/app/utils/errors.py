from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.detail.get("code", "UNKNOWN_ERROR"),
                "message": exc.detail.get("message", str(exc.detail)),
                "details": exc.detail.get("details", {})
            },
            "status": exc.status_code
        }
    )