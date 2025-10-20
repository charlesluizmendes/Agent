from fastapi import Request
from fastapi.responses import JSONResponse
from dataclasses import asdict

from src.core.common.result import Result


async def error_request(request: Request, call_next):
    try:
        return await call_next(request)
    except ValueError as e:
        error_result = Result.error(str(e))
        return JSONResponse(
            status_code=400,
            content=asdict(error_result)
        )
    except Exception as e:
        error_result = Result.error(str(e))
        return JSONResponse(
            status_code=500,
            content=asdict(error_result)
        )