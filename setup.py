#!/usr/bin/env python3
"""
Setup script for FinBot project.
This script helps users set up the project environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories."""
    directories = [
        "data/raw/credito",
        "data/raw/debito", 
        "data/processed",
        "data/relatorios",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Set up environment file."""
    env_file = Path(".env")
    env_template = Path("env.template")
    
    if not env_file.exists():
        if env_template.exists():
            shutil.copy(env_template, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("⚠️  No .env file found. Please create one with your OpenAI API key")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def run_tests():
    """Run tests to verify installation."""
    print("🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "run_tests.py"])
        print("✅ Tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        print("⚠️  Continuing anyway, but some features may not work properly")

def main():
    """Main setup function."""
    print("🚀 Setting up FinBot...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Set up environment
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies()
    
    # Run tests
    print("\n🧪 Verifying installation...")
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 FinBot setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Add your CSV files to data/raw/credito/ or data/raw/debito/")
    print("3. Run: streamlit run app/app.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 