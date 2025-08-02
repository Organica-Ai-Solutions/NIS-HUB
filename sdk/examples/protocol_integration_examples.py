"""
NIS HUB SDK - Protocol Integration Examples

This module demonstrates how to use the NIS HUB SDK's protocol integration
capabilities to communicate with external protocols like MCP, ATOA, and OpenAI Tools.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from nis_hub_sdk import NISNode, ProtocolBridge, ProtocolType, MessageType, UrgencyLevel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Example 1: Model Context Protocol (MCP) Integration
async def mcp_integration_example():
    """Demonstrate MCP integration with NIS HUB."""
    logger.info("=== MCP Integration Example ===")
    
    # Initialize NIS Node
    node = NISNode(
        name="MCP Integration Example",
        node_type="EXTERNAL_AGENT",
        capabilities=["MCP_INTEGRATION", "CONSCIOUSNESS"]
    )
    
    # Connect to NIS HUB
    await node.connect()
    logger.info(f"Connected to NIS HUB as node: {node.node_id}")
    
    # Initialize Protocol Bridge
    protocol_bridge = ProtocolBridge(node=node)
    
    try:
        # Register MCP protocol
        bridge_id = await protocol_bridge.register_protocol(
            protocol=ProtocolType.MCP,
            endpoint="http://mcp-server:8080",
            configuration={
                "tools": ["nis_consciousness_analysis", "nis_pinn_validation", "nis_kan_interpretation"]
            }
        )
        logger.info(f"MCP protocol registered with bridge ID: {bridge_id}")
        
        # Create and send MCP request for consciousness analysis
        response = await protocol_bridge.send_mcp_request(
            bridge_id=bridge_id,
            method="nis_consciousness_analysis",
            params={
                "data": {
                    "text": "AI systems should be designed with ethical considerations in mind.",
                    "context": "AI ethics discussion"
                },
                "analysis_type": "bias_detection"
            }
        )
        
        # Print response with NIS validation
        logger.info(f"MCP Response: {json.dumps(response, indent=2)}")
        
        # Check NIS validation results
        if "nis_validation" in response:
            validation = response["nis_validation"]
            logger.info(f"Consciousness Level: {validation.get('consciousness_level', 'N/A')}")
            logger.info(f"PINN Validation Score: {validation.get('pinn_validation_score', 'N/A')}")
            logger.info(f"KAN Interpretability: {validation.get('kan_interpretability', 'N/A')}")
            logger.info(f"Safety Score: {validation.get('safety_score', 'N/A')}")
        
        # Get protocol status
        status = await protocol_bridge.get_protocol_status(bridge_id)
        logger.info(f"Protocol Status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in MCP integration: {e}")
    
    finally:
        # Disconnect node
        await node.disconnect()
        await protocol_bridge.close()

# Example 2: Agent-to-Operator-to-Agent (ATOA) Workflow
async def atoa_workflow_example():
    """Demonstrate ATOA workflow with NIS HUB."""
    logger.info("=== ATOA Workflow Example ===")
    
    # Initialize NIS Node
    node = NISNode(
        name="ATOA Workflow Example",
        node_type="EXTERNAL_AGENT",
        capabilities=["ATOA_WORKFLOW", "CONSCIOUSNESS", "PHYSICS_VALIDATION"]
    )
    
    # Connect to NIS HUB
    await node.connect()
    logger.info(f"Connected to NIS HUB as node: {node.node_id}")
    
    # Initialize Protocol Bridge
    protocol_bridge = ProtocolBridge(node=node)
    
    try:
        # Create ATOA message
        message = await protocol_bridge.create_atoa_message(
            agent_id=node.node_id,
            message_type=MessageType.REQUEST,
            content={
                "task": "analyze_data",
                "data": {
                    "temperature": 25.5,
                    "pressure": 101.3,
                    "volume": 2.5
                },
                "analysis_type": "thermodynamics"
            },
            target_agent_id="physics_agent_001",
            operator_id="human_operator_001",
            requires_human_approval=True,
            urgency=UrgencyLevel.NORMAL,
            ethical_review_required=True,
            physics_validation_required=True
        )
        logger.info(f"ATOA message created: {json.dumps(message, indent=2)}")
        
        # Initiate ATOA workflow
        workflow = await protocol_bridge.initiate_atoa_workflow(message)
        workflow_id = workflow["workflow_id"]
        logger.info(f"ATOA workflow initiated: {workflow_id}")
        
        # Add operator approval message
        approval_message = await protocol_bridge.create_atoa_message(
            agent_id="human_operator_001",
            message_type=MessageType.APPROVAL,
            content={
                "comments": "Request approved after review",
                "modifications": {}
            },
            target_agent_id="physics_agent_001"
        )
        
        await protocol_bridge.add_message_to_workflow(workflow_id, approval_message)
        logger.info("Operator approval added to workflow")
        
        # Get workflow status
        status = await protocol_bridge.get_workflow_status(workflow_id)
        logger.info(f"Workflow Status: {json.dumps(status, indent=2)}")
        
        # Handle complete workflow with timeout
        result = await protocol_bridge.handle_atoa_workflow(
            agent_request=message,
            operator_oversight=True,
            timeout=30
        )
        
        logger.info(f"ATOA Workflow Result: {json.dumps(result, indent=2)}")
        
        # Check consciousness assessment
        if "stages" in result and "consciousness_assessment" in result["stages"]:
            assessment = result["stages"]["consciousness_assessment"]
            logger.info(f"Consciousness Level: {assessment.get('consciousness_level', 'N/A')}")
            logger.info(f"Bias Detected: {assessment.get('bias_detected', 'N/A')}")
        
        # Check physics validation
        if "stages" in result and "physics_validation" in result["stages"]:
            validation = result["stages"]["physics_validation"]
            logger.info(f"Physics Compliant: {validation.get('physics_compliant', 'N/A')}")
            logger.info(f"Validation Score: {validation.get('validation_score', 'N/A')}")
            logger.info(f"Laws Checked: {validation.get('laws_checked', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Error in ATOA workflow: {e}")
    
    finally:
        # Disconnect node
        await node.disconnect()
        await protocol_bridge.close()

# Example 3: OpenAI Tools Integration
async def openai_tools_example():
    """Demonstrate OpenAI Tools integration with NIS HUB."""
    logger.info("=== OpenAI Tools Integration Example ===")
    
    # Initialize NIS Node
    node = NISNode(
        name="OpenAI Tools Example",
        node_type="EXTERNAL_AGENT",
        capabilities=["OPENAI_TOOLS", "CONSCIOUSNESS", "KAN_NETWORKS"]
    )
    
    # Connect to NIS HUB
    await node.connect()
    logger.info(f"Connected to NIS HUB as node: {node.node_id}")
    
    # Initialize Protocol Bridge
    protocol_bridge = ProtocolBridge(node=node)
    
    try:
        # Register OpenAI Tools protocol
        bridge_id = await protocol_bridge.register_protocol(
            protocol=ProtocolType.OPENAI_TOOLS,
            endpoint="https://api.openai.com/v1",
            authentication={
                "type": "bearer",
                "token": "YOUR_API_KEY"  # Replace with actual API key in production
            }
        )
        logger.info(f"OpenAI Tools protocol registered with bridge ID: {bridge_id}")
        
        # Create custom NIS-enhanced tool
        tool_definition = await protocol_bridge.create_openai_tool(
            name="nis_enhanced_analysis",
            description="Analyze data with NIS v3.1 unified pipeline validation",
            parameters={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Data to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["scientific", "financial", "medical", "environmental"],
                        "description": "Type of analysis to perform"
                    },
                    "validation_level": {
                        "type": "string",
                        "enum": ["basic", "consciousness", "physics", "full_pipeline"],
                        "description": "Level of NIS validation to apply"
                    }
                },
                "required": ["data", "analysis_type"]
            },
            nis_requirements={
                "requires_consciousness": True,
                "requires_pinn_validation": True,
                "requires_kan_interpretation": True,
                "requires_safety_check": True
            }
        )
        
        # Register tool with NIS HUB
        await protocol_bridge.register_openai_tool(tool_definition)
        logger.info("NIS-enhanced tool registered")
        
        # Create tool call
        tool_call = await protocol_bridge.create_tool_call(
            function_name="nis_enhanced_analysis",
            arguments={
                "data": {
                    "temperature": [25.5, 26.2, 24.8, 25.1, 25.9],
                    "pressure": [101.3, 101.5, 101.2, 101.4, 101.3],
                    "humidity": [45, 48, 42, 44, 47]
                },
                "analysis_type": "environmental",
                "validation_level": "full_pipeline"
            }
        )
        logger.info(f"Tool call created: {json.dumps(tool_call, indent=2)}")
        
        # Handle tool call
        result = await protocol_bridge.handle_tool_call(
            tool_call=tool_call,
            bridge_id=bridge_id,
            session_id=f"session_{datetime.utcnow().timestamp()}"
        )
        
        logger.info(f"Tool Call Result: {json.dumps(result, indent=2)}")
        
        # Parse output
        try:
            output = json.loads(result["output"])
            logger.info(f"Analysis Result: {json.dumps(output, indent=2)}")
        except:
            logger.info(f"Raw Output: {result['output']}")
        
        # Check NIS validation
        if "nis_validation" in result:
            validation = result["nis_validation"]
            
            if "consciousness" in validation:
                logger.info(f"Consciousness Assessment: {json.dumps(validation['consciousness'], indent=2)}")
            
            if "physics" in validation:
                logger.info(f"Physics Validation: {json.dumps(validation['physics'], indent=2)}")
            
            if "kan" in validation:
                logger.info(f"KAN Interpretation: {json.dumps(validation['kan'], indent=2)}")
            
            if "safety" in validation:
                logger.info(f"Safety Validation: {json.dumps(validation['safety'], indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in OpenAI Tools integration: {e}")
    
    finally:
        # Disconnect node
        await node.disconnect()
        await protocol_bridge.close()

# Example 4: Multi-Protocol Workflow
async def multi_protocol_workflow_example():
    """Demonstrate integration across multiple protocols with NIS HUB."""
    logger.info("=== Multi-Protocol Workflow Example ===")
    
    # Initialize NIS Node
    node = NISNode(
        name="Multi-Protocol Workflow Example",
        node_type="EXTERNAL_AGENT",
        capabilities=["MCP_INTEGRATION", "ATOA_WORKFLOW", "OPENAI_TOOLS", "UNIFIED_PIPELINE"]
    )
    
    # Connect to NIS HUB
    await node.connect()
    logger.info(f"Connected to NIS HUB as node: {node.node_id}")
    
    # Initialize Protocol Bridge
    protocol_bridge = ProtocolBridge(node=node)
    
    try:
        # Step 1: Register all protocols
        mcp_bridge_id = await protocol_bridge.register_protocol(
            protocol=ProtocolType.MCP,
            endpoint="http://mcp-server:8080"
        )
        
        atoa_bridge_id = await protocol_bridge.register_protocol(
            protocol=ProtocolType.ATOA,
            endpoint="ws://atoa-server:8081"
        )
        
        openai_bridge_id = await protocol_bridge.register_protocol(
            protocol=ProtocolType.OPENAI_TOOLS,
            endpoint="https://api.openai.com/v1"
        )
        
        logger.info(f"All protocols registered: MCP={mcp_bridge_id}, ATOA={atoa_bridge_id}, OpenAI={openai_bridge_id}")
        
        # Step 2: Start with MCP for consciousness analysis
        consciousness_response = await protocol_bridge.send_mcp_request(
            bridge_id=mcp_bridge_id,
            method="nis_consciousness_analysis",
            params={
                "data": {
                    "text": "Patient shows symptoms of high fever and respiratory distress.",
                    "context": "Medical diagnosis"
                },
                "analysis_type": "ethical_assessment"
            }
        )
        
        # Extract consciousness assessment
        consciousness_result = consciousness_response.get("result", {})
        logger.info(f"Consciousness Assessment: {json.dumps(consciousness_result, indent=2)}")
        
        # Step 3: Use OpenAI Tools for PINN validation
        tool_call = await protocol_bridge.create_tool_call(
            function_name="nis_pinn_validation",
            arguments={
                "data": {
                    "temperature": 39.5,  # High fever
                    "respiratory_rate": 28,  # Elevated
                    "oxygen_saturation": 92  # Slightly low
                },
                "physics_laws": ["biological_constraints", "thermodynamics_second"]
            }
        )
        
        pinn_result = await protocol_bridge.handle_tool_call(
            tool_call=tool_call,
            bridge_id=openai_bridge_id
        )
        
        # Parse PINN validation
        physics_validation = {}
        try:
            physics_output = json.loads(pinn_result["output"])
            physics_validation = physics_output
            logger.info(f"PINN Validation: {json.dumps(physics_output, indent=2)}")
        except:
            logger.info(f"PINN Raw Output: {pinn_result['output']}")
        
        # Step 4: Use ATOA for human operator review
        atoa_message = await protocol_bridge.create_atoa_message(
            agent_id=node.node_id,
            message_type=MessageType.REQUEST,
            content={
                "patient_data": {
                    "temperature": 39.5,
                    "respiratory_rate": 28,
                    "oxygen_saturation": 92
                },
                "consciousness_assessment": consciousness_result,
                "physics_validation": physics_validation,
                "diagnosis_suggestion": "Possible COVID-19 or pneumonia",
                "recommended_action": "Immediate medical attention required"
            },
            target_agent_id="medical_agent_001",
            operator_id="doctor_001",
            requires_human_approval=True,
            urgency=UrgencyLevel.HIGH,
            ethical_review_required=True,
            physics_validation_required=True
        )
        
        # Handle complete ATOA workflow
        workflow_result = await protocol_bridge.handle_atoa_workflow(
            agent_request=atoa_message,
            operator_oversight=True,
            timeout=60
        )
        
        logger.info(f"Multi-Protocol Workflow Result: {json.dumps(workflow_result, indent=2)}")
        
        # Final result with unified pipeline validation
        if workflow_result.get("status") == "completed" and workflow_result.get("result"):
            final_result = workflow_result["result"]
            logger.info(f"Final Diagnosis: {final_result.get('diagnosis')}")
            logger.info(f"Recommended Treatment: {final_result.get('treatment')}")
            logger.info(f"Validation Summary: {final_result.get('validation_summary')}")
        
    except Exception as e:
        logger.error(f"Error in multi-protocol workflow: {e}")
    
    finally:
        # Disconnect node
        await node.disconnect()
        await protocol_bridge.close()

# Main function to run all examples
async def main():
    """Run all protocol integration examples."""
    await mcp_integration_example()
    print("\n")
    
    await atoa_workflow_example()
    print("\n")
    
    await openai_tools_example()
    print("\n")
    
    await multi_protocol_workflow_example()

# Run examples
if __name__ == "__main__":
    asyncio.run(main())