"""
NIS Protocol Integration Routes for NIS-HUB v3.1

Handles direct integration with running NIS Protocol v3.2.0 base system
Provides access to multimodal capabilities, research, reasoning, and vision analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from services.protocol_bridge_service import ProtocolBridgeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nis-integration", tags=["NIS Protocol Integration"])

# Initialize protocol bridge service (will be injected in main.py)
protocol_bridge: Optional[ProtocolBridgeService] = None

def get_protocol_bridge() -> ProtocolBridgeService:
    """Get protocol bridge service instance."""
    if protocol_bridge is None:
        raise HTTPException(status_code=503, detail="Protocol bridge service not initialized")
    return protocol_bridge

# Request/Response Models

class NISConnectionRequest(BaseModel):
    """Request to connect to NIS Protocol base system."""
    base_url: str = Field("http://localhost:8000", description="NIS Protocol base URL")

class VisionAnalysisRequest(BaseModel):
    """Request for vision analysis via NIS Protocol."""
    image_url: Optional[str] = Field(None, description="URL of image to analyze")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    analysis_type: str = Field("comprehensive", description="Type of analysis")
    provider: Optional[str] = Field(None, description="Specific AI provider to use")

class ResearchRequest(BaseModel):
    """Request for deep research via NIS Protocol."""
    query: str = Field(..., description="Research query")
    sources: List[str] = Field(["arxiv", "semantic_scholar", "wikipedia"], description="Research sources")
    depth: str = Field("standard", description="Research depth: quick, standard, deep")

class ReasoningRequest(BaseModel):
    """Request for collaborative reasoning via NIS Protocol."""
    problem: str = Field(..., description="Problem to reason about")
    reasoning_type: str = Field("analytical", description="Type of reasoning")
    models: List[str] = Field(["claude-3-opus", "gpt-4-turbo", "gemini-pro"], description="Models to use")

class ChatRequest(BaseModel):
    """Request for enhanced chat via NIS Protocol."""
    message: str = Field(..., description="Message to send")
    agent_type: str = Field("consciousness", description="Type of agent to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

# API Endpoints

@router.post("/connect")
async def connect_to_nis_protocol(request: NISConnectionRequest) -> Dict[str, Any]:
    """
    Connect NIS-HUB to a running NIS Protocol v3.2.0 base system.
    
    This establishes communication with the base NIS Protocol system,
    discovering its capabilities and multimodal agents.
    """
    try:
        bridge = get_protocol_bridge()
        result = await bridge.connect_to_nis_base(request.base_url)
        
        if result["status"] == "success":
            logger.info(f"Successfully connected to NIS Protocol at {request.base_url}")
            return {
                "success": True,
                "message": "Connected to NIS Protocol base system",
                "connection": result
            }
        else:
            raise HTTPException(status_code=400, detail=f"Connection failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error connecting to NIS Protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_nis_integration_status() -> Dict[str, Any]:
    """
    Get comprehensive status of NIS Protocol integration.
    
    Returns connection status, capabilities, and health information
    for the connected NIS Protocol v3.2.0 base system.
    """
    try:
        bridge = get_protocol_bridge()
        status = await bridge.get_nis_base_status()
        
        return {
            "success": True,
            "nis_integration": status,
            "timestamp": status.get("timestamp", None)
        }
        
    except Exception as e:
        logger.error(f"Error getting NIS integration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/analyze")
async def analyze_via_nis_vision(request: VisionAnalysisRequest) -> Dict[str, Any]:
    """
    Perform vision analysis using NIS Protocol v3.2.0 vision agents.
    
    Supports multiple AI providers (OpenAI, Google, Anthropic) and analysis types
    including scientific, technical, and physics-focused analysis.
    """
    try:
        bridge = get_protocol_bridge()
        
        # Prepare image data for NIS Protocol
        image_data = {
            "image_url": request.image_url,
            "image_data": request.image_data,
            "analysis_type": request.analysis_type,
            "provider": request.provider
        }
        
        result = await bridge.vision_analysis_via_nis_base(image_data)
        
        if result["status"] == "success":
            return {
                "success": True,
                "message": "Vision analysis completed",
                "analysis": result["data"],
                "response_time": result.get("response_time")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Vision analysis failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in vision analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/deep")
async def deep_research_via_nis(request: ResearchRequest) -> Dict[str, Any]:
    """
    Perform deep research using NIS Protocol v3.2.0 research agents.
    
    Accesses multiple sources (arXiv, Semantic Scholar, Wikipedia) and
    provides evidence-based research with claim validation.
    """
    try:
        bridge = get_protocol_bridge()
        
        result = await bridge.deep_research_via_nis_base(request.query, request.sources)
        
        if result["status"] == "success":
            return {
                "success": True,
                "message": "Research completed",
                "research": result["data"],
                "response_time": result.get("response_time")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Research failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in deep research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reasoning/collaborative")
async def collaborative_reasoning_via_nis(request: ReasoningRequest) -> Dict[str, Any]:
    """
    Perform collaborative reasoning using NIS Protocol v3.2.0 reasoning agents.
    
    Uses multiple AI models for cross-validation and consensus building
    across mathematical, logical, creative, and analytical reasoning types.
    """
    try:
        bridge = get_protocol_bridge()
        
        result = await bridge.collaborative_reasoning_via_nis_base(
            request.problem, 
            request.reasoning_type
        )
        
        if result["status"] == "success":
            return {
                "success": True,
                "message": "Collaborative reasoning completed",
                "reasoning": result["data"],
                "response_time": result.get("response_time")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Reasoning failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in collaborative reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/enhanced")
async def enhanced_chat_via_nis(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with NIS Protocol v3.2.0 enhanced agents.
    
    Provides access to consciousness-driven agents with bias detection,
    ethical reasoning, and the full unified pipeline processing.
    """
    try:
        bridge = get_protocol_bridge()
        
        result = await bridge.enhanced_chat_via_nis_base(
            request.message,
            request.agent_type,
            f"nis-hub-{datetime.now().strftime('%Y%m%d')}"
        )
        
        if result["status"] == "success":
            # Extract the response content properly
            response_data = result.get("data", {})
            
            return {
                "success": True,
                "message": "Chat completed",
                "response": response_data,
                "response_time": result.get("response_time"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Chat failed: {result.get('message', 'Unknown error')}",
                "error_details": result,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in enhanced chat: {e}")
        return {
            "success": False,
            "message": f"Chat error: {str(e)}",
            "error_details": {"exception": str(e)},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/capabilities")
async def get_nis_capabilities() -> Dict[str, Any]:
    """
    Get detailed capabilities of the connected NIS Protocol v3.2.0 system.
    
    Returns information about available providers, features, multimodal agents,
    and supported operations.
    """
    try:
        bridge = get_protocol_bridge()
        
        if not bridge.nis_base_connection:
            return {
                "success": False,
                "message": "Not connected to NIS Protocol base system",
                "capabilities": {},
                "connection_info": None
            }
        
        return {
            "success": True,
            "capabilities": bridge.nis_base_capabilities,
            "connection_info": {
                "url": bridge.nis_base_connection.get("url"),
                "connected_at": bridge.nis_base_connection.get("connected_at"),
                "status": bridge.nis_base_connection.get("status")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "message": f"Error getting capabilities: {str(e)}",
            "capabilities": {},
            "connection_info": None
        }

@router.post("/pipeline/process")
async def process_via_unified_pipeline(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data through the NIS Protocol v3.2.0 unified pipeline.
    
    Applies the complete Laplace → Consciousness → KAN → PINN → Safety pipeline
    to any input data, ensuring verifiable and physics-compliant outputs.
    """
    try:
        bridge = get_protocol_bridge()
        
        # Try to send through various pipeline endpoints
        result = await bridge.send_to_nis_base("/pipeline/process", data)
        
        if result["status"] == "success":
            return {
                "success": True,
                "message": "Pipeline processing completed",
                "processed_data": result["data"],
                "response_time": result.get("response_time")
            }
        else:
            # Fallback to enhanced chat if pipeline endpoint not available
            fallback_result = await bridge.enhanced_chat_via_nis_base(
                str(data), "consciousness"
            )
            
            return {
                "success": True,
                "message": "Processed via enhanced chat (fallback)",
                "processed_data": fallback_result.get("data"),
                "response_time": fallback_result.get("response_time"),
                "method": "fallback"
            }
            
    except Exception as e:
        logger.error(f"Error in pipeline processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-connect")
async def auto_connect_nis_protocol() -> Dict[str, Any]:
    """
    Automatically discover and connect to local NIS Protocol instance.
    
    Tries common local URLs to find running NIS Protocol v3.2.0 systems.
    """
    try:
        bridge = get_protocol_bridge()
        
        # Try auto-connection
        await bridge._auto_connect_nis_base()
        
        if bridge.nis_base_connection:
            return {
                "success": True,
                "message": "Auto-connected to NIS Protocol",
                "connection": {
                    "url": bridge.nis_base_connection.get("url"),
                    "version": bridge.nis_base_capabilities.get("version"),
                    "capabilities": len(bridge.nis_base_capabilities.get("multimodal_agents", []))
                }
            }
        else:
            raise HTTPException(status_code=404, detail="No local NIS Protocol instance found")
            
    except Exception as e:
        logger.error(f"Error in auto-connect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize function (called from main.py)
def init_nis_integration_routes(bridge_service: ProtocolBridgeService):
    """Initialize the NIS integration routes with protocol bridge service."""
    global protocol_bridge
    protocol_bridge = bridge_service
    logger.info("🌐 NIS Protocol integration routes initialized")
