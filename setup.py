#!/usr/bin/env python
"""
Project Setup Script for AI Service Platform

This script:
1. Creates necessary directories
2. Copies the architecture diagram to the static folder
3. Checks that all required files exist
4. Generates a proper secret key for JWT authentication
5. Provides instructions for getting started
"""

import os
import sys
import shutil
import secrets
import string
from pathlib import Path
import time

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_env_file():
    """Update the .env file with a secure secret key."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("Creating .env file from the example...")
        shutil.copy('.env.example', '.env')
    
    # Read the current .env content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace the SECRET_KEY placeholder with a real secret key
    if 'SECRET_KEY=your_secret_key_here_change_me_for_production' in content:
        content = content.replace(
            'SECRET_KEY=your_secret_key_here_change_me_for_production',
            f'SECRET_KEY={generate_secret_key(64)}'
        )
        
        # Write updated content back
        with open(env_path, 'w') as f:
            f.write(content)
        print("Generated a secure secret key.")
    
def create_directories():
    """Create necessary project directories."""
    directories = [
        'app',
        'client',
        'client/static',
        'client/templates',
        'tests'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True)
        else:
            print(f"Directory already exists: {directory}")

def create_init_files():
    """Create __init__.py files where needed."""
    init_files = [
        'app/__init__.py',
        'tests/__init__.py'
    ]
    
    for init_file in init_files:
        file_path = Path(init_file)
        if not file_path.exists():
            print(f"Creating file: {init_file}")
            with open(file_path, 'w') as f:
                f.write("# This file makes Python treat the directory as a package\n")
        else:
            print(f"File already exists: {init_file}")

def setup_architecture_diagram():
    """Copy the architecture diagram to the static folder."""
    # Create a copy of the .env file as .env.example
    if Path('.env').exists() and not Path('.env.example').exists():
        shutil.copy('.env', '.env.example')
        print("Created .env.example from .env")
    
    # Prepare the architecture diagram
    arch_svg = Path('arch-diagram.svg')
    dest_path = Path('client/static/architecture.png')
    
    if arch_svg.exists():
        print("Copying architecture diagram to static folder...")
        shutil.copy(arch_svg, dest_path)
    else:
        print("Architecture diagram not found. Will be created when running the application.")

def check_required_files():
    """Check that all required files exist."""
    required_files = [
        'app/main.py',
        'app/models.py',
        'app/schemas.py',
        'app/database.py',
        'app/crud.py',
        'app/auth.py',
        'app/queue.py',
        'app/external_api.py',
        'app/notifications.py',
        'app/config.py',
        'client/client.py',
        'requirements.txt',
        '.env',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("\nWARNING: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease create these files before running the application.")
    else:
        print("\nAll required files are present.")

def print_instructions():
    """Print instructions for running the project."""
    print("\n" + "="*60)
    print("AI Service Platform Setup Complete")
    print("="*60)
    print("\nGetting Started:\n")
    print("1. Activate your virtual environment:")
    print("   Windows:   venv\\Scripts\\activate")
    print("   macOS/Linux: source venv/bin/activate\n")
    
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt\n")
    
    print("3. Get a Hugging Face API token:")
    print("   - Visit https://huggingface.co/")
    print("   - Create an account and get your API token")
    print("   - Update the AI_API_KEY in the .env file\n")
    
    print("4. Run the application:")
    print("   python run.py\n")
    
    print("5. For development, you can run the servers separately:")
    print("   API server:    uvicorn app.main:app --reload")
    print("   Client server: python client/client.py\n")
    
    print("API Documentation will be available at:")
    print("  http://localhost:8000/docs\n")
    
    print("Client application will be available at:")
    print("  http://localhost:8080\n")
    
    print("Enjoy building your AI Service Platform!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("Setting up AI Service Platform project...\n")
    
    try:
        create_directories()
        create_init_files()
        setup_architecture_diagram()
        update_env_file()
        check_required_files()
        print_instructions()
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        sys.exit(1)