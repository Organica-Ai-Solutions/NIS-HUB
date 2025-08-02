"""
NIS HUB SDK - Protocol Integration Module

Provides classes and utilities for interacting with the NIS HUB's
external protocol bridges, including MCP, ATOA, and OpenAI Tools.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
from enum import Enum

import aiohttp
from pydantic import BaseModel, Field, validator

from .client import NISNode
from .config import NISHubConfig
from .exceptions import NISProtocolError, NISConnectionError, NISValidationError

logger = logging.getLogger(__name__)

class ProtocolType(str, Enum):
    """Supported external protocol types."""
    MCP = "model_context_protocol"
    ATOA = "agent_to_operator_to_agent"
    OPENAI_TOOLS = "openai_tools"
    ANTHROPIC_MCP = "anthropic_mcp"
    LANGCHAIN = "langchain"
    AUTOGEN = "autogen"
    CREWAI = "crewai"
    SEMANTIC_KERNEL = "semantic_kernel"
    CHAINLIT = "chainlit"
    CUSTOM = "custom"

class MessageDirection(str, Enum):
    """Direction of protocol message."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

class MessageType(str, Enum):
    """Types of messages in ATOA workflows."""
    REQUEST = "request"
    RESPONSE = "response"
    APPROVAL = "approval"
    REJECTION = "rejection"
    CLARIFICATION = "clarification"
    NOTIFICATION = "notification"
    VALIDATION = "validation"
    ERROR = "error"
    CONSCIOUSNESS_ALERT = "consciousness_alert"
    PHYSICS_VIOLATION = "physics_violation"
    SAFETY_ALERT = "safety_alert"

class UrgencyLevel(str, Enum):
    """Urgency levels for ATOA messages."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class ToolType(str, Enum):
    """Types of OpenAI tools."""
    FUNCTION = "function"
    RETRIEVAL = "retrieval"
    CODE_INTERPRETER = "code_interpreter"

class MCPRequest(BaseModel):
    """Model Context Protocol request structure."""
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[Union[str, int]] = None
    
    # NIS v3.1 extensions
    nis_pipeline_stage: Optional[str] = None
    consciousness_level: Optional[float] = None
    pinn_validation_required: bool = False
    kan_interpretability_required: bool = False
    
    class Config:
        use_enum_values = True

class MCPResponse(BaseModel):
    """Model Context Protocol response structure."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    
    # NIS v3.1 extensions
    nis_validation: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True

class ATOAMessage(BaseModel):
    """Agent-to-Operator-to-Agent message structure."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    operator_id: Optional[str] = None
    target_agent_id: Optional[str] = None
    message_type: MessageType
    content: Dict[str, Any]
    requires_human_approval: bool = False
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # NIS v3.1 extensions
    ethical_review_required: bool = False
    physics_validation_required: bool = False
    consciousness_assessment: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None
    
    class Config:
        use_enum_values = True

class OpenAITool(BaseModel):
    """OpenAI Tool definition."""
    type: ToolType = ToolType.FUNCTION
    function: Dict[str, Any]
    
    # NIS v3.1 extensions
    nis_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True

class ToolCall(BaseModel):
    """OpenAI Tool Call."""
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    type: ToolType = ToolType.FUNCTION
    function: Dict[str, Any]
    
    class Config:
        use_enum_values = True

class ToolCallResult(BaseModel):
    """Result of an OpenAI Tool Call."""
    tool_call_id: str
    output: str
    
    # NIS v3.1 extensions
    nis_validation: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True

class ProtocolBridge:
    """
    Client for interacting with NIS HUB's external protocol bridges.
    
    This class provides methods for registering and using external protocol
    bridges like MCP, ATOA, and OpenAI Tools with NIS HUB.
    """
    
    def __init__(self, config: Optional[NISHubConfig] = None, node: Optional[NISNode] = None):
        """
        Initialize the Protocol Bridge client.
        
        Args:
            config: NIS HUB configuration
            node: NIS Node instance for authentication
        """
        self.config = config or NISHubConfig()
        self.node = node
        
        # Active bridges
        self.active_bridges: Dict[str, Dict[str, Any]] = {}
        
        # Session
        self._session = None
        
        logger.info("🌉 Protocol Bridge client initialized")
    
    async def register_protocol(self, 
                              protocol: Union[str, ProtocolType],
                              endpoint: str,
                              authentication: Optional[Dict[str, Any]] = None,
                              configuration: Optional[Dict[str, Any]] = None) -> str:
        """
        Register an external protocol for communication.
        
        Args:
            protocol: Type of external protocol
            endpoint: Communication endpoint
            authentication: Authentication credentials
            configuration: Protocol-specific configuration
            
        Returns:
            Bridge ID for this protocol connection
        """
        if isinstance(protocol, ProtocolType):
            protocol = protocol.value
        
        try:
            # Prepare request data
            data = {
                "protocol": protocol,
                "endpoint": endpoint,
                "authentication": authentication or {},
                "configuration": configuration or {}
            }
            
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/register", data)
            
            # Store bridge information
            bridge_id = response["bridge_id"]
            self.active_bridges[bridge_id] = {
                "protocol": protocol,
                "endpoint": endpoint,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Protocol registered: {protocol} (Bridge ID: {bridge_id})")
            
            return bridge_id
            
        except Exception as e:
            logger.error(f"Error registering protocol {protocol}: {e}")
            raise NISProtocolError(f"Failed to register protocol: {str(e)}")
    
    async def send_to_protocol(self,
                             bridge_id: str,
                             message: Dict[str, Any],
                             require_nis_validation: bool = True) -> Dict[str, Any]:
        """
        Send message to external protocol through bridge.
        
        Args:
            bridge_id: Bridge identifier
            message: Message to send
            require_nis_validation: Whether to apply NIS v3.1 validation
            
        Returns:
            Response from external protocol
        """
        if bridge_id not in self.active_bridges:
            raise NISProtocolError(f"Bridge {bridge_id} not found")
        
        try:
            # Prepare request data
            data = {
                "bridge_id": bridge_id,
                "message": message,
                "require_nis_validation": require_nis_validation
            }
            
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/send", data)
            
            # Update bridge statistics
            self.active_bridges[bridge_id]["last_activity"] = datetime.utcnow().isoformat()
            
            logger.info(f"Message sent to protocol via {bridge_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending to protocol via {bridge_id}: {e}")
            raise NISProtocolError(f"Failed to send message: {str(e)}")
    
    async def get_protocol_status(self, bridge_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of protocol bridges.
        
        Args:
            bridge_id: Optional bridge identifier
            
        Returns:
            Protocol bridge status
        """
        try:
            # Prepare request path
            path = "/api/v1/protocols/status"
            if bridge_id:
                path += f"/{bridge_id}"
            
            # Send request to NIS HUB
            response = await self._get(path)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting protocol status: {e}")
            raise NISProtocolError(f"Failed to get protocol status: {str(e)}")
    
    # MCP-specific methods
    
    async def create_mcp_request(self, 
                               method: str, 
                               params: Dict[str, Any],
                               nis_validation: bool = True) -> Dict[str, Any]:
        """
        Create an MCP request with NIS v3.1 validation metadata.
        
        Args:
            method: MCP method name
            params: Method parameters
            nis_validation: Whether to apply NIS validation
            
        Returns:
            MCP request with NIS metadata
        """
        request_id = str(uuid.uuid4())
        
        request = MCPRequest(
            jsonrpc="2.0",
            method=method,
            params=params,
            id=request_id
        )
        
        if nis_validation:
            # Add NIS-specific extensions
            request.nis_pipeline_stage = "pending"
            request.consciousness_level = 0.0  # Will be updated during validation
            request.pinn_validation_required = True
            request.kan_interpretability_required = True
        
        return request.dict()
    
    async def send_mcp_request(self,
                             bridge_id: str,
                             method: str,
                             params: Dict[str, Any],
                             nis_validation: bool = True) -> Dict[str, Any]:
        """
        Send an MCP request through a protocol bridge.
        
        Args:
            bridge_id: Bridge identifier
            method: MCP method name
            params: Method parameters
            nis_validation: Whether to apply NIS validation
            
        Returns:
            MCP response
        """
        # Create MCP request
        request = await self.create_mcp_request(method, params, nis_validation)
        
        # Send through protocol bridge
        response = await self.send_to_protocol(bridge_id, request, nis_validation)
        
        # Parse response
        try:
            mcp_response = MCPResponse(**response)
            return mcp_response.dict()
        except Exception as e:
            logger.error(f"Error parsing MCP response: {e}")
            return response
    
    # ATOA-specific methods
    
    async def create_atoa_message(self,
                                agent_id: str,
                                message_type: Union[str, MessageType],
                                content: Dict[str, Any],
                                target_agent_id: Optional[str] = None,
                                operator_id: Optional[str] = None,
                                requires_human_approval: bool = False,
                                urgency: Union[str, UrgencyLevel] = UrgencyLevel.NORMAL,
                                ethical_review_required: bool = False,
                                physics_validation_required: bool = False) -> Dict[str, Any]:
        """
        Create an ATOA message.
        
        Args:
            agent_id: Source agent identifier
            message_type: Type of message
            content: Message content
            target_agent_id: Target agent identifier
            operator_id: Operator identifier
            requires_human_approval: Whether human approval is required
            urgency: Message urgency
            ethical_review_required: Whether ethical review is required
            physics_validation_required: Whether physics validation is required
            
        Returns:
            ATOA message
        """
        if isinstance(message_type, str):
            message_type = MessageType(message_type)
        
        if isinstance(urgency, str):
            urgency = UrgencyLevel(urgency)
        
        message = ATOAMessage(
            agent_id=agent_id,
            message_type=message_type,
            content=content,
            target_agent_id=target_agent_id,
            operator_id=operator_id,
            requires_human_approval=requires_human_approval,
            urgency=urgency,
            ethical_review_required=ethical_review_required,
            physics_validation_required=physics_validation_required
        )
        
        return message.dict()
    
    async def initiate_atoa_workflow(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a new ATOA workflow.
        
        Args:
            message: ATOA message
            
        Returns:
            Workflow information
        """
        try:
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/atoa/initiate", message)
            
            logger.info(f"ATOA workflow initiated: {response.get('workflow_id')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error initiating ATOA workflow: {e}")
            raise NISProtocolError(f"Failed to initiate ATOA workflow: {str(e)}")
    
    async def add_message_to_workflow(self, 
                                    workflow_id: str, 
                                    message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a message to an existing ATOA workflow.
        
        Args:
            workflow_id: Workflow identifier
            message: ATOA message
            
        Returns:
            Updated workflow information
        """
        try:
            # Prepare request data
            data = {
                "workflow_id": workflow_id,
                "message": message
            }
            
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/atoa/message", data)
            
            logger.info(f"Message added to ATOA workflow: {workflow_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding message to ATOA workflow: {e}")
            raise NISProtocolError(f"Failed to add message to workflow: {str(e)}")
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of an ATOA workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status information
        """
        try:
            # Send request to NIS HUB
            response = await self._get(f"/api/v1/protocols/atoa/status/{workflow_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting ATOA workflow status: {e}")
            raise NISProtocolError(f"Failed to get workflow status: {str(e)}")
    
    async def handle_atoa_workflow(self,
                                 agent_request: Dict[str, Any],
                                 operator_oversight: bool = True,
                                 timeout: int = 60) -> Dict[str, Any]:
        """
        Handle complete Agent-to-Operator-to-Agent workflow with NIS v3.1 validation.
        
        Args:
            agent_request: Request from initiating agent
            operator_oversight: Whether human operator oversight is required
            timeout: Timeout in seconds
            
        Returns:
            Workflow result with all validations
        """
        try:
            # Prepare request data
            data = {
                "agent_request": agent_request,
                "operator_oversight": operator_oversight
            }
            
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/atoa/handle", data)
            
            # Check if workflow is completed
            workflow_id = response.get("workflow_id")
            if not workflow_id:
                raise NISProtocolError("No workflow ID returned")
            
            # Wait for workflow completion if not already completed
            if response.get("status") not in ["completed", "rejected", "error", "cancelled"]:
                start_time = datetime.utcnow()
                while True:
                    # Check if timeout reached
                    if (datetime.utcnow() - start_time).total_seconds() > timeout:
                        raise NISProtocolError(f"Workflow timeout after {timeout} seconds")
                    
                    # Get workflow status
                    status = await self.get_workflow_status(workflow_id)
                    
                    if status.get("status") in ["completed", "rejected", "error", "cancelled"]:
                        response = status
                        break
                    
                    # Wait before checking again
                    await asyncio.sleep(1)
            
            logger.info(f"ATOA workflow handled: {workflow_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling ATOA workflow: {e}")
            raise NISProtocolError(f"Failed to handle ATOA workflow: {str(e)}")
    
    # OpenAI Tools-specific methods
    
    async def create_openai_tool(self, 
                               name: str,
                               description: str,
                               parameters: Dict[str, Any],
                               nis_requirements: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """
        Create an OpenAI tool with NIS v3.1 validation requirements.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            nis_requirements: NIS validation requirements
            
        Returns:
            OpenAI tool definition with NIS metadata
        """
        # Default NIS requirements
        if nis_requirements is None:
            nis_requirements = {
                "requires_consciousness": True,
                "requires_pinn_validation": True,
                "requires_kan_interpretation": True,
                "requires_safety_check": True
            }
        
        tool = OpenAITool(
            type=ToolType.FUNCTION,
            function={
                "name": name,
                "description": description,
                "parameters": parameters
            },
            nis_metadata=nis_requirements
        )
        
        return tool.dict()
    
    async def register_openai_tool(self, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new OpenAI tool with NIS HUB.
        
        Args:
            tool_definition: Tool definition
            
        Returns:
            Registration result
        """
        try:
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/openai/register_tool", tool_definition)
            
            logger.info(f"OpenAI tool registered: {tool_definition.get('function', {}).get('name')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error registering OpenAI tool: {e}")
            raise NISProtocolError(f"Failed to register OpenAI tool: {str(e)}")
    
    async def create_tool_call(self,
                             function_name: str,
                             arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an OpenAI tool call.
        
        Args:
            function_name: Function name
            arguments: Function arguments
            
        Returns:
            Tool call
        """
        tool_call = ToolCall(
            function={
                "name": function_name,
                "arguments": json.dumps(arguments) if not isinstance(arguments, str) else arguments
            }
        )
        
        return tool_call.dict()
    
    async def handle_tool_call(self,
                             tool_call: Dict[str, Any],
                             bridge_id: Optional[str] = None,
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle an OpenAI tool call with NIS v3.1 validation.
        
        Args:
            tool_call: Tool call data
            bridge_id: Bridge identifier
            session_id: Session identifier
            
        Returns:
            Tool call result
        """
        try:
            # Prepare request data
            data = {
                "tool_call": tool_call,
                "session_id": session_id
            }
            
            if bridge_id:
                data["bridge_id"] = bridge_id
            
            # Send request to NIS HUB
            response = await self._post("/api/v1/protocols/openai/handle_tool_call", data)
            
            logger.info(f"OpenAI tool call handled: {tool_call.get('function', {}).get('name')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling OpenAI tool call: {e}")
            raise NISProtocolError(f"Failed to handle OpenAI tool call: {str(e)}")
    
    # Private methods
    
    async def _ensure_session(self):
        """Ensure HTTP session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
    
    async def _get(self, path: str) -> Dict[str, Any]:
        """Send GET request to NIS HUB."""
        await self._ensure_session()
        
        url = f"{self.config.hub_url}{path}"
        headers = self._get_headers()
        
        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise NISConnectionError(f"HTTP error {response.status}: {error_text}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise NISConnectionError(f"Connection error: {str(e)}")
    
    async def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request to NIS HUB."""
        await self._ensure_session()
        
        url = f"{self.config.hub_url}{path}"
        headers = self._get_headers()
        
        try:
            async with self._session.post(url, json=data, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise NISConnectionError(f"HTTP error {response.status}: {error_text}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise NISConnectionError(f"Connection error: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication if node is available
        if self.node and self.node.node_id:
            headers["X-NIS-Node-ID"] = self.node.node_id
            
            if hasattr(self.node, "auth_token") and self.node.auth_token:
                headers["Authorization"] = f"Bearer {self.node.auth_token}"
        
        return headers
    
    async def close(self):
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None