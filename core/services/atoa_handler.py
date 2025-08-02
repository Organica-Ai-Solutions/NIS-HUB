"""
ATOA (Agent-to-Operator-to-Agent) Workflow Handler for NIS HUB v3.1

Implements a dedicated handler for ATOA workflows, enabling seamless 
agent-to-operator-to-agent communication with consciousness validation,
physics compliance checks, and human oversight integration.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
import uuid
from enum import Enum
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    """Types of agents in ATOA workflows."""
    NIS_AGENT = "nis_agent"
    EXTERNAL_AGENT = "external_agent"
    HUMAN_OPERATOR = "human_operator"
    BITNET_AGENT = "bitnet_agent"
    CONSCIOUSNESS_AGENT = "consciousness_agent"
    PINN_VALIDATOR = "pinn_validator"
    KAN_PROCESSOR = "kan_processor"
    SYSTEM = "system"

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

class WorkflowStatus(str, Enum):
    """Status of ATOA workflows."""
    INITIATED = "initiated"
    AWAITING_OPERATOR = "awaiting_operator"
    AWAITING_AGENT = "awaiting_agent"
    CONSCIOUSNESS_REVIEW = "consciousness_review"
    PHYSICS_VALIDATION = "physics_validation"
    SAFETY_VALIDATION = "safety_validation"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ERROR = "error"
    CANCELLED = "cancelled"

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

class ConsciousnessAssessment(BaseModel):
    """Consciousness assessment result structure."""
    consciousness_level: float = Field(..., ge=0, le=1)
    bias_detected: bool = False
    bias_details: Optional[Dict[str, Any]] = None
    ethical_concerns: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    self_awareness_score: float = Field(..., ge=0, le=1)
    
    class Config:
        validate_assignment = True

class PhysicsValidation(BaseModel):
    """Physics validation result structure."""
    physics_compliant: bool = True
    validation_score: float = Field(..., ge=0, le=1)
    laws_checked: List[str] = Field(default_factory=list)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    
    class Config:
        validate_assignment = True

class OperatorReview(BaseModel):
    """Human operator review result structure."""
    review_requested: bool = True
    approved: bool = False
    operator_comments: Optional[str] = None
    review_time: Optional[datetime] = None
    modified_content: Optional[Dict[str, Any]] = None
    
    class Config:
        validate_assignment = True

class ATOAWorkflow(BaseModel):
    """Complete ATOA workflow structure."""
    workflow_id: str = Field(default_factory=lambda: f"atoa_{uuid.uuid4().hex[:8]}")
    initiating_message: ATOAMessage
    status: WorkflowStatus = WorkflowStatus.INITIATED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Workflow stages
    consciousness_assessment: Optional[ConsciousnessAssessment] = None
    physics_validation: Optional[PhysicsValidation] = None
    operator_review: Optional[OperatorReview] = None
    
    # Messages in workflow
    messages: List[ATOAMessage] = Field(default_factory=list)
    
    # Final result
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True

class ATOAHandler:
    """Handler for Agent-to-Operator-to-Agent workflows with NIS v3.1 validation."""
    
    def __init__(self, 
                 consciousness_service=None, 
                 pinn_service=None, 
                 kan_service=None, 
                 websocket_manager=None,
                 redis_service=None):
        """Initialize the ATOA handler."""
        self.consciousness_service = consciousness_service
        self.pinn_service = pinn_service
        self.kan_service = kan_service
        self.websocket_manager = websocket_manager
        self.redis_service = redis_service
        
        # Active workflows
        self.active_workflows: Dict[str, ATOAWorkflow] = {}
        
        # Operator callbacks
        self.operator_callbacks: Dict[str, Callable] = {}
        
        # Agent callbacks
        self.agent_callbacks: Dict[str, Dict[str, Callable]] = {}
        
        logger.info("🤝 ATOA Workflow Handler initialized")
    
    async def initiate_workflow(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a new ATOA workflow.
        
        Args:
            message: Initial ATOA message
            
        Returns:
            Workflow information
        """
        try:
            # Parse and validate message
            atoa_message = ATOAMessage(**message)
            
            # Create workflow
            workflow = ATOAWorkflow(
                initiating_message=atoa_message,
                status=WorkflowStatus.INITIATED
            )
            
            # Add message to workflow
            workflow.messages.append(atoa_message)
            
            # Store workflow
            self.active_workflows[workflow.workflow_id] = workflow
            
            # Set workflow ID in message
            atoa_message.workflow_id = workflow.workflow_id
            
            # Start workflow processing
            asyncio.create_task(self._process_workflow(workflow.workflow_id))
            
            logger.info(f"ATOA workflow initiated: {workflow.workflow_id}")
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "created_at": workflow.created_at.isoformat(),
                "message_id": atoa_message.message_id
            }
            
        except Exception as e:
            logger.error(f"Error initiating ATOA workflow: {e}")
            raise
    
    async def add_message_to_workflow(self, 
                                    workflow_id: str, 
                                    message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a message to an existing workflow.
        
        Args:
            workflow_id: Workflow identifier
            message: ATOA message
            
        Returns:
            Updated workflow information
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        try:
            # Parse and validate message
            atoa_message = ATOAMessage(**message)
            
            # Set workflow ID in message
            atoa_message.workflow_id = workflow_id
            
            # Add message to workflow
            workflow.messages.append(atoa_message)
            workflow.updated_at = datetime.utcnow()
            
            # Update workflow status based on message type
            if atoa_message.message_type == MessageType.APPROVAL:
                if workflow.status == WorkflowStatus.AWAITING_OPERATOR:
                    # Operator approved
                    workflow.status = WorkflowStatus.AWAITING_AGENT
                    
                    # Update operator review
                    if workflow.operator_review:
                        workflow.operator_review.approved = True
                        workflow.operator_review.review_time = datetime.utcnow()
                        workflow.operator_review.operator_comments = atoa_message.content.get("comments")
                    
                    # Continue workflow processing
                    asyncio.create_task(self._process_workflow(workflow_id))
            
            elif atoa_message.message_type == MessageType.REJECTION:
                if workflow.status == WorkflowStatus.AWAITING_OPERATOR:
                    # Operator rejected
                    workflow.status = WorkflowStatus.REJECTED
                    
                    # Update operator review
                    if workflow.operator_review:
                        workflow.operator_review.approved = False
                        workflow.operator_review.review_time = datetime.utcnow()
                        workflow.operator_review.operator_comments = atoa_message.content.get("comments")
                    
                    # Complete workflow
                    await self._complete_workflow(workflow_id, "rejected")
            
            elif atoa_message.message_type == MessageType.RESPONSE:
                if workflow.status == WorkflowStatus.AWAITING_AGENT:
                    # Target agent responded
                    workflow.status = WorkflowStatus.COMPLETED
                    
                    # Complete workflow
                    await self._complete_workflow(workflow_id, "completed", atoa_message.content)
            
            elif atoa_message.message_type == MessageType.CONSCIOUSNESS_ALERT:
                # Consciousness issue detected
                workflow.status = WorkflowStatus.CONSCIOUSNESS_REVIEW
                
                # Force operator review
                workflow.initiating_message.requires_human_approval = True
                
                # Continue workflow processing
                asyncio.create_task(self._process_workflow(workflow_id))
            
            elif atoa_message.message_type == MessageType.PHYSICS_VIOLATION:
                # Physics violation detected
                workflow.status = WorkflowStatus.PHYSICS_VALIDATION
                
                # Force operator review
                workflow.initiating_message.requires_human_approval = True
                
                # Continue workflow processing
                asyncio.create_task(self._process_workflow(workflow_id))
            
            logger.info(f"Message added to ATOA workflow: {workflow_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": workflow.status,
                "updated_at": workflow.updated_at.isoformat(),
                "message_count": len(workflow.messages)
            }
            
        except Exception as e:
            logger.error(f"Error adding message to ATOA workflow: {e}")
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of an ATOA workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status information
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "message_count": len(workflow.messages),
            "initiating_agent": workflow.initiating_message.agent_id,
            "target_agent": workflow.initiating_message.target_agent_id,
            "operator_id": workflow.initiating_message.operator_id,
            "requires_human_approval": workflow.initiating_message.requires_human_approval,
            "ethical_review_required": workflow.initiating_message.ethical_review_required,
            "physics_validation_required": workflow.initiating_message.physics_validation_required
        }
    
    async def register_operator_callback(self, 
                                       operator_id: str, 
                                       callback: Callable) -> None:
        """
        Register a callback for operator notifications.
        
        Args:
            operator_id: Operator identifier
            callback: Callback function
        """
        self.operator_callbacks[operator_id] = callback
        logger.info(f"Operator callback registered: {operator_id}")
    
    async def register_agent_callback(self, 
                                    agent_id: str, 
                                    callback: Callable) -> None:
        """
        Register a callback for agent notifications.
        
        Args:
            agent_id: Agent identifier
            callback: Callback function
        """
        self.agent_callbacks[agent_id] = callback
        logger.info(f"Agent callback registered: {agent_id}")
    
    async def handle_atoa_workflow(self,
                                 agent_request: Dict[str, Any],
                                 operator_oversight: bool = True) -> Dict[str, Any]:
        """
        Handle complete Agent-to-Operator-to-Agent workflow with NIS v3.1 validation.
        
        Args:
            agent_request: Request from initiating agent
            operator_oversight: Whether human operator oversight is required
            
        Returns:
            Workflow result with all validations
        """
        try:
            # Initiate workflow
            workflow_info = await self.initiate_workflow(agent_request)
            workflow_id = workflow_info["workflow_id"]
            
            # Wait for workflow completion
            while True:
                workflow_status = await self.get_workflow_status(workflow_id)
                
                if workflow_status["status"] in [
                    WorkflowStatus.COMPLETED,
                    WorkflowStatus.REJECTED,
                    WorkflowStatus.ERROR,
                    WorkflowStatus.CANCELLED
                ]:
                    break
                
                await asyncio.sleep(0.5)
            
            # Get final workflow
            workflow = self.active_workflows[workflow_id]
            
            # Prepare result
            result = {
                "workflow_id": workflow_id,
                "status": workflow.status,
                "created_at": workflow.created_at.isoformat(),
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "stages": {},
                "result": workflow.result,
                "error": workflow.error
            }
            
            # Add stage results
            if workflow.consciousness_assessment:
                result["stages"]["consciousness_assessment"] = workflow.consciousness_assessment.dict()
            
            if workflow.physics_validation:
                result["stages"]["physics_validation"] = workflow.physics_validation.dict()
            
            if workflow.operator_review:
                result["stages"]["operator_review"] = workflow.operator_review.dict()
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling ATOA workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Private methods
    
    async def _process_workflow(self, workflow_id: str) -> None:
        """
        Process an ATOA workflow through all stages.
        
        Args:
            workflow_id: Workflow identifier
        """
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found for processing")
            return
        
        workflow = self.active_workflows[workflow_id]
        
        try:
            # Stage 1: Consciousness assessment of agent request
            if workflow.initiating_message.ethical_review_required and not workflow.consciousness_assessment:
                workflow.status = WorkflowStatus.CONSCIOUSNESS_REVIEW
                consciousness_result = await self._assess_agent_consciousness(workflow.initiating_message)
                workflow.consciousness_assessment = ConsciousnessAssessment(**consciousness_result)
                
                # Check if human review required based on consciousness assessment
                if workflow.consciousness_assessment.requires_human_review:
                    workflow.initiating_message.requires_human_approval = True
                    
                    # Notify via WebSocket if available
                    if self.websocket_manager:
                        await self.websocket_manager.send_consciousness_alert({
                            "workflow_id": workflow_id,
                            "consciousness_assessment": consciousness_result,
                            "message": "Consciousness assessment requires human review"
                        })
            
            # Stage 2: Physics validation if required
            if workflow.initiating_message.physics_validation_required and not workflow.physics_validation:
                workflow.status = WorkflowStatus.PHYSICS_VALIDATION
                physics_result = await self._validate_agent_request_physics(workflow.initiating_message)
                workflow.physics_validation = PhysicsValidation(**physics_result)
                
                # Check for physics violations
                if not workflow.physics_validation.physics_compliant:
                    workflow.initiating_message.requires_human_approval = True
                    
                    # Notify via WebSocket if available
                    if self.websocket_manager:
                        await self.websocket_manager.send_pinn_validation_result({
                            "workflow_id": workflow_id,
                            "physics_validation": physics_result,
                            "message": "Physics validation failed, human review required"
                        })
            
            # Stage 3: Operator review if required
            if workflow.initiating_message.requires_human_approval and not workflow.operator_review:
                workflow.status = WorkflowStatus.AWAITING_OPERATOR
                operator_review = await self._request_operator_review(workflow.initiating_message, workflow_id)
                workflow.operator_review = OperatorReview(**operator_review)
                
                # If operator review is synchronous and rejected, complete workflow
                if not workflow.operator_review.approved and workflow.operator_review.review_time:
                    workflow.status = WorkflowStatus.REJECTED
                    await self._complete_workflow(workflow_id, "rejected")
                    return
            
            # Stage 4: Execute agent-to-agent communication if approved
            if (not workflow.initiating_message.requires_human_approval or 
                (workflow.operator_review and workflow.operator_review.approved)):
                
                if workflow.initiating_message.target_agent_id:
                    workflow.status = WorkflowStatus.AWAITING_AGENT
                    agent_communication = await self._facilitate_agent_communication(workflow.initiating_message)
                    
                    # If agent communication is synchronous, complete workflow
                    if "response" in agent_communication:
                        workflow.status = WorkflowStatus.COMPLETED
                        await self._complete_workflow(workflow_id, "completed", agent_communication["response"])
            
            # Update workflow
            workflow.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing ATOA workflow {workflow_id}: {e}")
            workflow.status = WorkflowStatus.ERROR
            workflow.error = str(e)
            await self._complete_workflow(workflow_id, "error")
    
    async def _assess_agent_consciousness(self, message: ATOAMessage) -> Dict[str, Any]:
        """Assess consciousness aspects of agent request."""
        try:
            if self.consciousness_service:
                # Use actual consciousness service if available
                consciousness_result = await self.consciousness_service.evaluate_consciousness(message.content)
                bias_result = await self.consciousness_service.detect_bias(message.content)
                ethics_result = await self.consciousness_service.perform_ethical_reasoning(message.content)
                
                return {
                    "consciousness_level": consciousness_result.get("consciousness_level", 0.8),
                    "bias_detected": bias_result.get("bias_detected", False),
                    "bias_details": bias_result.get("details"),
                    "ethical_concerns": ethics_result.get("concerns", []),
                    "requires_human_review": (
                        bias_result.get("bias_detected", False) or 
                        len(ethics_result.get("concerns", [])) > 0
                    ),
                    "self_awareness_score": consciousness_result.get("self_awareness", 0.8)
                }
            else:
                # Mock implementation
                return {
                    "consciousness_level": 0.8,
                    "bias_detected": False,
                    "bias_details": None,
                    "ethical_concerns": [],
                    "requires_human_review": False,
                    "self_awareness_score": 0.85
                }
        except Exception as e:
            logger.error(f"Error in consciousness assessment: {e}")
            return {
                "consciousness_level": 0.5,
                "bias_detected": True,
                "bias_details": {"error": str(e)},
                "ethical_concerns": ["Assessment error"],
                "requires_human_review": True,
                "self_awareness_score": 0.5
            }
    
    async def _validate_agent_request_physics(self, message: ATOAMessage) -> Dict[str, Any]:
        """Validate physics aspects of agent request."""
        try:
            if self.pinn_service:
                # Use actual PINN service if available
                physics_result = await self.pinn_service.validate_physics_compliance(message.content)
                
                return {
                    "physics_compliant": physics_result.get("compliant", True),
                    "validation_score": physics_result.get("score", 0.95),
                    "laws_checked": physics_result.get("laws_checked", ["conservation_energy"]),
                    "violations": physics_result.get("violations", []),
                    "confidence": physics_result.get("confidence", 0.9)
                }
            else:
                # Mock implementation
                return {
                    "physics_compliant": True,
                    "validation_score": 0.95,
                    "laws_checked": ["conservation_energy", "conservation_momentum"],
                    "violations": [],
                    "confidence": 0.9
                }
        except Exception as e:
            logger.error(f"Error in physics validation: {e}")
            return {
                "physics_compliant": False,
                "validation_score": 0.5,
                "laws_checked": [],
                "violations": [{"error": str(e)}],
                "confidence": 0.5
            }
    
    async def _request_operator_review(self, message: ATOAMessage, workflow_id: str) -> Dict[str, Any]:
        """Request human operator review."""
        try:
            operator_id = message.operator_id
            
            # Prepare review request
            review_request = {
                "workflow_id": workflow_id,
                "message_id": message.message_id,
                "agent_id": message.agent_id,
                "content": message.content,
                "urgency": message.urgency,
                "timestamp": message.timestamp.isoformat(),
                "review_requested_at": datetime.utcnow().isoformat()
            }
            
            # Add consciousness assessment if available
            workflow = self.active_workflows[workflow_id]
            if workflow.consciousness_assessment:
                review_request["consciousness_assessment"] = workflow.consciousness_assessment.dict()
            
            # Add physics validation if available
            if workflow.physics_validation:
                review_request["physics_validation"] = workflow.physics_validation.dict()
            
            # Notify operator via callback if registered
            if operator_id and operator_id in self.operator_callbacks:
                asyncio.create_task(self.operator_callbacks[operator_id](review_request))
            
            # Notify via WebSocket if available
            if self.websocket_manager:
                await self.websocket_manager.broadcast({
                    "type": "operator_review_request",
                    "data": review_request
                })
            
            # Store in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"atoa:review:{workflow_id}", 
                    json.dumps(review_request),
                    expire=86400  # 24 hours
                )
            
            # In this implementation, we return immediately with review_requested=True
            # but approved=False, as the operator will need to respond asynchronously
            return {
                "review_requested": True,
                "approved": False,
                "operator_comments": None,
                "review_time": None,
                "modified_content": None
            }
            
        except Exception as e:
            logger.error(f"Error requesting operator review: {e}")
            return {
                "review_requested": True,
                "approved": False,
                "operator_comments": f"Error: {str(e)}",
                "review_time": datetime.utcnow().isoformat(),
                "modified_content": None
            }
    
    async def _facilitate_agent_communication(self, message: ATOAMessage) -> Dict[str, Any]:
        """Facilitate communication between agents."""
        try:
            target_agent_id = message.target_agent_id
            
            if not target_agent_id:
                return {
                    "communication_established": False,
                    "error": "No target agent specified",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Prepare agent message
            agent_message = {
                "source_agent_id": message.agent_id,
                "message_id": message.message_id,
                "content": message.content,
                "urgency": message.urgency,
                "timestamp": message.timestamp.isoformat(),
                "workflow_id": message.workflow_id
            }
            
            # Add consciousness assessment if available
            workflow = self.active_workflows[message.workflow_id]
            if workflow.consciousness_assessment:
                agent_message["consciousness_assessment"] = workflow.consciousness_assessment.dict()
            
            # Add physics validation if available
            if workflow.physics_validation:
                agent_message["physics_validation"] = workflow.physics_validation.dict()
            
            # Notify target agent via callback if registered
            response = None
            if target_agent_id in self.agent_callbacks:
                response = await self.agent_callbacks[target_agent_id](agent_message)
            
            # Notify via WebSocket if available
            if self.websocket_manager:
                await self.websocket_manager.broadcast({
                    "type": "agent_communication",
                    "data": agent_message
                })
            
            # Store in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"atoa:communication:{message.workflow_id}", 
                    json.dumps(agent_message),
                    expire=86400  # 24 hours
                )
            
            return {
                "communication_established": True,
                "message_delivered": True,
                "response_received": response is not None,
                "response": response,
                "communication_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error facilitating agent communication: {e}")
            return {
                "communication_established": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _complete_workflow(self, 
                               workflow_id: str, 
                               status: str,
                               result: Optional[Dict[str, Any]] = None) -> None:
        """Complete an ATOA workflow."""
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found for completion")
            return
        
        workflow = self.active_workflows[workflow_id]
        
        # Update workflow status
        if status == "completed":
            workflow.status = WorkflowStatus.COMPLETED
        elif status == "rejected":
            workflow.status = WorkflowStatus.REJECTED
        elif status == "error":
            workflow.status = WorkflowStatus.ERROR
        else:
            workflow.status = WorkflowStatus.CANCELLED
        
        # Set completion time
        workflow.completed_at = datetime.utcnow()
        
        # Set result if provided
        if result:
            workflow.result = result
        
        # Notify via WebSocket if available
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "workflow_completed",
                "data": {
                    "workflow_id": workflow_id,
                    "status": workflow.status,
                    "completed_at": workflow.completed_at.isoformat(),
                    "result": workflow.result,
                    "error": workflow.error
                }
            })
        
        # Store in Redis if available
        if self.redis_service:
            await self.redis_service.set(
                f"atoa:completed:{workflow_id}", 
                json.dumps({
                    "workflow_id": workflow_id,
                    "status": workflow.status,
                    "completed_at": workflow.completed_at.isoformat(),
                    "result": workflow.result,
                    "error": workflow.error
                }),
                expire=86400  # 24 hours
            )
        
        logger.info(f"ATOA workflow completed: {workflow_id} (status: {status})")