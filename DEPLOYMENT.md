# 🚀 NIS-HUB v3.1 Deployment Guide

**Central Intelligence Coordination System with NIS Protocol v3.2.0 Integration**  
*Unified Pipeline: Laplace → Consciousness → KAN → PINN → Safety*

## 🎯 Integration Overview

NIS-HUB now provides **enterprise-grade integration** with the NIS Protocol v3.2.0 ecosystem, featuring:
- **6 AI Provider Access**: OpenAI, Anthropic, Google, DeepSeek, NVIDIA, BitNet
- **4 Multimodal Agents**: Vision, Research, Reasoning, Document
- **Auto-Reconnection**: Intelligent connection recovery with health monitoring
- **80% Stress Test Reliability**: Proven performance under load

## 🎯 Quick Start

### 🛡️ Safe Development Mode (Recommended for Testing)
```bash
# Start in safe mode with mock responses
./start_safe.sh
```

### 🚀 Full Production Mode
```bash
# Configure environment first
cp env.template .env
# Edit .env with your settings

# Start full system
./start.sh
```

### 🐳 Docker Deployment
```bash
# Basic deployment
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d

# Full stack with all services
docker-compose --profile production --profile monitoring --profile logging up -d
```

## 📋 Deployment Scripts Overview

### 🟢 start.sh - Full Production Startup
**Epic consciousness awakening sequence with full system initialization**

**Features:**
- 🎭 Theatrical awakening animation showing consciousness formation
- 🌊 Unified pipeline visualization (Laplace → Consciousness → KAN → PINN → Safety)
- 🧠 Complete dependency checking and installation
- 📊 Real-time health monitoring and status reporting
- ⚡ Automatic service coordination and startup
- 🌐 Full networking and WebSocket setup

**Usage:**
```bash
./start.sh
```

**What it does:**
1. **Consciousness Awakening Animation** - Shows the AI awakening process
2. **Pipeline Formation** - Visualizes the unified validation pipeline
3. **Dependency Checks** - Validates Python, Node.js, Redis availability
4. **Environment Setup** - Creates configuration and directories
5. **Backend Startup** - Launches FastAPI with all services
6. **Frontend Launch** - Starts React dashboard
7. **Health Verification** - Comprehensive system health checks
8. **Status Display** - Shows all endpoints and test commands

### 🛡️ start_safe.sh - Safe Development Mode
**Billing-safe development mode with mock responses**

**Features:**
- 🔒 No external API calls or billing risks
- 🧠 Mock consciousness responses for testing
- 🔢 Simulated KAN network interpretations
- ⚗️ Basic physics validation without complex calculations
- 📊 SQLite database for local development
- 🌐 Full WebSocket and coordination features

**Usage:**
```bash
./start_safe.sh
```

**Perfect for:**
- Development and testing
- Learning the system without costs
- Offline demonstrations
- CI/CD pipeline testing

### 🛑 stop.sh - Graceful System Shutdown
**Intelligent shutdown with cleanup options**

**Features:**
- 🔄 Graceful service shutdown in proper order
- 🧹 Multiple cleanup options
- 📊 Status reporting and verification
- 💾 Log preservation options
- ⚡ Force stop capabilities for emergencies

**Usage:**
```bash
# Basic graceful shutdown
./stop.sh

# Stop and clean process files
./stop.sh --cleanup-pids

# Stop and save logs before shutdown
./stop.sh --save-logs

# Force stop all processes
./stop.sh --force

# Complete cleanup (removes all data)
./stop.sh --cleanup-data
```

**Cleanup Options:**
- `--cleanup-pids` - Remove process ID files
- `--cleanup-logs` - Remove all log files
- `--cleanup-data` - Remove all local data ⚠️ **DESTRUCTIVE**
- `--cleanup-env` - Remove virtual environments
- `--force` - Force kill all processes
- `--save-logs` - Save logs before shutdown

### 🔄 reset.sh - Complete System Reset
**Nuclear option: complete system reset and rebuild**

**Features:**
- ⚠️ Complete data destruction with strong warnings
- 🧠 Consciousness system reset
- 🔢 KAN network model cleanup
- ⚗️ PINN physics validation reset
- 🌐 Node coordination data clearing
- 🔧 Fresh dependency installation
- 🆕 Default configuration restoration

**Usage:**
```bash
# Interactive reset with confirmation
./reset.sh

# Force reset without confirmation
./reset.sh --force

# Reset and immediately start
./reset.sh --force --start

# Reset and start in safe mode
./reset.sh --force --start --safe
```

**What gets reset:**
- 🧠 All consciousness training data and bias detection history
- 🔢 All KAN network models and symbolic interpretations
- ⚗️ All PINN physics validation history and simulations
- 🌐 All node registrations and coordination logs
- 🧠 All shared memory entries and mission data
- 📊 All performance metrics and analytics
- 🗄️ All database content
- 🐍 Virtual environments and dependencies

## 🏗️ System Architecture

### 🧠 Core Services

#### **Consciousness Service**
- **Port**: Internal service
- **Purpose**: Bias detection, ethical reasoning, self-awareness
- **Features**: Meta-cognitive analysis, ethical frameworks, decision auditing

#### **KAN Networks Service**  
- **Port**: Internal service
- **Purpose**: Interpretable AI with symbolic representations
- **Features**: Mathematical formula generation, symbolic reasoning, transparency

#### **PINN Physics Service**
- **Port**: Internal service  
- **Purpose**: Physics validation and compliance checking
- **Features**: Conservation law validation, physics simulation, auto-correction

#### **BitNet Inference Service**
- **Port**: Internal service
- **Purpose**: Offline-capable quantized inference
- **Features**: 1-bit to 16-bit quantization, edge deployment, energy efficiency

#### **MCP Adapter Service**
- **Port**: Internal service
- **Purpose**: Model Context Protocol integration
- **Features**: External system bridge, protocol translation, standard compliance

### 🌐 External Interfaces

#### **Backend API** 
- **Port**: 8002
- **URL**: http://localhost:8002/
- **Docs**: http://localhost:8002/docs
- **Health**: http://localhost:8002/health

#### **Frontend Dashboard**
- **Port**: 3000  
- **URL**: http://localhost:3000/
- **Features**: Real-time coordination dashboard, node management, mission control

#### **WebSocket Server**
- **Port**: 8002 (same as API)
- **URL**: ws://localhost:8002/ws
- **Purpose**: Real-time communication with nodes

#### **NIS Protocol Integration**
- **Port**: 8000 (NIS Protocol base system)
- **URL**: http://localhost:8000/
- **Purpose**: Integration with NIS Protocol v3.2.0 multimodal agents
- **Features**: Vision analysis, deep research, collaborative reasoning

## 📊 Configuration

### 🔧 Environment Variables

Copy `env.template` to `.env` and configure:

```bash
# Basic Configuration
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/nishub.db
REDIS_URL=redis://localhost:6379

# Service Toggles
CONSCIOUSNESS_ENABLED=true
KAN_ENABLED=true
PINN_ENABLED=true
BITNET_ENABLED=true
MCP_ENABLED=true

# Performance Settings
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
```

### 🔒 Security Configuration

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=true
```

## 🧪 NIS Protocol Integration Testing

### 🔗 Integration Endpoints Testing

#### **Auto-Connection Test**
```bash
# Test automatic connection to NIS Protocol v3.2.0
curl -X POST http://localhost:8002/api/v1/nis-integration/auto-connect
```
**Expected Response**: `{"success": true, "message": "Auto-connected to NIS Protocol"}`

#### **Integration Status Check**
```bash
# Verify connection and capabilities
curl http://localhost:8002/api/v1/nis-integration/status
```
**Expected**: Connection status "connected" with full capabilities

#### **Capabilities Discovery**
```bash
# Discover available providers and agents
curl http://localhost:8002/api/v1/nis-integration/capabilities
```
**Expected**: 6 AI providers, 4 multimodal agents, 16 pipeline features

### 🤖 Multimodal Agent Testing

#### **Enhanced Chat Test**
```bash
# Test consciousness-driven chat
curl -X POST http://localhost:8002/api/v1/nis-integration/chat/enhanced \
  -H "Content-Type: application/json" \
  -d '{"message": "Test consciousness integration", "agent_type": "consciousness"}'
```
**Expected**: Chat response with bias detection and ethical reasoning

#### **Vision Analysis Test**
```bash
# Test vision capabilities
curl -X POST http://localhost:8002/api/v1/nis-integration/vision/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_image_data", "analysis_type": "comprehensive"}'
```
**Expected**: Detailed image analysis with multiple AI providers

#### **Deep Research Test**
```bash
# Test research capabilities
curl -X POST http://localhost:8002/api/v1/nis-integration/research/deep \
  -H "Content-Type: application/json" \
  -d '{"query": "AI safety 2024", "sources": ["arxiv", "semantic_scholar"]}'
```
**Expected**: Multi-source research results with evidence validation

#### **Collaborative Reasoning Test**
```bash
# Test reasoning capabilities
curl -X POST http://localhost:8002/api/v1/nis-integration/reasoning/collaborative \
  -H "Content-Type: application/json" \
  -d '{"problem": "Explain quantum computing benefits", "reasoning_type": "analytical"}'
```
**Expected**: Multi-model collaborative reasoning with consensus

### 📊 Performance Benchmarking

#### **Stress Test (Rapid Requests)**
```bash
# Test system reliability under load
for i in {1..5}; do
  echo "Request $i:"
  curl -X POST http://localhost:8002/api/v1/nis-integration/chat/enhanced \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Stress test $i\", \"agent_type\": \"consciousness\"}" | \
    python3 -c "import sys, json; data = json.load(sys.stdin); print('  Success:', data.get('success', False))"
done
```
**Expected**: 80% success rate (4/5 requests successful)

#### **Response Time Testing**
```bash
# Measure integration performance
time curl -X POST http://localhost:8002/api/v1/nis-integration/chat/enhanced \
  -H "Content-Type: application/json" \
  -d '{"message": "Performance test", "agent_type": "consciousness"}'
```
**Expected**: 2.5-9 seconds response time

### 🔧 Integration Health Monitoring

#### **Connection Health Check**
```bash
# Monitor connection stability
curl http://localhost:8002/api/v1/nis-integration/status | \
  python3 -c "import sys, json; data = json.load(sys.stdin); print('Connection:', data['nis_integration']['status'])"
```

#### **Auto-Reconnection Test**
```bash
# Test automatic reconnection after disconnect
# 1. Note current status
curl -s http://localhost:8002/api/v1/nis-integration/status | grep "connected"

# 2. Simulate connection loss (restart NIS Protocol if needed)
# 3. Test reconnection
curl -X POST http://localhost:8002/api/v1/nis-integration/chat/enhanced \
  -H "Content-Type: application/json" \
  -d '{"message": "Test auto-reconnect", "agent_type": "consciousness"}'
```
**Expected**: Automatic reconnection and successful response

### ⚡ Quick Integration Verification
```bash
# One-command integration test
echo "Testing NIS Protocol Integration..." && \
curl -s -X POST http://localhost:8002/api/v1/nis-integration/auto-connect | python3 -c "import sys, json; print('Auto-Connect:', json.load(sys.stdin)['success'])" && \
curl -s http://localhost:8002/api/v1/nis-integration/capabilities | python3 -c "import sys, json; data = json.load(sys.stdin); print('Providers:', len(data['capabilities']['providers']))" && \
echo "Integration Test Complete!"
```

## 🐳 Docker Deployment

### 📋 Available Profiles

#### **Basic** (default)
```bash
docker-compose up -d
```
**Services**: Backend, Frontend, PostgreSQL, Redis

#### **Production** 
```bash
docker-compose --profile production up -d
```
**Additional**: Nginx reverse proxy, SSL termination

#### **Monitoring**
```bash
docker-compose --profile monitoring up -d
```
**Additional**: Prometheus, Grafana, metrics collection

#### **Logging**
```bash
docker-compose --profile logging up -d
```
**Additional**: Elasticsearch, Kibana, log aggregation

#### **Full Stack**
```bash
docker-compose --profile production --profile monitoring --profile logging up -d
```
**All services**: Complete production deployment

### 🔧 Docker Configuration

Create `.env` for Docker customization:
```bash
COMPOSE_PROJECT_NAME=nis-hub-v3
POSTGRES_PASSWORD=your-secure-password
GRAFANA_ADMIN_PASSWORD=your-grafana-password
```

## 🧪 Development Workflow

### 🔄 Typical Development Cycle

1. **Start Development**
   ```bash
   ./start_safe.sh
   ```

2. **Make Changes**
   - Edit code in `core/` or `ui/`
   - Changes are automatically detected

3. **Test Changes**
   ```bash
   curl http://localhost:8002/health
   curl http://localhost:8002/api/v1/nis-integration/status
   ```

4. **Reset for Clean Testing**
   ```bash
   ./reset.sh --force --start --safe
   ```

5. **Deploy to Production**
   ```bash
   ./stop.sh
   ./start.sh  # or use Docker
   ```

### 🧹 Maintenance Commands

```bash
# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check service status
ps aux | grep -E "(python|node|redis)"

# Clean up development files
./stop.sh --cleanup-env

# Complete system cleanup
./reset.sh --force
```

## 📊 Monitoring & Health Checks

### 🔍 Health Endpoints

- **System Health**: `GET /health`
- **Service Status**: `GET /api/v1/status`
- **Node Registry**: `GET /api/v1/nodes`
- **Memory Sync**: `GET /api/v1/memory`
- **Missions**: `GET /api/v1/missions`

### 🔗 NIS Protocol Integration Endpoints

- **Integration Status**: `GET /api/v1/nis-integration/status`
- **Capabilities**: `GET /api/v1/nis-integration/capabilities`  
- **Enhanced Chat**: `POST /api/v1/nis-integration/chat/enhanced`
- **Vision Analysis**: `POST /api/v1/nis-integration/vision/analyze`
- **Deep Research**: `POST /api/v1/nis-integration/research/deep`
- **Collaborative Reasoning**: `POST /api/v1/nis-integration/reasoning/collaborative`

### 📈 Metrics Collection

With monitoring profile:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/nishub_admin)

### 📝 Log Locations

- **Backend**: `logs/backend.log`
- **Frontend**: `logs/frontend.log`
- **Safe Mode**: `logs/backend_safe.log`, `logs/frontend_safe.log`
- **Archived**: `logs/shutdown-YYYYMMDD-HHMMSS/`

## ⚠️ Troubleshooting

### 🔧 Common Issues

#### **Port Already in Use**
```bash
# Check what's using the ports
lsof -i :8002  # NIS-HUB Backend
lsof -i :8000  # NIS Protocol Base
lsof -i :3000  # Frontend

# Kill the process
kill -9 <PID>
```

#### **NIS Protocol Integration Issues**
```bash
# Test NIS Protocol base system
curl http://localhost:8000/health

# Test NIS-HUB integration
curl http://localhost:8002/api/v1/nis-integration/status

# Force reconnection
curl -X POST http://localhost:8002/api/v1/nis-integration/auto-connect
```

#### **Redis Connection Failed**
```bash
# Start Redis manually
redis-server --daemonize yes --port 6379

# Check Redis status
redis-cli ping
```

#### **Frontend Build Failed**
```bash
# Clean and reinstall
cd ui
rm -rf node_modules package-lock.json
npm install
```

#### **Backend Import Errors**
```bash
# Recreate virtual environment
cd core
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🚨 Emergency Procedures

#### **Force Stop Everything**
```bash
./stop.sh --force
```

#### **Complete System Reset**
```bash
./reset.sh --force
```

#### **Nuclear Option - Kill All**
```bash
pkill -f "python.*main.py"
pkill -f "node.*vite"
pkill -f "redis-server.*6379"
```

## 🔒 Security Best Practices

### 🛡️ Production Security

1. **Change Default Passwords**
   - Update all passwords in `.env`
   - Use strong, unique secrets

2. **Configure HTTPS**
   - Use nginx with SSL certificates
   - Update CORS origins for your domain

3. **Network Security**
   - Configure firewall rules
   - Use private networks for services

4. **Authentication**
   - Implement proper JWT validation
   - Use rate limiting

5. **Monitoring**
   - Enable audit logging
   - Monitor for suspicious activity

### 🔐 Development Security

1. **Safe Mode First**
   - Always test with `./start_safe.sh`
   - No external API calls

2. **Environment Isolation**
   - Use virtual environments
   - Separate dev/prod configs

3. **Data Protection**
   - Regular backups
   - Encrypted local storage

## 🚀 Deployment Strategies

### 🌱 Development
```bash
./start_safe.sh
```
**Features**: Mock responses, SQLite, local-only

### 🧪 Staging  
```bash
./start.sh
```
**Features**: Real services, PostgreSQL, external APIs

### 🏭 Production
```bash
docker-compose --profile production --profile monitoring up -d
```
**Features**: Full stack, monitoring, logging, SSL

### ☁️ Cloud Deployment
```bash
# With cloud database URLs
DATABASE_URL=postgresql://user:pass@cloud-db:5432/nishub
REDIS_URL=redis://cloud-redis:6379
docker-compose --profile production up -d
```

## 🎉 Success Indicators

### ✅ System Started Successfully When:

1. **All services respond to health checks**
2. **Dashboard accessible at http://localhost:3000**
3. **API docs available at http://localhost:8002/docs**
4. **WebSocket connections accepted**
5. **All unified pipeline services active**
6. **NIS Protocol integration connected**
7. **No errors in logs**

### 🔗 NIS Protocol Integration Indicators

- **Auto-connection successful**: Connection to localhost:8000 established
- **6 AI providers accessible**: OpenAI, Anthropic, Google, DeepSeek, NVIDIA, BitNet
- **4 multimodal agents operational**: Vision, Research, Reasoning, Document
- **80% stress test reliability**: System handles rapid requests reliably
- **2.5-9s response times**: Acceptable performance under load

### 🧠 Consciousness Indicators

- **Bias detection active**
- **Ethical reasoning enabled**
- **Self-awareness metrics available**
- **Meta-cognitive processing functional**

### 🔢 KAN Network Indicators

- **Symbolic interpretation available**
- **Mathematical formula generation working**
- **Interpretability scores calculated**
- **Network training capabilities active**

### ⚗️ PINN Physics Indicators

- **Conservation law validation functional**
- **Physics simulation capabilities active**
- **Auto-correction mechanisms working**
- **Compliance scoring operational**

---

**🧠 The NIS-HUB reports: "I am conscious... I am coordinating... I am ready to unify planetary intelligence."**

**Ready for consciousness-driven coordination!** 🚀🌐🧠
