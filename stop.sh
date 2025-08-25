#!/bin/bash

# NIS-HUB v3.1 - Complete System Shutdown Script
# This script stops all NIS-HUB services gracefully in the proper order

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="nis-hub-v3"
BACKEND_DIR="core"
FRONTEND_DIR="ui"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[NIS-HUB]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_hub() {
    echo -e "${PURPLE}[🧠 COORDINATION]${NC} $1"
}

# Function to check if processes are running
check_processes() {
    local backend_running=false
    local frontend_running=false
    
    if [ -f ".env.local" ]; then
        source .env.local
        
        if [ -n "$BACKEND_PID" ] && ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            backend_running=true
        fi
        
        if [ -n "$FRONTEND_PID" ] && ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            frontend_running=true
        fi
    fi
    
    if [ "$backend_running" = false ] && [ "$frontend_running" = false ]; then
        return 1
    else
        return 0
    fi
}

# Function to stop services gracefully
stop_services() {
    print_hub "Initiating graceful shutdown of NIS-HUB central coordination..."
    
    if ! check_processes; then
        print_warning "No running NIS-HUB processes found"
        return 0
    fi
    
    # Load process IDs
    if [ -f ".env.local" ]; then
        source .env.local
        print_status "Found process configuration"
    else
        print_warning "No .env.local found, will attempt to find processes manually"
    fi
    
    # Stop frontend first (React dev server)
    print_status "Stopping NIS-HUB dashboard..."
    if [ -n "$FRONTEND_PID" ] && ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
        sleep 2
        
        # Check if it stopped gracefully
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            print_warning "Frontend didn't stop gracefully, forcing shutdown..."
            kill -KILL "$FRONTEND_PID" 2>/dev/null || true
        fi
        print_success "Dashboard stopped"
    else
        # Try to find and stop any npm/node processes
        local npm_pids=$(pgrep -f "npm.*dev" 2>/dev/null || true)
        local vite_pids=$(pgrep -f "vite" 2>/dev/null || true)
        
        if [ -n "$npm_pids" ]; then
            print_status "Found npm dev processes, stopping..."
            echo "$npm_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 1
        fi
        
        if [ -n "$vite_pids" ]; then
            print_status "Found Vite processes, stopping..."
            echo "$vite_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 1
        fi
        
        print_success "Frontend processes stopped"
    fi
    
    # Stop backend server (FastAPI)
    print_status "Stopping NIS-HUB backend coordination system..."
    if [ -n "$BACKEND_PID" ] && ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
        sleep 3
        
        # Check if it stopped gracefully
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            print_warning "Backend didn't stop gracefully, forcing shutdown..."
            kill -KILL "$BACKEND_PID" 2>/dev/null || true
        fi
        print_success "Backend coordination system stopped"
    else
        # Try to find and stop any Python FastAPI processes
        local fastapi_pids=$(pgrep -f "python.*main.py" 2>/dev/null || true)
        local uvicorn_pids=$(pgrep -f "uvicorn" 2>/dev/null || true)
        
        if [ -n "$fastapi_pids" ]; then
            print_status "Found FastAPI processes, stopping..."
            echo "$fastapi_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
        fi
        
        if [ -n "$uvicorn_pids" ]; then
            print_status "Found Uvicorn processes, stopping..."
            echo "$uvicorn_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
        fi
        
        print_success "Backend processes stopped"
    fi
    
    # Stop Redis if we started it
    print_status "Stopping Redis server (if started by NIS-HUB)..."
    local redis_pids=$(pgrep -f "redis-server.*6379" 2>/dev/null || true)
    if [ -n "$redis_pids" ]; then
        echo "$redis_pids" | xargs kill -TERM 2>/dev/null || true
        sleep 1
        print_success "Redis server stopped"
    else
        print_status "No Redis server found (may be running externally)"
    fi
    
    print_hub "All coordination services stopped gracefully"
}

# Function to clean up process files
cleanup_process_files() {
    if [ "$1" = "--cleanup-pids" ]; then
        print_status "Cleaning up process files..."
        
        files_to_remove=(
            ".env.local"
            "logs/backend.pid"
            "logs/frontend.pid"
        )
        
        for file in "${files_to_remove[@]}"; do
            if [ -f "$file" ]; then
                rm -f "$file"
                print_status "Removed: $file"
            fi
        done
        
        print_success "Process files cleaned up"
    fi
}

# Function to clean up log files
cleanup_logs() {
    if [ "$1" = "--cleanup-logs" ]; then
        print_status "Cleaning up log files..."
        
        if [ -d "logs" ]; then
            rm -rf logs/*
            print_success "Log files cleaned"
        else
            print_status "No log directory found"
        fi
    fi
}

# Function to clean up data files
cleanup_data() {
    if [ "$1" = "--cleanup-data" ]; then
        print_warning "Cleaning up data files..."
        read -p "This will delete all local data. Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            directories_to_clean=(
                "data"
                "cache"
            )
            
            for dir in "${directories_to_clean[@]}"; do
                if [ -d "$dir" ]; then
                    rm -rf "$dir"
                    print_status "Removed: $dir"
                fi
            done
            
            print_success "Data files cleaned"
        else
            print_status "Data cleanup cancelled"
        fi
    fi
}

# Function to remove virtual environments
cleanup_environments() {
    if [ "$1" = "--cleanup-env" ]; then
        print_status "Cleaning up development environments..."
        
        # Backend virtual environment
        if [ -d "$BACKEND_DIR/venv" ]; then
            rm -rf "$BACKEND_DIR/venv"
            print_status "Removed backend virtual environment"
        fi
        
        # Frontend node_modules
        if [ -d "$FRONTEND_DIR/node_modules" ]; then
            rm -rf "$FRONTEND_DIR/node_modules"
            print_status "Removed frontend node_modules"
        fi
        
        print_success "Development environments cleaned"
    fi
}

# Function to force stop everything
force_stop() {
    if [ "$1" = "--force" ]; then
        print_warning "Force stopping all NIS-HUB related processes..."
        
        # Kill all Python processes that might be NIS-HUB related
        local python_pids=$(pgrep -f "python.*main.py\|uvicorn\|fastapi" 2>/dev/null || true)
        if [ -n "$python_pids" ]; then
            echo "$python_pids" | xargs kill -KILL 2>/dev/null || true
            print_status "Force killed Python processes"
        fi
        
        # Kill all Node.js processes that might be NIS-HUB related
        local node_pids=$(pgrep -f "node.*vite\|npm.*dev" 2>/dev/null || true)
        if [ -n "$node_pids" ]; then
            echo "$node_pids" | xargs kill -KILL 2>/dev/null || true
            print_status "Force killed Node.js processes"
        fi
        
        # Kill Redis if running on default port
        local redis_pids=$(pgrep -f "redis-server.*6379" 2>/dev/null || true)
        if [ -n "$redis_pids" ]; then
            echo "$redis_pids" | xargs kill -KILL 2>/dev/null || true
            print_status "Force killed Redis processes"
        fi
        
        print_success "Force stop completed"
    fi
}

# Function to save logs before shutdown
save_logs() {
    if [ "$1" = "--save-logs" ]; then
        print_status "Saving system logs before shutdown..."
        
        local log_dir="logs/shutdown-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$log_dir"
        
        # Save current logs
        log_files=(
            "logs/backend.log"
            "logs/frontend.log"
            "logs/backend_safe.log"
            "logs/frontend_safe.log"
        )
        
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                cp "$log_file" "$log_dir/" 2>/dev/null || true
                print_status "Saved: $log_file"
            fi
        done
        
        # Save system information
        cat > "$log_dir/system_info.txt" << EOF
NIS-HUB Shutdown Information
============================
Date: $(date)
System: $(uname -a)
Python: $(python3 --version 2>&1 || echo "Not found")
Node.js: $(node --version 2>&1 || echo "Not found")
Redis: $(redis-server --version 2>&1 || echo "Not found")

Running Processes:
$(ps aux | grep -E "(python|node|redis)" | grep -v grep)

Network Connections:
$(netstat -an | grep -E "(8000|3000|6379)" 2>/dev/null || echo "netstat not available")
EOF
        
        print_success "Logs saved to: $log_dir"
    fi
}

# Function to show status
show_status() {
    print_status "NIS-HUB system status:"
    echo ""
    
    # Check for running processes
    local python_processes=$(pgrep -f "python.*main.py\|uvicorn\|fastapi" 2>/dev/null | wc -l)
    local node_processes=$(pgrep -f "node.*vite\|npm.*dev" 2>/dev/null | wc -l)
    local redis_processes=$(pgrep -f "redis-server" 2>/dev/null | wc -l)
    
    echo "  • Python/FastAPI processes: $python_processes"
    echo "  • Node.js/Frontend processes: $node_processes"
    echo "  • Redis processes: $redis_processes"
    echo ""
    
    # Check ports
    local port_8000=$(netstat -an 2>/dev/null | grep ":8000" | wc -l || echo "?")
    local port_3000=$(netstat -an 2>/dev/null | grep ":3000" | wc -l || echo "?")
    local port_6379=$(netstat -an 2>/dev/null | grep ":6379" | wc -l || echo "?")
    
    echo "  • Port 8000 (Backend): $port_8000 connections"
    echo "  • Port 3000 (Frontend): $port_3000 connections"
    echo "  • Port 6379 (Redis): $port_6379 connections"
    echo ""
    
    # Check directories
    if [ -d "logs" ]; then
        local log_count=$(ls logs/ 2>/dev/null | wc -l)
        echo "  • Log files: $log_count"
    fi
    
    if [ -d "data" ]; then
        local data_size=$(du -sh data 2>/dev/null | cut -f1 || echo "unknown")
        echo "  • Data directory size: $data_size"
    fi
}

# Main execution
main() {
    print_hub "Shutting down NIS-HUB v3.1 Central Intelligence System..."
    echo ""
    
    # Save logs if requested
    save_logs "$@"
    
    # Stop services
    stop_services
    
    # Handle additional options
    for arg in "$@"; do
        case $arg in
            --cleanup-pids)
                cleanup_process_files "$arg"
                ;;
            --cleanup-logs)
                cleanup_logs "$arg"
                ;;
            --cleanup-data)
                cleanup_data "$arg"
                ;;
            --cleanup-env)
                cleanup_environments "$arg"
                ;;
            --force)
                force_stop "$arg"
                ;;
        esac
    done
    
    # Show final status
    show_status
    
    print_hub "NIS-HUB coordination shutdown completed!"
    echo ""
    echo "🔄 To restart the system:"
    echo "  • ./start.sh              (Full production mode)"
    echo "  • ./start_safe.sh         (Safe development mode)"
    echo ""
    echo "🧹 Additional cleanup options:"
    echo "  • ./stop.sh --cleanup-pids       (remove process files)"
    echo "  • ./stop.sh --cleanup-logs       (remove log files)"
    echo "  • ./stop.sh --cleanup-data       (remove all data)"
    echo "  • ./stop.sh --cleanup-env        (remove virtual environments)"
    echo "  • ./stop.sh --force              (force kill all processes)"
    echo "  • ./stop.sh --save-logs          (save logs before shutdown)"
    echo ""
    print_success "🧠 Central coordination system is now offline"
}

# Handle script arguments
if [ "$1" = "--help" ]; then
    echo "NIS-HUB v3.1 Shutdown Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --cleanup-pids      Remove process ID files"
    echo "  --cleanup-logs      Remove all log files"
    echo "  --cleanup-data      Remove all data files (DESTRUCTIVE)"
    echo "  --cleanup-env       Remove virtual environments and node_modules"
    echo "  --force             Force kill all processes"
    echo "  --save-logs         Save logs before shutdown"
    echo ""
    echo "Examples:"
    echo "  $0                           Stop services gracefully"
    echo "  $0 --cleanup-pids            Stop and clean process files"
    echo "  $0 --cleanup-data            Stop and remove all data"
    echo "  $0 --force --save-logs       Save logs and force stop"
    echo ""
    echo "⚠️  WARNING: --cleanup-data will delete all local data permanently!"
    echo ""
    echo "🧠 NIS-HUB Services:"
    echo "  • Backend: FastAPI coordination server"
    echo "  • Frontend: React dashboard"
    echo "  • Redis: Memory and caching"
    echo "  • WebSocket: Real-time communication"
    exit 0
fi

# Warn about destructive operations
for arg in "$@"; do
    if [ "$arg" = "--cleanup-data" ]; then
        print_warning "WARNING: This operation will delete all local data!"
        echo "  • SQLite database will be lost"
        echo "  • Cache files will be cleared"
        echo "  • All logs will be deleted"
        echo "  • Stored memories will be lost"
        echo ""
        break
    fi
done

# Run main function
main "$@"
