from fastapi import FastAPI
from src.api.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(api_router)

origins = [
    "http://localhost",  # Allow requests from localhost
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["POST"],  # Allow only POST requests
    allow_headers=["*"],  # Allow all headers
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
