"""
NIS HUB Core - Central FastAPI Application

This is the main entry point for the NIS HUB coordination system.
It handles node registration, memory synchronization, and inter-agent communication.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from routes.nodes import router as nodes_router
from routes.memory import router as memory_router
from routes.missions import router as missions_router
from routes.websocket import router as websocket_router
from routes.nis_integration import router as nis_integration_router, init_nis_integration_routes
from services.redis_service import RedisService
from services.protocol_bridge_service import ProtocolBridgeService
from services.logging_service import setup_logging

# Initialize structured logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("🚀 NIS HUB Core starting up...")
    
    # Initialize Redis connection
    redis_service = RedisService()
    await redis_service.initialize()
    app.state.redis = redis_service
    
    # Initialize WebSocket manager
    from services.websocket_manager import WebSocketManager
    ws_manager = WebSocketManager()
    app.state.ws_manager = ws_manager
    
    # Initialize Protocol Bridge Service for NIS Protocol v3.2.0 integration
    protocol_bridge = ProtocolBridgeService(redis_service, ws_manager)
    app.state.protocol_bridge = protocol_bridge
    
    # Initialize NIS integration routes with the protocol bridge
    init_nis_integration_routes(protocol_bridge)
    
    logger.info("🌐 NIS Protocol v3.2.0 integration initialized")
    logger.info("✅ NIS HUB Core initialization complete")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🔄 NIS HUB Core shutting down...")
    await redis_service.close()
    logger.info("✅ NIS HUB Core shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="NIS HUB - Central Intelligence Coordination",
    description="Central nervous system for all NIS Protocol deployments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.nis-hub.local"]
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(nodes_router, prefix="/api/v1", tags=["nodes"])
app.include_router(memory_router, prefix="/api/v1", tags=["memory"])
app.include_router(missions_router, prefix="/api/v1", tags=["missions"])
app.include_router(websocket_router, tags=["websocket"])
app.include_router(nis_integration_router, tags=["NIS Protocol Integration"])

@app.get("/")
async def root():
    """Health check and system status endpoint."""
    return {
        "message": "🧠 NIS HUB Central Intelligence System",
        "status": "operational",
        "version": "1.0.0",
        "unified_pipeline": "Laplace → Consciousness → KAN → PINN → Safety",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "nodes": "/api/v1/nodes",
            "memory": "/api/v1/memory",
            "missions": "/api/v1/missions",
            "websocket": "/ws",
            "nis_integration": "/api/v1/nis-integration"
        },
        "nis_integration_features": {
            "connect": "/api/v1/nis-integration/connect",
            "status": "/api/v1/nis-integration/status",
            "vision_analysis": "/api/v1/nis-integration/vision/analyze",
            "deep_research": "/api/v1/nis-integration/research/deep",
            "collaborative_reasoning": "/api/v1/nis-integration/reasoning/collaborative",
            "enhanced_chat": "/api/v1/nis-integration/chat/enhanced",
            "pipeline_processing": "/api/v1/nis-integration/pipeline/process",
            "auto_connect": "/api/v1/nis-integration/auto-connect"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    try:
        # Check Redis connection
        redis_status = await app.state.redis.ping()
        
        # Check active WebSocket connections
        active_connections = len(app.state.ws_manager.active_connections)
        
        # Check NIS Protocol connection
        nis_connection_status = "disconnected"
        nis_capabilities = {}
        if hasattr(app.state, 'protocol_bridge') and app.state.protocol_bridge.nis_base_connection:
            nis_connection_status = "connected"
            nis_capabilities = app.state.protocol_bridge.nis_base_capabilities
        
        return {
            "status": "healthy",
            "timestamp": "2025-01-20T12:00:00Z",
            "services": {
                "redis": "connected" if redis_status else "disconnected",
                "websocket": f"{active_connections} active connections",
                "api": "operational",
                "nis_protocol_integration": nis_connection_status
            },
            "system": {
                "registered_nodes": await app.state.redis.get_node_count(),
                "active_missions": await app.state.redis.get_mission_count(),
                "memory_size": await app.state.redis.get_memory_size()
            },
            "nis_integration": {
                "status": nis_connection_status,
                "version": nis_capabilities.get("version", "unknown"),
                "providers": nis_capabilities.get("providers", []),
                "multimodal_agents": len(nis_capabilities.get("multimodal_agents", []))
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    # Development server configuration  
    # Using port 8002 to avoid conflicts with NIS Protocol base system (8000) and runner (8001)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
        access_log=True
    ) 