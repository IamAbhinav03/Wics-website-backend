from fastapi import FastAPI
from sql_app.main import router as api_router

app = FastAPI()

# Include routes from api_routes.main.router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> dict:
    """
    Just a welcome message when using the api
    """
    return {"message": "Welcome to the Wics API"}
