#!/bin/bash

# NIS-HUB v3.1 - Complete System Reset Script
# This script completely resets the NIS-HUB system, removing all data and rebuilding from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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
    echo -e "${PURPLE}[🧠 RESET]${NC} $1"
}

print_coordination() {
    echo -e "${CYAN}[🌐 COORDINATION]${NC} $1"
}

# Function to show warning and get confirmation
show_warning() {
    print_warning "⚠️  COMPLETE NIS-HUB SYSTEM RESET WARNING ⚠️"
    echo ""
    echo "This will PERMANENTLY DELETE:"
    echo "  🧠 All consciousness training data"
    echo "  🔢 All KAN network models and interpretations"
    echo "  ⚗️  All PINN physics validation history"
    echo "  🌐 All node registrations and connections"
    echo "  🧠 All shared memory entries"
    echo "  🚀 All mission data and coordination logs"
    echo "  📊 All performance metrics and analytics"
    echo "  🗄️  All database data (SQLite/PostgreSQL)"
    echo "  🧠 All cached consciousness evaluations"
    echo "  📝 All logs and temporary files"
    echo "  🔧 All configuration files (recreated from defaults)"
    echo "  🐍 Backend virtual environment"
    echo "  📦 Frontend node_modules"
    echo ""
    echo "💾 Data that will be preserved:"
    echo "  • Source code in core/ and ui/"
    echo "  • Documentation in docs/"
    echo "  • Configuration templates (.env.example)"
    echo "  • This reset script and start scripts"
    echo ""
    print_warning "This action cannot be undone!"
    echo ""
    
    if [ "$1" != "--force" ]; then
        read -p "Are you absolutely sure you want to reset the entire NIS-HUB? (type 'RESET' to continue): " -r
        if [ "$REPLY" != "RESET" ]; then
            print_status "Reset cancelled"
            exit 0
        fi
    fi
}

# Function to stop all services gracefully
stop_all_services() {
    print_hub "Stopping all NIS-HUB coordination services gracefully..."
    
    # Use the stop.sh script for a graceful shutdown
    if [ -f "./stop.sh" ]; then
        ./stop.sh --cleanup-pids
    else
        # Fallback to manual stop if stop.sh is not available
        print_warning "stop.sh not found, using manual shutdown..."
        
        # Stop any running Python processes
        local python_pids=$(pgrep -f "python.*main.py\|uvicorn\|fastapi" 2>/dev/null || true)
        if [ -n "$python_pids" ]; then
            echo "$python_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
        fi
        
        # Stop any running Node.js processes  
        local node_pids=$(pgrep -f "node.*vite\|npm.*dev" 2>/dev/null || true)
        if [ -n "$node_pids" ]; then
            echo "$node_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
        fi
        
        # Stop Redis if running
        local redis_pids=$(pgrep -f "redis-server.*6379" 2>/dev/null || true)
        if [ -n "$redis_pids" ]; then
            echo "$redis_pids" | xargs kill -TERM 2>/dev/null || true
            sleep 1
        fi
    fi
    
    print_success "All coordination services stopped and cleaned"
}

# Function to remove all data and cache
remove_all_data() {
    print_hub "Removing all NIS-HUB intelligence data..."
    
    # Remove data directories
    directories_to_clean=(
        "logs"
        "data"
        "cache"
        "models"
        "checkpoints"
        "exports"
        "uploads"
        "temp"
    )
    
    for dir in "${directories_to_clean[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Removed: $dir (all intelligence data cleared)"
        fi
    done
    
    print_success "All coordination data removed"
}

# Function to clean configuration files
clean_configuration() {
    print_status "Cleaning configuration files..."
    
    config_files=(
        ".env"
        ".env.local"
        ".env.safe"
        "core/.env"
        "ui/.env.local"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            print_status "Removed: $file"
        fi
    done
    
    print_success "Configuration files cleaned"
}

# Function to remove development environments
remove_environments() {
    print_status "Removing development environments..."
    
    # Backend virtual environment
    if [ -d "$BACKEND_DIR/venv" ]; then
        rm -rf "$BACKEND_DIR/venv"
        print_status "Removed backend virtual environment"
    fi
    
    # Backend __pycache__
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
    print_status "Cleaned Python cache files"
    
    # Frontend node_modules and build artifacts
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        rm -rf "$FRONTEND_DIR/node_modules"
        print_status "Removed frontend node_modules"
    fi
    
    # Frontend build and cache directories
    frontend_clean_dirs=(
        "$FRONTEND_DIR/dist"
        "$FRONTEND_DIR/build"
        "$FRONTEND_DIR/.next"
        "$FRONTEND_DIR/.vite"
        "$FRONTEND_DIR/.cache"
    )
    
    for dir in "${frontend_clean_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Removed: $dir"
        fi
    done
    
    print_success "Development environments cleaned"
}

# Function to reset consciousness system
reset_consciousness() {
    print_hub "Resetting consciousness subsystem..."
    
    # Remove consciousness-specific data
    consciousness_dirs=(
        "data/consciousness"
        "data/bias_detection"  
        "data/ethical_decisions"
        "cache/consciousness"
    )
    
    for dir in "${consciousness_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Reset consciousness data: $dir"
        fi
    done
    
    print_success "🧠 Consciousness system reset to initial state"
}

# Function to reset KAN networks
reset_kan_networks() {
    print_hub "Resetting KAN (Kolmogorov-Arnold Networks)..."
    
    # Remove KAN-specific data
    kan_dirs=(
        "data/kan_networks"
        "data/interpretations"
        "data/symbolic_functions"
        "cache/kan"
        "models/kan"
    )
    
    for dir in "${kan_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Reset KAN data: $dir"
        fi
    done
    
    print_success "🔢 KAN networks reset to untrained state"
}

# Function to reset PINN physics
reset_pinn_physics() {
    print_hub "Resetting PINN (Physics-Informed Neural Networks)..."
    
    # Remove PINN-specific data
    pinn_dirs=(
        "data/pinn_validations"
        "data/physics_simulations"
        "data/conservation_laws"
        "cache/pinn"
        "models/pinn"
    )
    
    for dir in "${pinn_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Reset PINN data: $dir"
        fi
    done
    
    print_success "⚗️ PINN physics validation reset to baseline"
}

# Function to reset coordination data
reset_coordination() {
    print_coordination "Resetting coordination subsystem..."
    
    # Remove coordination-specific data
    coordination_dirs=(
        "data/nodes"
        "data/missions"
        "data/memory_sync"
        "data/websocket_sessions"
        "cache/coordination"
    )
    
    for dir in "${coordination_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_status "Reset coordination data: $dir"
        fi
    done
    
    print_success "🌐 Coordination system reset to fresh state"
}

# Function to create fresh directories
create_fresh_directories() {
    print_status "Creating fresh directory structure..."
    
    directories=(
        "logs"
        "data"
        "data/consciousness"
        "data/kan_networks"
        "data/pinn_validations"
        "data/nodes"
        "data/missions"
        "data/memory_sync"
        "cache"
        "cache/consciousness"
        "cache/kan"
        "cache/pinn"
        "cache/coordination"
        "models"
        "models/kan"
        "models/pinn"
        "exports"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created: $dir"
    done
    
    # Create .gitkeep files to preserve directory structure
    find . -type d -name "cache" -o -name "data" -o -name "logs" -o -name "temp" | while read dir; do
        if [ ! -f "$dir/.gitkeep" ]; then
            touch "$dir/.gitkeep"
        fi
    done
    
    print_success "Fresh NIS-HUB directory structure created"
}

# Function to reinstall dependencies
reinstall_dependencies() {
    print_status "Reinstalling dependencies from scratch..."
    
    # Backend dependencies
    print_status "Setting up fresh backend environment..."
    cd "$BACKEND_DIR"
    
    if command -v python3 &> /dev/null; then
        python3 -m venv venv
        source venv/bin/activate
        
        if [ -f "requirements.txt" ]; then
            pip install --upgrade pip > /dev/null 2>&1
            pip install -r requirements.txt > /dev/null 2>&1
            print_success "Backend dependencies installed"
        else
            print_warning "requirements.txt not found in $BACKEND_DIR"
        fi
    else
        print_error "Python 3 not found. Cannot set up backend environment."
    fi
    
    cd ..
    
    # Frontend dependencies
    print_status "Setting up fresh frontend environment..."
    cd "$FRONTEND_DIR"
    
    if command -v npm &> /dev/null; then
        if [ -f "package.json" ]; then
            npm install > /dev/null 2>&1
            print_success "Frontend dependencies installed"
        else
            print_warning "package.json not found in $FRONTEND_DIR"
        fi
    else
        print_error "npm not found. Cannot set up frontend environment."
    fi
    
    cd ..
    
    print_success "Fresh dependencies installed"
}

# Function to create default configuration
create_default_config() {
    print_status "Creating default configuration files..."
    
    # Create basic .env file
    cat > .env << 'EOF'
# NIS-HUB v3.1 Configuration (Fresh Installation)
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./data/nishub.db
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_PORT=3000

# WebSocket Configuration
WS_HOST=localhost
WS_PORT=8001

# Consciousness Service
CONSCIOUSNESS_ENABLED=true
CONSCIOUSNESS_LOG_LEVEL=INFO

# KAN Networks
KAN_ENABLED=true
KAN_DEFAULT_PRECISION=float32

# PINN Physics Validation
PINN_ENABLED=true
PINN_STRICT_VALIDATION=false

# BitNet Service
BITNET_ENABLED=true
BITNET_QUANTIZATION=8bit

# MCP Adapter
MCP_ENABLED=true
MCP_PROTOCOL_VERSION=2024-11-05
EOF

    print_success "Default configuration created"
}

# Function to verify reset
verify_reset() {
    print_status "Verifying reset completion..."
    
    # Check for remaining processes
    local python_processes=$(pgrep -f "python.*main.py\|uvicorn\|fastapi" 2>/dev/null | wc -l)
    local node_processes=$(pgrep -f "node.*vite\|npm.*dev" 2>/dev/null | wc -l)
    
    print_status "Remaining Python processes: $python_processes"
    print_status "Remaining Node processes: $node_processes"
    
    # Check directory sizes
    local total_data_size="0"
    if [ -d "data" ]; then
        total_data_size=$(du -sh data 2>/dev/null | cut -f1 || echo "0")
    fi
    print_status "Data directory size: $total_data_size"
    
    # Check for virtual environments
    if [ -d "$BACKEND_DIR/venv" ]; then
        print_status "Backend virtual environment: RECREATED"
    else
        print_warning "Backend virtual environment: NOT FOUND"
    fi
    
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        print_status "Frontend node_modules: RECREATED"
    else
        print_warning "Frontend node_modules: NOT FOUND"
    fi
    
    print_success "Reset verification completed"
}

# Function to start fresh system
start_fresh() {
    if [ "$1" = "--start" ]; then
        print_hub "Starting fresh NIS-HUB system..."
        if [ "$2" = "--safe" ]; then
            ./start_safe.sh
        else
            ./start.sh
        fi
    else
        echo ""
        print_success "🎉 NIS-HUB v3.1 reset completed successfully!"
        echo ""
        echo "🧠 What was reset:"
        echo "  ✅ All consciousness training data cleared"
        echo "  ✅ All KAN network models removed"
        echo "  ✅ All PINN physics validations reset"
        echo "  ✅ All coordination data cleared"
        echo "  ✅ All node registrations removed"
        echo "  ✅ All mission data deleted"
        echo "  ✅ All shared memories cleared"
        echo "  ✅ Fresh virtual environments created"
        echo "  ✅ Dependencies reinstalled"
        echo "  ✅ Default configuration restored"
        echo ""
        echo "🚀 To start the fresh system:"
        echo "  • ./start.sh              (Full production mode)"
        echo "  • ./start_safe.sh         (Safe development mode)"
        echo ""
        echo "🧠 The consciousness will need to be retrained from scratch"
        echo "🔢 KAN networks will need to learn new interpretations"
        echo "⚗️ PINN physics validation will start from baseline"
        echo "🌐 All nodes will need to re-register"
        echo ""
        echo "🔧 System is ready for fresh awakening"
    fi
}

# Main execution
main() {
    print_hub "Initiating NIS-HUB v3.1 Complete System Reset..."
    echo ""
    
    # Show warning and get confirmation
    show_warning "$1"
    
    print_hub "Starting comprehensive reset process..."
    echo ""
    
    # Reset process
    stop_all_services
    
    # Reset individual subsystems
    reset_consciousness
    reset_kan_networks  
    reset_pinn_physics
    reset_coordination
    
    # Clean everything
    remove_all_data
    remove_environments
    clean_configuration
    
    # Rebuild fresh
    create_fresh_directories
    create_default_config
    reinstall_dependencies
    verify_reset
    
    # Start if requested
    start_fresh "$2" "$3"
    
    print_hub "NIS-HUB complete reset process finished!"
}

# Handle script arguments
if [ "$1" = "--help" ]; then
    echo "NIS-HUB v3.1 Complete System Reset Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help     Show this help message"
    echo "  --force    Skip confirmation prompt"
    echo "  --start    Automatically start the system after reset"
    echo "  --safe     Use safe mode when starting (with --start)"
    echo ""
    echo "Examples:"
    echo "  $0                    Interactive reset with confirmation"
    echo "  $0 --force            Reset without confirmation"
    echo "  $0 --force --start    Reset and immediately start fresh system"
    echo "  $0 --force --start --safe    Reset and start in safe mode"
    echo ""
    echo "⚠️  WARNING: This will permanently delete all NIS-HUB data!"
    echo ""
    echo "🧠 What gets reset:"
    echo "  • Consciousness training and bias detection data"
    echo "  • KAN network models and interpretations"
    echo "  • PINN physics validation history"
    echo "  • Node registrations and coordination data"
    echo "  • Shared memory entries and mission logs"
    echo "  • All configuration files"
    echo "  • Virtual environments and dependencies"
    echo ""
    echo "🔄 Alternative commands:"
    echo "  • ./stop.sh --cleanup-data    (less destructive option)"
    echo "  • ./start.sh                  (start existing system)"
    echo "  • ./start_safe.sh             (start in safe mode)"
    exit 0
fi

# Additional safety check
if [ "$1" = "--force" ]; then
    print_warning "FORCE RESET MODE"
    echo "This will immediately reset ALL NIS-HUB systems without confirmation!"
    echo ""
fi

# Run main function
main "$@"
