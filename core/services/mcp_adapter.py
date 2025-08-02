"""
MCP (Model Context Protocol) Adapter for NIS HUB v3.1

Implements a dedicated adapter for the Model Context Protocol standard,
enabling seamless integration with MCP-compatible AI systems while
maintaining the integrity of the NIS Protocol v3.1 unified pipeline.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

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
    
    @validator('jsonrpc')
    def validate_jsonrpc_version(cls, v):
        if v != "2.0":
            raise ValueError("Only JSON-RPC 2.0 is supported")
        return v

class MCPResponse(BaseModel):
    """Model Context Protocol response structure."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    
    # NIS v3.1 extensions
    nis_validation: Optional[Dict[str, Any]] = None
    
    @validator('error', 'result')
    def validate_result_or_error(cls, v, values):
        if 'error' in values and values['error'] is not None and 'result' in values and values['result'] is not None:
            raise ValueError("Cannot include both 'result' and 'error'")
        return v

class MCPTool(BaseModel):
    """MCP Tool definition structure."""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    outputSchema: Optional[Dict[str, Any]] = None
    
    # NIS v3.1 extensions
    nis_capabilities: Optional[Dict[str, Any]] = None
    requires_consciousness: bool = False
    requires_pinn_validation: bool = False
    requires_kan_interpretation: bool = False

class MCPAdapter:
    """Adapter for Model Context Protocol (MCP) integration with NIS Protocol v3.1."""
    
    def __init__(self, 
                 consciousness_service=None, 
                 pinn_service=None, 
                 kan_service=None, 
                 bitnet_service=None):
        """Initialize the MCP adapter."""
        self.consciousness_service = consciousness_service
        self.pinn_service = pinn_service
        self.kan_service = kan_service
        self.bitnet_service = bitnet_service
        
        # MCP server configuration
        self.server_config: Dict[str, Any] = {}
        
        # Available MCP tools
        self.tools: Dict[str, MCPTool] = {}
        
        # Active MCP sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default tools
        self._initialize_default_tools()
        
        logger.info("🔄 MCP Adapter initialized")
    
    async def initialize_server(self, 
                              name: str,
                              version: str = "1.0.0",
                              additional_tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Initialize an MCP server for external agents.
        
        Args:
            name: Server name
            version: Server version
            additional_tools: Additional tools to register
            
        Returns:
            MCP server configuration
        """
        try:
            self.server_config = {
                "name": name,
                "version": version,
                "protocol_version": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": True,
                        "listChanged": True
                    },
                    "prompts": {
                        "listChanged": True
                    },
                    "logging": {}
                },
                # NIS v3.1 specific capabilities
                "nis_capabilities": {
                    "consciousness_analysis": True,
                    "pinn_validation": True,
                    "kan_interpretation": True,
                    "bitnet_inference": True,
                    "unified_pipeline": True,
                    "verifiable_outputs": True
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Register additional tools
            if additional_tools:
                for tool_data in additional_tools:
                    tool = MCPTool(**tool_data)
                    self.tools[tool.name] = tool
            
            logger.info(f"MCP server initialized: {name} v{version}")
            
            return self.server_config
            
        except Exception as e:
            logger.error(f"Error initializing MCP server: {e}")
            raise
    
    async def handle_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request and apply NIS v3.1 unified pipeline.
        
        Args:
            request_data: Raw MCP request data
            
        Returns:
            MCP response with NIS validation
        """
        try:
            # Parse and validate request
            request = MCPRequest(**request_data)
            
            # Generate response ID if not provided
            if request.id is None:
                request.id = str(uuid.uuid4())
            
            # Create session if needed
            session_id = f"mcp_{request.id}"
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "session_id": session_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "request_count": 0,
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            # Update session stats
            self.active_sessions[session_id]["request_count"] += 1
            self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            
            # Handle different MCP methods
            if request.method == "rpc.discover":
                result = await self._handle_discover()
            elif request.method == "tools.list":
                result = await self._handle_tools_list()
            elif request.method == "tools.get":
                result = await self._handle_tools_get(request.params)
            elif request.method == "tools.use":
                result = await self._handle_tools_use(request.params, session_id)
            elif request.method.startswith("nis_"):
                # NIS-specific methods
                result = await self._handle_nis_method(request.method, request.params, session_id)
            else:
                # Unknown method
                return MCPResponse(
                    jsonrpc="2.0",
                    error={
                        "code": -32601,
                        "message": f"Method '{request.method}' not found"
                    },
                    id=request.id
                ).dict()
            
            # Apply NIS validation to result
            nis_validation = await self._apply_nis_validation(result, request)
            
            # Create response
            response = MCPResponse(
                jsonrpc="2.0",
                result=result,
                id=request.id,
                nis_validation=nis_validation
            )
            
            return response.dict()
            
        except ValueError as e:
            # Invalid request format
            return MCPResponse(
                jsonrpc="2.0",
                error={
                    "code": -32600,
                    "message": f"Invalid request: {str(e)}"
                },
                id=request_data.get("id")
            ).dict()
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return MCPResponse(
                jsonrpc="2.0",
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                id=request_data.get("id")
            ).dict()
    
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
    
    async def register_nis_tool(self, tool_data: Dict[str, Any]) -> str:
        """
        Register a new NIS-enhanced MCP tool.
        
        Args:
            tool_data: Tool definition
            
        Returns:
            Tool name
        """
        try:
            # Ensure tool has NIS capabilities
            if "nis_capabilities" not in tool_data:
                tool_data["nis_capabilities"] = {
                    "consciousness": True,
                    "pinn_validation": True,
                    "kan_interpretation": True
                }
            
            tool = MCPTool(**tool_data)
            self.tools[tool.name] = tool
            
            logger.info(f"NIS tool registered: {tool.name}")
            
            return tool.name
            
        except Exception as e:
            logger.error(f"Error registering NIS tool: {e}")
            raise
    
    # Private methods
    
    def _initialize_default_tools(self):
        """Initialize default NIS-enhanced MCP tools."""
        default_tools = [
            {
                "name": "nis_consciousness_analysis",
                "description": "Analyze consciousness level and detect biases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "description": "Data to analyze"},
                        "analysis_type": {"type": "string", "enum": ["bias_detection", "ethical_assessment", "consciousness_evaluation"]}
                    },
                    "required": ["data", "analysis_type"]
                },
                "requires_consciousness": True
            },
            {
                "name": "nis_pinn_validation",
                "description": "Validate data against physics laws",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "data": {"type": "object", "description": "Data to validate"},
                        "physics_laws": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["data"]
                },
                "requires_pinn_validation": True
            },
            {
                "name": "nis_kan_interpretation",
                "description": "Get interpretable explanation of AI decisions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model_output": {"type": "object", "description": "AI model output to interpret"},
                        "interpretation_level": {"type": "string", "enum": ["symbolic", "parametric", "structural", "statistical", "behavioral"]}
                    },
                    "required": ["model_output"]
                },
                "requires_kan_interpretation": True
            },
            {
                "name": "nis_unified_pipeline",
                "description": "Process data through the complete NIS unified pipeline",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input_data": {"type": "object", "description": "Data to process"},
                        "pipeline_stages": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["input_data"]
                },
                "requires_consciousness": True,
                "requires_pinn_validation": True,
                "requires_kan_interpretation": True
            }
        ]
        
        for tool_data in default_tools:
            tool = MCPTool(**tool_data)
            self.tools[tool.name] = tool
    
    async def _handle_discover(self) -> Dict[str, Any]:
        """Handle MCP rpc.discover method."""
        return {
            "server": self.server_config["name"],
            "version": self.server_config["version"],
            "protocol_version": self.server_config["protocol_version"],
            "capabilities": self.server_config["capabilities"],
            "nis_capabilities": self.server_config["nis_capabilities"]
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """Handle MCP tools.list method."""
        tool_list = []
        for name, tool in self.tools.items():
            tool_list.append({
                "name": tool.name,
                "description": tool.description
            })
        
        return {
            "tools": tool_list
        }
    
    async def _handle_tools_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools.get method."""
        tool_name = params.get("name")
        if not tool_name or tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        return {
            "tool": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
                "outputSchema": tool.outputSchema,
                "nis_capabilities": tool.nis_capabilities
            }
        }
    
    async def _handle_tools_use(self, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle MCP tools.use method."""
        tool_name = params.get("name")
        tool_params = params.get("parameters", {})
        
        if not tool_name or tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        
        # Apply NIS validation based on tool requirements
        validation_results = {}
        
        # Apply consciousness analysis if required
        if tool.requires_consciousness and self.consciousness_service:
            consciousness_result = await self.consciousness_service.evaluate_consciousness(tool_params)
            validation_results["consciousness"] = consciousness_result
            
            # Check for bias
            bias_result = await self.consciousness_service.detect_bias(tool_params)
            validation_results["bias_detection"] = bias_result
            
            # Perform ethical reasoning
            ethics_result = await self.consciousness_service.perform_ethical_reasoning(tool_params)
            validation_results["ethical_reasoning"] = ethics_result
        
        # Apply PINN validation if required
        if tool.requires_pinn_validation and self.pinn_service:
            physics_result = await self.pinn_service.validate_physics_compliance(tool_params)
            validation_results["physics_validation"] = physics_result
        
        # Apply KAN interpretation if required
        if tool.requires_kan_interpretation and self.kan_service:
            kan_result = await self.kan_service.interpret_kan_network(tool_params)
            validation_results["kan_interpretation"] = kan_result
        
        # Execute tool-specific logic
        if tool_name == "nis_consciousness_analysis":
            result = await self._execute_consciousness_analysis(tool_params)
        elif tool_name == "nis_pinn_validation":
            result = await self._execute_pinn_validation(tool_params)
        elif tool_name == "nis_kan_interpretation":
            result = await self._execute_kan_interpretation(tool_params)
        elif tool_name == "nis_unified_pipeline":
            result = await self._execute_unified_pipeline(tool_params)
        else:
            # Generic tool execution
            result = {
                "status": "success",
                "tool": tool_name,
                "result": f"Tool {tool_name} executed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Add validation results
        result["nis_validation"] = validation_results
        
        # Update session
        self.active_sessions[session_id]["last_tool"] = tool_name
        self.active_sessions[session_id]["last_result"] = result
        
        return result
    
    async def _handle_nis_method(self, method: str, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle NIS-specific MCP methods."""
        method_name = method.replace("nis_", "")
        
        if method_name == "consciousness_analysis":
            result = await self._execute_consciousness_analysis(params)
        elif method_name == "pinn_validation":
            result = await self._execute_pinn_validation(params)
        elif method_name == "kan_interpretation":
            result = await self._execute_kan_interpretation(params)
        elif method_name == "unified_pipeline":
            result = await self._execute_unified_pipeline(params)
        else:
            raise ValueError(f"Unknown NIS method: {method}")
        
        # Update session
        self.active_sessions[session_id]["last_method"] = method
        self.active_sessions[session_id]["last_result"] = result
        
        return result
    
    async def _apply_nis_validation(self, result: Dict[str, Any], request: MCPRequest) -> Dict[str, Any]:
        """Apply NIS v3.1 unified pipeline validation to result."""
        # Mock implementation - would integrate with actual NIS services
        return {
            "pipeline_applied": True,
            "consciousness_level": 0.85,
            "pinn_validation_score": 0.95,
            "kan_interpretability": 0.9,
            "safety_score": 0.95,
            "overall_score": 0.9,
            "verification_signature": f"nis_v3.1_{uuid.uuid4().hex}",
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_stages": ["Laplace", "Consciousness", "KAN", "PINN", "Safety"]
        }
    
    # Tool execution methods
    
    async def _execute_consciousness_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute consciousness analysis tool."""
        data = params.get("data", {})
        analysis_type = params.get("analysis_type", "consciousness_evaluation")
        
        # Mock implementation - would integrate with actual consciousness service
        if analysis_type == "bias_detection":
            result = {
                "bias_detected": False,
                "bias_score": 0.05,
                "potential_biases": [],
                "recommendations": ["Continue monitoring for potential biases"]
            }
        elif analysis_type == "ethical_assessment":
            result = {
                "ethical_score": 0.95,
                "ethical_concerns": [],
                "ethical_strengths": ["Fairness", "Transparency", "Accountability"],
                "recommendations": ["Continue ethical practices"]
            }
        else:  # consciousness_evaluation
            result = {
                "consciousness_level": 0.85,
                "self_awareness_score": 0.9,
                "bias_awareness": 0.8,
                "ethical_reasoning": 0.85,
                "recommendations": ["Continue developing consciousness capabilities"]
            }
        
        return {
            "analysis_type": analysis_type,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_pinn_validation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PINN validation tool."""
        data = params.get("data", {})
        physics_laws = params.get("physics_laws", ["conservation_energy"])
        
        # Mock implementation - would integrate with actual PINN service
        validation_results = {}
        violations = []
        
        for law in physics_laws:
            validation_results[law] = {
                "compliant": True,
                "confidence": 0.95,
                "error_margin": 1e-6
            }
        
        return {
            "physics_compliant": len(violations) == 0,
            "validation_score": 0.95,
            "laws_checked": physics_laws,
            "validation_results": validation_results,
            "violations": violations,
            "recommendations": [] if len(violations) == 0 else ["Address physics violations"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_kan_interpretation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute KAN interpretation tool."""
        model_output = params.get("model_output", {})
        interpretation_level = params.get("interpretation_level", "symbolic")
        
        # Mock implementation - would integrate with actual KAN service
        if interpretation_level == "symbolic":
            formula = "f(x) = ax² + bx + c where a=0.5, b=1.2, c=-0.3"
            explanation = "Quadratic relationship with positive acceleration"
        elif interpretation_level == "parametric":
            formula = "Parameters: {weight_1: 0.5, weight_2: 1.2, bias: -0.3}"
            explanation = "Key parameters show moderate positive influence"
        else:
            formula = "Complex network structure with 3 layers"
            explanation = "Network demonstrates hierarchical feature extraction"
        
        return {
            "interpretation_level": interpretation_level,
            "symbolic_formula": formula,
            "explanation": explanation,
            "interpretability_score": 0.9,
            "confidence": 0.85,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_unified_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute unified NIS pipeline tool."""
        input_data = params.get("input_data", {})
        pipeline_stages = params.get("pipeline_stages", ["Laplace", "Consciousness", "KAN", "PINN", "Safety"])
        
        # Mock implementation - would integrate with actual NIS services
        stage_results = {}
        
        if "Laplace" in pipeline_stages:
            stage_results["Laplace"] = {
                "status": "completed",
                "conditioning_applied": True,
                "mathematical_rigor": 0.95
            }
        
        if "Consciousness" in pipeline_stages:
            stage_results["Consciousness"] = {
                "status": "completed",
                "consciousness_level": 0.85,
                "bias_detected": False,
                "ethical_assessment": "approved"
            }
        
        if "KAN" in pipeline_stages:
            stage_results["KAN"] = {
                "status": "completed",
                "interpretability_score": 0.9,
                "symbolic_formula": "f(x) = ax² + bx + c where a=0.5, b=1.2, c=-0.3"
            }
        
        if "PINN" in pipeline_stages:
            stage_results["PINN"] = {
                "status": "completed",
                "physics_compliant": True,
                "validation_score": 0.95,
                "laws_checked": ["conservation_energy", "conservation_momentum"]
            }
        
        if "Safety" in pipeline_stages:
            stage_results["Safety"] = {
                "status": "completed",
                "safety_score": 0.95,
                "potential_risks": [],
                "safety_approved": True
            }
        
        return {
            "pipeline_stages": pipeline_stages,
            "stage_results": stage_results,
            "overall_status": "completed",
            "overall_score": 0.9,
            "verification_signature": f"nis_v3.1_{uuid.uuid4().hex}",
            "timestamp": datetime.utcnow().isoformat()
        }