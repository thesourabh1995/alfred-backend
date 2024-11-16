import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controllers.jira_controller import router as jira_router

app = FastAPI()

origins = [
    "http://localhost:3000",  # Update this with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Hey all ! Welcome to the Jira API"}

@app.get("/test-endpoint")
def test_api():
    return {"message": "test end point"}

app.include_router(jira_router)