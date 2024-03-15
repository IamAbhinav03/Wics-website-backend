from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sql_app.main import router as api_router

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "https://iamabhinav03.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from api_routes.main.router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> dict:
    """
    Just a welcome message when using the api
    """
    return {"message": "Welcome to the Wics API"}
