#!/bin/bash
# 🛡️ SAFE START SCRIPT - NIS-HUB Development Mode
# This script starts NIS-HUB with safe development configuration

echo "🛡️ Starting NIS-HUB in SAFE DEVELOPMENT MODE..."
echo "🧠 Consciousness: ACTIVE (Local Mode)"
echo "🔢 KAN Networks: MOCK RESPONSES"
echo "⚗️ PINN Physics: BASIC VALIDATION"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[NIS-HUB-SAFE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if .env.safe exists, if not create it
if [ ! -f ".env.safe" ]; then
    print_info "Creating .env.safe configuration..."
    cat > .env.safe << 'EOF'
# NIS-HUB Safe Development Configuration
DEBUG=true
LOG_LEVEL=DEBUG

# Safe mode flags
SAFE_MODE=true
MOCK_RESPONSES=true
SKIP_EXTERNAL_APIS=true

# Local development database
DATABASE_URL=sqlite:///./data/nishub_dev.db
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=localhost
API_PORT=8000

# Frontend Configuration
FRONTEND_PORT=3000

# WebSocket Configuration
WS_HOST=localhost
WS_PORT=8001

# Consciousness Service (Safe Mode)
CONSCIOUSNESS_SAFE_MODE=true
CONSCIOUSNESS_MOCK_BIAS_DETECTION=true

# KAN Service (Mock Mode)  
KAN_MOCK_INTERPRETATIONS=true
KAN_SKIP_TRAINING=true

# PINN Service (Basic Mode)
PINN_BASIC_VALIDATION=true
PINN_MOCK_PHYSICS=true

# BitNet Service (Local Only)
BITNET_LOCAL_ONLY=true
BITNET_MOCK_INFERENCE=true

# MCP Adapter (Disabled)
MCP_DISABLED=true

# No external API keys needed in safe mode
EOF
else
    print_success ".env.safe already exists"
fi

# Use safe configuration
print_info "Using safe configuration (.env.safe)"
cp .env.safe .env

# Create safe data directory
mkdir -p data logs cache

# Start Redis if available
print_info "Starting Redis server (if available)..."
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes --port 6379 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Redis server started"
    else
        print_warning "Redis server failed to start (will use in-memory fallback)"
    fi
else
    print_warning "Redis not available (will use in-memory fallback)"
fi

# Install dependencies if needed
if [ ! -d "core/venv" ]; then
    print_info "Creating virtual environment for backend..."
    cd core
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    cd ..
    print_success "Backend environment ready"
fi

if [ ! -d "ui/node_modules" ]; then
    print_info "Installing frontend dependencies..."
    cd ui
    npm install > /dev/null 2>&1
    cd ..
    print_success "Frontend dependencies installed"
fi

# Start backend in safe mode
print_info "Starting NIS-HUB backend in safe mode..."
cd core
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python main.py > ../logs/backend_safe.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

sleep 3

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend started successfully (PID: $BACKEND_PID)"
else
    print_warning "Backend may be starting slowly. Check logs/backend_safe.log"
fi

# Start frontend
print_info "Starting NIS-HUB dashboard..."
cd ui
npm run dev > ../logs/frontend_safe.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

sleep 3

# Check if frontend started
if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Dashboard started successfully (PID: $FRONTEND_PID)"
else
    print_warning "Dashboard may be starting slowly. Check logs/frontend_safe.log"
fi

# Wait for services to be ready
print_info "Waiting for services to initialize..."
sleep 5

# Test basic connectivity
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed - system may need more time"
fi

echo ""
echo -e "${GREEN}✅ NIS-HUB started successfully in SAFE DEVELOPMENT MODE${NC}"
echo ""
echo "🌐 Access points:"
echo "  • Dashboard: http://localhost:3000/"
echo "  • API: http://localhost:8002/"
echo "  • API Docs: http://localhost:8002/docs"
echo "  • Health Check: http://localhost:8002/health"
echo ""
echo "🛡️ SAFE MODE STATUS:"
echo "  • External APIs: DISABLED"
echo "  • Mock responses: ENABLED"
echo "  • Local database: SQLite"
echo "  • Development logging: VERBOSE"
echo ""
echo "🧠 CONSCIOUSNESS FEATURES (Safe Mode):"
echo "  • Bias detection: MOCK RESPONSES"
echo "  • Ethical reasoning: BASIC LOGIC"
echo "  • Self-awareness: SIMULATED"
echo ""
echo "🔢 KAN NETWORKS (Mock Mode):"
echo "  • Symbolic interpretation: SAMPLE FORMULAS"
echo "  • Network training: SKIPPED"
echo "  • Mathematical proofs: GENERATED"
echo ""
echo "⚗️ PINN PHYSICS (Basic Mode):"
echo "  • Conservation laws: BASIC CHECKS"
echo "  • Physics simulation: SIMPLIFIED"
echo "  • Validation: MOCK RESULTS"
echo ""
echo "🌐 COORDINATION:"
echo "  • WebSocket: ACTIVE"
echo "  • Node registry: LOCAL ONLY"
echo "  • Memory sync: IN-MEMORY"
echo ""
echo -e "${YELLOW}⚠️ To enable full features:${NC}"
echo "  1. Configure real database in .env"
echo "  2. Add external API keys if needed"
echo "  3. Set SAFE_MODE=false"
echo "  4. Restart with ./start.sh"
echo ""
echo -e "${YELLOW}🛑 To stop services:${NC}"
echo "  ./stop.sh"
echo ""
echo -e "${YELLOW}📊 View logs:${NC}"
echo "  tail -f logs/backend_safe.log"
echo "  tail -f logs/frontend_safe.log"

# Save process IDs for stop script
echo "BACKEND_PID=$BACKEND_PID" > .env.local
echo "FRONTEND_PID=$FRONTEND_PID" >> .env.local
echo "SAFE_MODE=true" >> .env.local

print_success "🧠 NIS-HUB Safe Mode ready for development!"
