#!/usr/bin/env python3
"""
NIS HUB Basic Node Example

This example demonstrates how to create a NIS node that connects to
the central HUB, registers itself, sends heartbeats, and participates
in memory sharing and mission coordination.

Usage:
    python basic_node_example.py
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any

# Import the NIS HUB SDK
try:
    from nis_hub_sdk import NISNode, NodeType, NodeCapability
except ImportError:
    # Add current directory to path for development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from nis_hub_sdk import NISNode, NodeType, NodeCapability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleNISNode:
    """
    Example NIS node that demonstrates basic HUB integration.
    
    This node simulates an exoplanet analysis system that:
    - Registers with the HUB
    - Sends regular heartbeats with system status
    - Shares analysis results in shared memory
    - Participates in coordinated missions
    - Responds to task assignments
    """
    
    def __init__(self):
        """Initialize the example node."""
        # Create NIS node instance
        self.node = NISNode(
            name="example-exoplanet-analyzer",
            node_type=NodeType.EXOPLANET_ANALYSIS,
            capabilities=[
                NodeCapability.DATA_PROCESSING,
                NodeCapability.MACHINE_LEARNING,
                NodeCapability.REAL_TIME_ANALYSIS
            ],
            description="Example exoplanet analysis node for NIS HUB demonstration",
            metadata={
                "version": "1.0.0",
                "location": "Laboratory",
                "instruments": ["spectrometer", "photometer"],
                "data_sources": ["TESS", "Kepler", "ground_based"]
            },
            heartbeat_interval=15  # Send heartbeat every 15 seconds
        )
        
        # Example state
        self.processed_planets = 0
        self.active_analyses = 0
        self.error_count = 0
        
        # Setup event handlers
        self.setup_event_handlers()
        
        # Shutdown flag
        self.shutdown_requested = False
    
    def setup_event_handlers(self):
        """Set up event handlers for node events."""
        
        @self.node.on_event("registered")
        async def on_registered(data):
            """Handle successful registration."""
            logger.info(f"🎉 Node registered successfully! Node ID: {data['node_id']}")
            
            # Share initial data after registration
            await self.share_initial_data()
        
        @self.node.on_event("connected")
        async def on_connected():
            """Handle WebSocket connection."""
            logger.info("🔗 WebSocket connected to NIS HUB")
        
        @self.node.on_event("disconnected")
        async def on_disconnected():
            """Handle WebSocket disconnection."""
            logger.warning("🔌 WebSocket disconnected from NIS HUB")
        
        @self.node.on_event("task_assigned")
        async def on_task_assigned(task_data):
            """Handle task assignment."""
            task_id = task_data.get("task_id")
            mission_id = task_data.get("mission_id")
            logger.info(f"📋 Task assigned: {task_id} for mission {mission_id}")
            
            # Handle the task
            await self.handle_assigned_task(task_data)
        
        @self.node.on_event("mission_created")
        async def on_mission_created(mission_data):
            """Handle new mission creation."""
            mission_id = mission_data.get("mission_id")
            mission_name = mission_data.get("name")
            logger.info(f"🚀 New mission created: {mission_name} ({mission_id})")
        
        @self.node.on_message("memory_notification")
        async def on_memory_update(data):
            """Handle memory update notifications."""
            entry_ids = data.get("entry_ids", [])
            logger.info(f"🧠 Memory updated: {len(entry_ids)} new entries")
        
        @self.node.on_message("coordination_event")
        async def on_coordination_event(data):
            """Handle coordination events."""
            event_type = data.get("event_type")
            message = data.get("message")
            logger.info(f"🤝 Coordination event: {event_type} - {message}")
    
    async def share_initial_data(self):
        """Share some initial data with the HUB."""
        try:
            # Create some example memory entries
            sample_entries = [
                {
                    "title": "Exoplanet Catalog Update",
                    "description": "Updated catalog of confirmed exoplanets",
                    "memory_type": "analysis_result",
                    "domain": "exoplanet",
                    "scope": "public",
                    "data": {
                        "catalog_version": "2025.1",
                        "total_planets": 5432,
                        "new_discoveries": 127,
                        "habitable_zone_candidates": 45
                    },
                    "tags": ["catalog", "exoplanets", "update"]
                },
                {
                    "title": "Atmospheric Analysis Results",
                    "description": "Spectroscopic analysis of HD 209458b atmosphere",
                    "memory_type": "analysis_result", 
                    "domain": "exoplanet",
                    "scope": "domain",
                    "data": {
                        "planet_name": "HD 209458b",
                        "detected_molecules": ["H2O", "CO2", "CH4"],
                        "temperature": 1400,
                        "pressure_profile": [0.1, 0.01, 0.001],
                        "confidence": 0.87
                    },
                    "tags": ["atmosphere", "spectroscopy", "hot_jupiter"]
                }
            ]
            
            # Sync entries to the HUB
            success = await self.node.memory.sync_entries(sample_entries)
            if success:
                logger.info(f"✅ Shared {len(sample_entries)} initial memory entries")
            
        except Exception as e:
            logger.error(f"❌ Failed to share initial data: {e}")
    
    async def simulate_analysis_work(self):
        """Simulate ongoing exoplanet analysis work."""
        while not self.shutdown_requested:
            try:
                # Simulate processing a planet
                await asyncio.sleep(10)  # Analysis takes 10 seconds
                
                self.processed_planets += 1
                self.active_analyses = max(0, self.active_analyses - 1)
                
                # Update node status
                await self.node.send_status_update({
                    "status": "healthy",
                    "active_tasks": self.active_analyses,
                    "completed_tasks": self.processed_planets,
                    "error_count": self.error_count,
                    "details": {
                        "last_analysis": f"Planet-{self.processed_planets}",
                        "processing_rate": "6 planets/hour"
                    }
                })
                
                # Occasionally share analysis results
                if self.processed_planets % 3 == 0:
                    await self.share_analysis_result()
                
                logger.info(f"🔬 Completed analysis of Planet-{self.processed_planets}")
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"❌ Analysis error: {e}")
    
    async def share_analysis_result(self):
        """Share analysis results with other nodes."""
        try:
            # Create analysis result entry
            analysis_entry = {
                "title": f"Analysis Result - Planet-{self.processed_planets}",
                "description": f"Completed analysis of exoplanet candidate {self.processed_planets}",
                "memory_type": "analysis_result",
                "domain": "exoplanet", 
                "scope": "public",
                "data": {
                    "planet_id": f"Planet-{self.processed_planets}",
                    "planet_type": "super_earth",
                    "radius": 1.7,
                    "mass": 2.3,
                    "orbital_period": 12.4,
                    "equilibrium_temperature": 285,
                    "habitability_score": 0.73,
                    "analysis_timestamp": "2025-01-20T12:00:00Z"
                },
                "tags": ["analysis", "super_earth", "habitable"]
            }
            
            success = await self.node.memory.sync_entries([analysis_entry])
            if success:
                logger.info(f"📤 Shared analysis result for Planet-{self.processed_planets}")
                
                # Broadcast notification
                await self.node.memory.broadcast_notification(
                    message_type="analysis_complete",
                    title=f"New Exoplanet Analysis Complete",
                    content={
                        "planet_id": f"Planet-{self.processed_planets}",
                        "habitability_score": 0.73,
                        "analysis_node": self.node.node_id
                    },
                    target_domains=["exoplanet", "astrobiology"]
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to share analysis result: {e}")
    
    async def handle_assigned_task(self, task_data: Dict[str, Any]):
        """Handle an assigned task."""
        task_id = task_data.get("task_id")
        mission_id = task_data.get("mission_id")
        
        try:
            # Record task assignment
            self.node.missions.handle_task_assignment(task_data)
            self.active_analyses += 1
            
            # Simulate task execution
            logger.info(f"🔄 Executing task {task_id}...")
            await asyncio.sleep(5)  # Task takes 5 seconds
            
            # Complete the task
            task_result = {
                "status": "completed",
                "processed_objects": 10,
                "discoveries": 2,
                "execution_time": 5.0
            }
            
            self.node.missions.complete_task(task_id, task_result)
            
            # Update mission progress
            await self.node.missions.update_mission_progress(
                mission_id=mission_id,
                progress_message=f"Task {task_id} completed successfully"
            )
            
            logger.info(f"✅ Task {task_id} completed successfully")
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Task execution failed: {e}")
    
    async def create_example_mission(self):
        """Create an example coordinated mission."""
        try:
            # Wait a bit after startup
            await asyncio.sleep(30)
            
            # Define mission tasks
            tasks = [
                {
                    "task_id": "survey_sector_1",
                    "name": "Survey Sector 1",
                    "task_type": "planet_detection",
                    "parameters": {"sector": 1, "sensitivity": "high"},
                    "required_capabilities": ["data_processing"]
                },
                {
                    "task_id": "analyze_candidates",
                    "name": "Analyze Planet Candidates", 
                    "task_type": "analysis",
                    "parameters": {"min_confidence": 0.8},
                    "required_capabilities": ["machine_learning"]
                },
                {
                    "task_id": "validate_discoveries",
                    "name": "Validate Discoveries",
                    "task_type": "validation",
                    "parameters": {"cross_reference": True},
                    "required_capabilities": ["data_processing", "real_time_analysis"]
                }
            ]
            
            # Create the mission
            mission_id = await self.node.missions.create_mission(
                name="Exoplanet Discovery Survey - Sector 1",
                mission_type="exploration",
                domain="exoplanet",
                tasks=tasks,
                description="Coordinated survey and analysis of exoplanet candidates in TESS Sector 1",
                priority="high",
                auto_assign_nodes=True
            )
            
            logger.info(f"🎯 Created example mission: {mission_id}")
            
            # Start the mission after a short delay
            await asyncio.sleep(10)
            await self.node.missions.start_mission(mission_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to create example mission: {e}")
    
    async def start(self):
        """Start the node and all its operations."""
        try:
            logger.info("🚀 Starting NIS HUB Example Node...")
            
            # Register with the HUB
            node_id = await self.node.register()
            logger.info(f"✅ Registered with node ID: {node_id}")
            
            # Start heartbeat
            await self.node.start_heartbeat()
            logger.info("💓 Heartbeat started")
            
            # Start WebSocket connection
            await self.node.start_websocket()
            logger.info("🔗 WebSocket connection started")
            
            # Start background tasks
            analysis_task = asyncio.create_task(self.simulate_analysis_work())
            mission_task = asyncio.create_task(self.create_example_mission())
            
            logger.info("🎬 Node is fully operational!")
            
            # Wait for shutdown signal
            while not self.shutdown_requested:
                await asyncio.sleep(1)
            
            # Cleanup
            analysis_task.cancel()
            mission_task.cancel()
            
            try:
                await asyncio.gather(analysis_task, mission_task, return_exceptions=True)
            except:
                pass
            
        except Exception as e:
            logger.error(f"❌ Node startup failed: {e}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the node."""
        logger.info("🔄 Shutting down node...")
        self.shutdown_requested = True
        
        try:
            await self.node.shutdown()
            logger.info("✅ Node shutdown complete")
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main():
    """Main entry point."""
    # Create and start the example node
    example_node = ExampleNISNode()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("🛑 Shutdown signal received")
        asyncio.create_task(example_node.shutdown())
    
    # Register signal handlers
    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(sig, signal_handler)
    
    try:
        await example_node.start()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        await example_node.shutdown()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        await example_node.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    print("""
    🧠 NIS HUB Example Node
    =====================
    
    This example demonstrates a complete NIS node that:
    ✅ Registers with the central HUB
    ✅ Sends regular heartbeats with status updates
    ✅ Shares analysis results in distributed memory
    ✅ Creates and participates in coordinated missions
    ✅ Handles task assignments from the HUB
    ✅ Responds to real-time events and notifications
    
    Make sure the NIS HUB server is running on localhost:8000
    before starting this example.
    
    Press Ctrl+C to stop.
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example node stopped.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 