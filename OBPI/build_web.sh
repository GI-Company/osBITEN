#!/bin/bash
echo "Building OBPI for Web Deployment..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install requirements
pip install -r requirements.txt

# Additional web-specific requirements
pip install flask gunicorn

# Build with PyInstaller
pyinstaller obpi_web.spec

echo "Build complete. Web application is in dist/OBPI-Web"

# Create a web server wrapper script
cat > dist/OBPI-Web/run_web_server.py << EOL
#!/usr/bin/env python3
import os
import sys
import logging
from flask import Flask, send_from_directory, request, jsonify
import subprocess

# Add the current directory to the path so we can import the OBPI modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('OBPI_Web_Server')

app = Flask(__name__)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'src/index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# API endpoints that would normally be handled by pywebview's js_api
@app.route('/api/<path:endpoint>', methods=['GET', 'POST'])
def api_proxy(endpoint):
    # This is a placeholder. In a real implementation, you would need to:
    # 1. Import the actual backend API modules
    # 2. Call the appropriate functions based on the endpoint
    # 3. Return the results as JSON

    if request.method == 'POST':
        data = request.json
        logger.info(f"API POST request to {endpoint} with data: {data}")
        # Example: result = your_backend_function(data)
        return jsonify({"status": "success", "message": f"Received POST request to {endpoint}"})
    else:
        logger.info(f"API GET request to {endpoint}")
        # Example: result = your_backend_function()
        return jsonify({"status": "success", "message": f"Received GET request to {endpoint}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting OBPI Web Server on port {port}")
    app.run(host='0.0.0.0', port=port)
EOL

chmod +x dist/OBPI-Web/run_web_server.py

# Create a Dockerfile for containerized deployment
cat > dist/OBPI-Web/Dockerfile << EOL
FROM python:3.9-slim

WORKDIR /app

# Copy the built application
COPY . /app/

# Install required packages
RUN pip install flask gunicorn

# Expose the port
EXPOSE 5000

# Run the web server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run_web_server:app"]
EOL

# Create a docker-compose.yml file for easy deployment
cat > dist/OBPI-Web/docker-compose.yml << EOL
version: '3'
services:
  obpi-web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - PORT=5000
EOL

echo "Web server wrapper script and Docker configuration created."
echo "To run the web server locally: cd dist/OBPI-Web && python run_web_server.py"
echo "To build and run with Docker: cd dist/OBPI-Web && docker-compose up -d"
