"""
AI Service Platform Runner Script

This script:
1. Sets up the project directories
2. Creates architecture diagram
3. Starts both API and client servers
"""

import os
import sys
import shutil
import subprocess
import time
import webbrowser
from pathlib import Path
import threading
import signal
import atexit

# Ensure we're in the correct directory
ROOT_DIR = Path(__file__).parent.absolute()
os.chdir(ROOT_DIR)

# Create directories if they don't exist
directories = [
    "app",
    "client",
    "client/static",
    "client/templates",
    "tests"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Create __init__.py files where needed
init_files = [
    "app/__init__.py",
    "tests/__init__.py"
]

for init_file in init_files:
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# This file is required to make Python treat this directory as a package.")

# Save the architecture diagram to static folder
if os.path.exists("architecture_diagram.svg"):
    shutil.copy("architecture_diagram.svg", "client/static/architecture.png")

# Global variables for processes
api_process = None
client_process = None

def start_api_server():
    """Start the FastAPI server"""
    global api_process
    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    print("API server running at http://127.0.0.1:8000")
    return api_process

def start_client_server():
    """Start the client FastAPI server"""
    global client_process
    print("Starting client server...")
    client_process = subprocess.Popen(
        [sys.executable, "client/client.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    print("Client server running at http://127.0.0.1:8080")
    return client_process

def log_output(process, prefix):
    """Log the output of a process"""
    for line in iter(process.stdout.readline, ""):
        print(f"{prefix}: {line.strip()}")

def cleanup():
    """Clean up processes on exit"""
    if api_process:
        print("Stopping API server...")
        api_process.terminate()
    
    if client_process:
        print("Stopping client server...")
        client_process.terminate()

# Register cleanup function
atexit.register(cleanup)

if __name__ == "__main__":
    try:
        # Start servers
        api_proc = start_api_server()
        client_proc = start_client_server()
        
        # Start threads to log output
        api_logger = threading.Thread(target=log_output, args=(api_proc, "API"))
        client_logger = threading.Thread(target=log_output, args=(client_proc, "CLIENT"))
        
        api_logger.daemon = True
        client_logger.daemon = True
        
        api_logger.start()
        client_logger.start()
        
        # Open browser tabs
        time.sleep(2)  # Give servers a moment to fully start
        webbrowser.open("http://127.0.0.1:8080")  # Client
        webbrowser.open("http://127.0.0.1:8000/docs")  # API docs
        
        print("\nPress Ctrl+C to stop servers...")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        cleanup()
        print("Done.")