"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .auth.router import router as auth_router
from .chat.router import router as chat_router
from .files.router import router as files_router

# Create FastAPI application
app = FastAPI(
    title="ChatGPTLike API",
    description="Backend API for ChatGPT-like application with file analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(files_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "ChatGPTLike API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
