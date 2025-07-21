#!/usr/bin/env python3
"""
NIS HUB Startup Script

This script helps you quickly start the complete NIS HUB system
including the FastAPI backend, Redis, and example nodes.
"""

import asyncio
import subprocess
import sys
import time
import platform
from pathlib import Path

def check_requirements():
    """Check if required dependencies are available."""
    requirements = {
        'python': 'Python 3.9+',
        'redis-server': 'Redis Server',
        'node': 'Node.js 18+',
    }
    
    missing = []
    
    # Check Python
    if sys.version_info < (3, 9):
        missing.append('Python 3.9+ (current: {}.{})'.format(*sys.version_info[:2]))
    
    # Check Redis
    try:
        subprocess.run(['redis-server', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('Redis Server')
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                               capture_output=True, check=True, text=True)
        version = result.stdout.strip().replace('v', '')
        major_version = int(version.split('.')[0])
        if major_version < 18:
            missing.append(f'Node.js 18+ (current: {version})')
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('Node.js 18+')
    
    return missing

def start_redis():
    """Start Redis server."""
    print("🔴 Starting Redis server...")
    
    try:
        # Check if Redis is already running
        subprocess.run(['redis-cli', 'ping'], 
                      capture_output=True, check=True)
        print("✅ Redis server is already running")
        return None
    except subprocess.CalledProcessError:
        pass  # Redis not running, start it
    
    try:
        if platform.system() == 'Windows':
            # Windows Redis startup
            redis_process = subprocess.Popen(['redis-server'])
        else:
            # Unix-like systems
            redis_process = subprocess.Popen(['redis-server', '--daemonize', 'yes'])
        
        # Wait a moment for Redis to start
        time.sleep(2)
        
        # Verify Redis is running
        subprocess.run(['redis-cli', 'ping'], 
                      capture_output=True, check=True)
        print("✅ Redis server started successfully")
        return redis_process
        
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return None

def start_nis_hub_core():
    """Start the NIS HUB FastAPI core."""
    print("🧠 Starting NIS HUB Core...")
    
    core_dir = Path(__file__).parent.parent / 'core'
    
    try:
        # Install Python dependencies if needed
        print("📦 Installing Python dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 
            str(core_dir / 'requirements.txt')
        ], check=True, capture_output=True)
        
        # Start the FastAPI server
        hub_process = subprocess.Popen([
            sys.executable, str(core_dir / 'main.py')
        ], cwd=core_dir)
        
        # Wait for the server to start
        time.sleep(3)
        print("✅ NIS HUB Core started successfully")
        return hub_process
        
    except Exception as e:
        print(f"❌ Failed to start NIS HUB Core: {e}")
        return None

def start_example_node():
    """Start an example NIS node."""
    print("🤖 Starting example NIS node...")
    
    sdk_dir = Path(__file__).parent.parent / 'sdk'
    example_script = sdk_dir / 'examples' / 'basic_node_example.py'
    
    try:
        # Install SDK dependencies
        print("📦 Installing SDK dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 
            str(sdk_dir / 'requirements.txt')
        ], check=True, capture_output=True)
        
        # Start the example node
        node_process = subprocess.Popen([
            sys.executable, str(example_script)
        ], cwd=sdk_dir)
        
        time.sleep(2)
        print("✅ Example NIS node started successfully")
        return node_process
        
    except Exception as e:
        print(f"❌ Failed to start example node: {e}")
        return None

def main():
    """Main startup function."""
    print("""
🧠 NIS HUB System Startup
========================

This script will start the complete NIS HUB system:
• Redis server for distributed memory
• NIS HUB Core (FastAPI backend)
• Example NIS node for demonstration

Press Ctrl+C to stop all services.
""")
    
    # Check requirements
    print("🔍 Checking requirements...")
    missing = check_requirements()
    
    if missing:
        print("❌ Missing requirements:")
        for req in missing:
            print(f"   • {req}")
        print("\nPlease install the missing requirements and try again.")
        return 1
    
    print("✅ All requirements satisfied")
    
    processes = []
    
    try:
        # Start Redis
        redis_process = start_redis()
        if redis_process:
            processes.append(('Redis', redis_process))
        
        # Start NIS HUB Core
        hub_process = start_nis_hub_core()
        if hub_process:
            processes.append(('NIS HUB Core', hub_process))
        else:
            print("❌ Failed to start NIS HUB Core, aborting...")
            return 1
        
        # Start example node
        node_process = start_example_node()
        if node_process:
            processes.append(('Example Node', node_process))
        
        print(f"""
🎉 NIS HUB System is now running!

Services started:
{chr(10).join(f'• {name} (PID: {proc.pid})' for name, proc in processes)}

You can now:
• View the API docs at: http://localhost:8000/docs
• Monitor the system at: http://localhost:8000/health
• Connect additional nodes using the SDK

Press Ctrl+C to stop all services.
""")
        
        # Wait for interruption
        try:
            while True:
                # Check if any process has died
                for name, proc in processes:
                    if proc.poll() is not None:
                        print(f"⚠️ {name} process has stopped")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown signal received")
    
    finally:
        # Clean up processes
        print("🔄 Stopping services...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {name} force-killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("✅ All services stopped")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 