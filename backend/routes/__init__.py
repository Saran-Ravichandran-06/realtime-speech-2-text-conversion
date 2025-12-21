from fastapi import APIRouter
from .websocket_routes import router as websocket_router
from .file_routes import router as file_router
from .healthcheck import router as health_router

# Main router that combines all sub-routers
router = APIRouter()

# Attach each route group
router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
router.include_router(file_router, prefix="/api", tags=["File Upload"])
router.include_router(health_router, prefix="/api", tags=["Health"])
