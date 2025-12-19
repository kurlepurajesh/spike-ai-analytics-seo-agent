#!/bin/bash

# Fix for gRPC DNS resolution issues
export GRPC_DNS_RESOLVER=native
export GRPC_VERBOSITY=ERROR

# Kill any existing server process on port 8080
echo "Stopping any existing server..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
pkill -f "uvicorn main:app" || true
sleep 2

# 1. Install 'uv' for extremely fast package management (Recommended by PS)
echo "Installing uv for faster setup..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
source $HOME/.cargo/env || true

# 2. Create Virtual Environment at project root as required
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
else
    echo "Virtual environment already exists."
fi

# 3. Activate the environment
source .venv/bin/activate

# 4. Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# 5. Start the server in the background
# We bind to 0.0.0.0 to make it accessible externally, and strictly to port 8080
echo "Starting FastAPI server on port 8080..."
GRPC_DNS_RESOLVER=native GRPC_VERBOSITY=ERROR nohup uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4 > server.log 2>&1 &

# 6. (Optional) Health check to ensure it started before script exits
echo "Waiting for server to launch..."
sleep 5
if pgrep -f "uvicorn" > /dev/null; then
    echo "Server is running (PID: $(pgrep -f "uvicorn"))"
else
    echo "Server failed to start. Check server.log:"
    cat server.log
    exit 1
fi
