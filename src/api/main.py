from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_versionizer.versionizer import Versionizer

from src.api.error import error_request
from src.api.routes.newsRoutes import router as newsRoutes


app = FastAPI(
    title="Agent",
    description="API Agent News.",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.middleware("http")(error_request)

app.include_router(newsRoutes)

versions = Versionizer(
    app=app,
    prefix_format='/api/v{major}',
    semantic_version_format='{major}',
    latest_prefix='/api/latest',
    sort_routes=True
).versionize()

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/api/latest/docs")