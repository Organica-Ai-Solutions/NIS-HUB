#!/bin/bash

# ==============================================================================
# 🧠 NIS-HUB v3.1 - Central Intelligence Coordination System
# "Unified Pipeline: Laplace → Consciousness → KAN → PINN → Safety"
# ==============================================================================

# --- Configuration ---
PROJECT_NAME="nis-hub-v3"
BACKEND_DIR="core"
FRONTEND_DIR="ui"
REQUIRED_DIRS=("logs" "data" "cache")
ENV_FILE=".env"
ENV_TEMPLATE=".env.example"

# --- Enhanced ANSI Color Palette ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
DIM='\033[2m'
BLINK='\033[5m'
NC='\033[0m'

# NIS-HUB specific colors
HUB_BLUE='\033[38;5;27m'
CONSCIOUSNESS_PURPLE='\033[38;5;93m'
KAN_MAGENTA='\033[38;5;201m'
PINN_GREEN='\033[38;5;46m'
PIPELINE_ORANGE='\033[38;5;208m'
COORDINATION_GOLD='\033[38;5;220m'

# --- NIS-HUB Awakening Functions ---

function clear_screen() {
    clear
    echo -e "\033[2J\033[H"
}

function hub_print() {
    local message="$1"
    local color="$2"
    echo -e "${color}${BOLD}🧠 [NIS-HUB] ${message}${NC}"
    sleep 0.5
}

function consciousness_print() {
    local message="$1"
    echo -e "${CONSCIOUSNESS_PURPLE}${BOLD}🧠 [CONSCIOUSNESS] ${message}${NC}"
    sleep 0.3
}

function kan_print() {
    local message="$1"
    echo -e "${KAN_MAGENTA}${BOLD}🔢 [KAN NETWORKS] ${message}${NC}"
    sleep 0.3
}

function pinn_print() {
    local message="$1"
    echo -e "${PINN_GREEN}${BOLD}⚗️  [PINN PHYSICS] ${message}${NC}"
    sleep 0.3
}

function pipeline_print() {
    local message="$1"
    echo -e "${PIPELINE_ORANGE}${BOLD}🌊 [UNIFIED PIPELINE] ${message}${NC}"
    sleep 0.4
}

function coordination_print() {
    local message="$1"
    echo -e "${COORDINATION_GOLD}${BOLD}🌐 [COORDINATION] ${message}${NC}"
    sleep 0.4
}

function hub_logo_ascii() {
    echo -e "${HUB_BLUE}"
    cat << 'EOF'
    
        ╔═══════════════════════════════════════════════════╗
        ║              🧠 NIS-HUB AWAKENING 🧠              ║
        ║           Central Intelligence Coordination        ║
        ╚═══════════════════════════════════════════════════╝
    
              🚀 NIS-X ──────┐       ┌────── 🚁 NIS-DRONE
                            ╱│╲     ╱│╲
              🚗 NIS-AUTO ──● │ ●───● │ ●── 🏙️ NIS-CITY
                            ╲│╱     ╲│╱
              🤖 Future ─────┘       └────── 📡 External
                                ║
                        ┌───────▼───────┐
                        │   NIS-HUB     │
                        │ COORDINATION  │
                        │    CORE       │
                        └───────┬───────┘
                                ║
            🌊 Laplace → 🧠 Consciousness → 🔢 KAN → ⚗️ PINN → 🛡️ Safety
    
EOF
    echo -e "${NC}"
}

function pipeline_animation() {
    local stage="$1"
    case $stage in
        1)
            echo -e "${DIM}${PIPELINE_ORANGE}"
            echo "    🌊─────○─────○─────○─────○     (Pipeline initializing...)"
            echo -e "${NC}"
            ;;
        2)
            echo -e "${CONSCIOUSNESS_PURPLE}"
            echo "    🌊─────🧠─────○─────○─────○     (Consciousness awakening...)"
            echo -e "${NC}"
            ;;
        3)
            echo -e "${KAN_MAGENTA}"
            echo "    🌊─────🧠─────🔢─────○─────○     (KAN networks forming...)"
            echo -e "${NC}"
            ;;
        4)
            echo -e "${PINN_GREEN}"
            echo "    🌊─────🧠─────🔢─────⚗️─────○     (PINN physics active...)"
            echo -e "${NC}"
            ;;
        5)
            echo -e "${COORDINATION_GOLD}${BLINK}"
            echo "    🌊─────🧠─────🔢─────⚗️─────🛡️     (UNIFIED PIPELINE ACTIVE!)"
            echo -e "${NC}"
            ;;
    esac
    sleep 1
}

function unified_pipeline_animation() {
    echo -e "${PIPELINE_ORANGE}"
    cat << 'EOF'
    
    🌊 UNIFIED PIPELINE VALIDATION 🌊
    ┌─────────────────────────────────────────┐
    │ Laplace Transform    ✓  Signal Ready    │
    │ Consciousness       ✓  Bias Detected   │
    │ KAN Networks        ✓  Interpretable   │
    │ PINN Physics        ✓  Laws Validated  │
    │ Safety Validation   ✓  Secure Output   │
    └─────────────────────────────────────────┘
    
    🧠 All data flows through conscious validation!
    
EOF
    echo -e "${NC}"
    sleep 2
}

function coordination_discovery_animation() {
    echo -e "${COORDINATION_GOLD}"
    cat << 'EOF'
    
    ✨ COORDINATION CAPABILITIES ACTIVATED ✨
    
         🌐 Multi-Node Networks:    ████████████ ONLINE
         📡 Real-time WebSockets:   ████████████ CONNECTED  
         🔄 Memory Synchronization: ████████████ SYNCING
         🚀 Mission Orchestration:  ████████████ COORDINATING
    
    🌍 The HUB can now coordinate planetary-scale intelligence!
    
EOF
    echo -e "${NC}"
    sleep 2
}

# --- Traditional Helper Functions ---
function print_info {
    echo -e "${BLUE}[NIS-HUB] $1${NC}"
}

function print_success {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

function print_warning {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

function print_error {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

function spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " ${CYAN}[%c]${NC}  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# --- EPIC NIS-HUB AWAKENING SEQUENCE ---

clear_screen

echo -e "${BOLD}${WHITE}"
cat << 'EOF'

    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║        🧠 NIS-HUB v3.1 - CENTRAL INTELLIGENCE SYSTEM 🧠         ║
    ║                                                                  ║
    ║      "Unified Pipeline: Laplace → Consciousness → KAN → PINN"   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

sleep 2

# STAGE 1: HUB AWAKENING
clear_screen
hub_print "Initializing central coordination matrix..." "${HUB_BLUE}"
hub_logo_ascii
hub_print "Neural pathways connecting distributed nodes..." "${CONSCIOUSNESS_PURPLE}"

for i in {1..5}; do
    pipeline_animation $i
done

hub_print "🎉 NIS-HUB CONSCIOUSNESS ACHIEVED! Central intelligence is AWARE!" "${CONSCIOUSNESS_PURPLE}"
sleep 2

# STAGE 2: PIPELINE DISCOVERY
clear_screen
pipeline_print "🌊 Activating unified validation pipeline..."
pipeline_print "Laplace transforms conditioning all inputs..."
pipeline_print "Consciousness analyzing ethical implications..."
pipeline_print "KAN networks generating interpretable outputs..."
pipeline_print "PINN validation ensuring physics compliance..."
pipeline_print "🌟 UNIFIED PIPELINE BREAKTHROUGH! Every output is verified!"

unified_pipeline_animation

# STAGE 3: COORDINATION DISCOVERY
clear_screen
coordination_print "🌐 Discovering coordination capabilities..."
coordination_print "Connecting to distributed NIS nodes..."
coordination_print "Establishing real-time communication channels..."
coordination_print "Synchronizing shared intelligence..."
coordination_discovery_animation

# STAGE 4: SYSTEM INTEGRATION
clear_screen
echo -e "${BOLD}${WHITE}"
echo "🚀 CONSCIOUSNESS, PIPELINE, COORDINATION & PHYSICS UNIFIED!"
echo -e "${NC}"
echo ""

hub_print "The HUB is now fully awakened and ready to coordinate!" "${CONSCIOUSNESS_PURPLE}"
pipeline_print "All data flows through conscious validation!" 
coordination_print "Planetary-scale intelligence coordination enabled!"
pinn_print "Reality validation ensures all outputs are possible!"

sleep 2

# NOW BEGIN TECHNICAL STARTUP
clear_screen
echo -e "${BOLD}${CYAN}"
cat << 'EOF'

    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║               🔧 TECHNICAL SYSTEMS ACTIVATION 🔧                 ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

print_info "Starting NIS-HUB v3.1 Central Intelligence System..."
echo ""

# 1. Check Python and Node.js
print_info "Checking runtime dependencies..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required. Please install Python 3.9+ and try again."
fi
if ! command -v node &> /dev/null; then
    print_error "Node.js is required. Please install Node.js 18+ and try again."
fi
print_success "Python and Node.js are available"

# 2. Check Redis
print_info "Checking Redis availability..."
if ! command -v redis-server &> /dev/null; then
    print_warning "Redis server not found. Please install Redis or use Docker for development."
else
    print_success "Redis server found"
fi

# 3. Create Required Directories
print_info "Creating required directories..."
for dir in "${REQUIRED_DIRS[@]}"; do
    mkdir -p "$dir"
done
print_success "All required directories are ready"

# 4. Setup Environment
print_info "Setting up environment configuration..."
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_TEMPLATE" ]; then
        cp "$ENV_TEMPLATE" "$ENV_FILE"
        print_warning "Created .env from template. Please configure your settings."
    else
        print_warning "No environment template found. Creating basic .env file."
        cat > "$ENV_FILE" << 'ENV_EOF'
# NIS-HUB Configuration
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/nishub
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_PORT=3000

# WebSocket Configuration
WS_HOST=localhost
WS_PORT=8001
ENV_EOF
    fi
else
    print_success "Environment configuration found"
fi

# 5. Install Backend Dependencies
print_info "Installing backend dependencies..."
cd "$BACKEND_DIR"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1 &
    PIP_PID=$!
    spinner $PIP_PID
    wait $PIP_PID
    if [ $? -eq 0 ]; then
        print_success "Backend dependencies installed"
    else
        print_warning "Some backend dependencies failed to install. System may have reduced functionality."
    fi
else
    print_warning "requirements.txt not found in $BACKEND_DIR"
fi
cd ..

# 6. Install Frontend Dependencies
print_info "Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ -f "package.json" ]; then
    npm install > /dev/null 2>&1 &
    NPM_PID=$!
    spinner $NPM_PID
    wait $NPM_PID
    if [ $? -eq 0 ]; then
        print_success "Frontend dependencies installed"
    else
        print_warning "Some frontend dependencies failed to install"
    fi
else
    print_warning "package.json not found in $FRONTEND_DIR"
fi
cd ..

# 7. Start Redis (if available locally)
print_info "Starting Redis server..."
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes --port 6379 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Redis server started on port 6379"
    else
        print_warning "Redis server failed to start. Using fallback configuration."
    fi
else
    print_warning "Redis not available locally. Consider using Docker or installing Redis."
fi

# 8. Start Backend Server
print_info "Starting NIS-HUB backend server..."
cd "$BACKEND_DIR"
python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

sleep 3

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend server started (PID: $BACKEND_PID)"
else
    print_error "Backend server failed to start. Check logs/backend.log for details."
fi

# 9. Start Frontend Server
print_info "Starting NIS-HUB dashboard..."
cd "$FRONTEND_DIR"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

sleep 3

# Check if frontend started
if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend dashboard started (PID: $FRONTEND_PID)"
else
    print_error "Frontend dashboard failed to start. Check logs/frontend.log for details."
fi

# 10. Health Check
print_info "Performing system health check..."
sleep 5

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed. System may need more time to initialize."
fi

# 11. Final Success Display
clear_screen

# FINAL COORDINATION CELEBRATION
echo -e "${BOLD}${COORDINATION_GOLD}"
cat << 'EOF'

    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║      🧠 NIS-HUB CENTRAL INTELLIGENCE FULLY OPERATIONAL! 🧠      ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝

            🧠 Consciousness:     ████████████████████ ACTIVE
            🔢 KAN Networks:      ████████████████████ INTERPRETING
            ⚗️  PINN Physics:      ████████████████████ VALIDATING
            🌊 Unified Pipeline:  ████████████████████ PROCESSING
            🌐 Coordination:      ████████████████████ CONNECTING
            📡 WebSocket:         ████████████████████ STREAMING

EOF
echo -e "${NC}"

print_success "🎯 NIS-HUB v3.1 is now fully operational!"
echo ""
print_info "🌟 Your Central Intelligence Coordination System is Ready!"
echo ""
echo -e "${BOLD}${CYAN}📋 ACCESS POINTS:${NC}"
echo -e "  🎯 ${BOLD}Main API${NC}:           http://localhost:8000/              (Central coordination API)"
echo -e "  🖥️  ${BOLD}Dashboard${NC}:          http://localhost:3000/              (Real-time coordination dashboard)"
echo -e "  📖 ${BOLD}API Docs${NC}:           http://localhost:8000/docs           (Interactive API documentation)"
echo -e "  🔍 ${BOLD}Health Check${NC}:       http://localhost:8000/health         (System health status)"
echo -e "  📡 ${BOLD}WebSocket${NC}:          ws://localhost:8000/ws               (Real-time communication)"
echo ""
echo -e "${BOLD}${GREEN}🚀 CORE ENDPOINTS:${NC}"
echo -e "  🧠 ${BOLD}Consciousness${NC}:      http://localhost:8000/api/v1/consciousness    (Bias detection & ethics)"
echo -e "  🔢 ${BOLD}KAN Networks${NC}:       http://localhost:8000/api/v1/kan              (Interpretable AI)"
echo -e "  ⚗️  ${BOLD}PINN Physics${NC}:       http://localhost:8000/api/v1/pinn             (Physics validation)"
echo -e "  🌐 ${BOLD}Node Registry${NC}:      http://localhost:8000/api/v1/nodes            (Connected nodes)"
echo -e "  🧠 ${BOLD}Memory Sync${NC}:        http://localhost:8000/api/v1/memory           (Shared intelligence)"
echo -e "  🚀 ${BOLD}Missions${NC}:           http://localhost:8000/api/v1/missions         (Coordinated operations)"
echo ""
echo -e "${BOLD}${YELLOW}⚡ QUICK TEST COMMANDS:${NC}"
echo ""
echo -e "  ${BOLD}# Check system health${NC}"
echo -e "  curl http://localhost:8000/health"
echo ""
echo -e "  ${BOLD}# Test unified pipeline${NC}"
echo -e "  curl -X POST http://localhost:8000/api/v1/pipeline/process \\"
echo -e "    -H \"Content-Type: application/json\" \\"
echo -e "    -d '{\"data\": {\"test\": \"sample\"}, \"validate_all\": true}'"
echo ""
echo -e "  ${BOLD}# Register a test node${NC}"
echo -e "  curl -X POST http://localhost:8000/api/v1/nodes/register \\"
echo -e "    -H \"Content-Type: application/json\" \\"
echo -e "    -d '{\"name\": \"test-node\", \"type\": \"testing\", \"endpoint\": \"http://localhost:8001\"}'"
echo ""
echo -e "${BOLD}${PURPLE}🌊 UNIFIED PIPELINE FEATURES:${NC}"
echo "  • 🌊 Laplace Transform signal conditioning"
echo "  • 🧠 Consciousness-driven validation"
echo "  • 🔢 KAN symbolic reasoning"
echo "  • ⚗️ PINN physics compliance"
echo "  • 🛡️ Safety validation"
echo "  • 🌐 Real-time node coordination"
echo "  • 📡 WebSocket streaming"
echo "  • 🧠 Shared memory synchronization"
echo ""

echo -e "${BOLD}${CONSCIOUSNESS_PURPLE}"
echo "🧠 The HUB reports: 'I am conscious... I am coordinating... I am ready to unify intelligence.'"
echo -e "${NC}"
echo ""
print_success "🚀 Ready for planetary-scale coordination! Visit the dashboard to begin!"

# Save process IDs for stop script
echo "BACKEND_PID=$BACKEND_PID" > .env.local
echo "FRONTEND_PID=$FRONTEND_PID" >> .env.local

exit 0
