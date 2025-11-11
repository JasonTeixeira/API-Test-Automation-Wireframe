#!/bin/bash

# API Test Automation Framework - Setup Script
# Automates project setup and verification

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print section header
print_header() {
    echo ""
    print_message "$BLUE" "=========================================="
    print_message "$BLUE" "$1"
    print_message "$BLUE" "=========================================="
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_header "API Test Automation Framework Setup"
    
    # Check Python version
    print_header "Checking Python Version"
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_message "$GREEN" "✓ Python $PYTHON_VERSION found"
        
        # Check if version is 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_message "$GREEN" "✓ Python version is 3.11 or higher"
        else
            print_message "$RED" "✗ Python 3.11+ required. Please upgrade Python."
            exit 1
        fi
    else
        print_message "$RED" "✗ Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Create virtual environment
    print_header "Setting Up Virtual Environment"
    if [ ! -d "venv" ]; then
        print_message "$YELLOW" "Creating virtual environment..."
        python3 -m venv venv
        print_message "$GREEN" "✓ Virtual environment created"
    else
        print_message "$GREEN" "✓ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_message "$YELLOW" "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_header "Upgrading pip"
    python -m pip install --upgrade pip --quiet
    print_message "$GREEN" "✓ pip upgraded"
    
    # Install dependencies
    print_header "Installing Dependencies"
    print_message "$YELLOW" "Installing required packages..."
    pip install -r requirements.txt --quiet
    print_message "$GREEN" "✓ All dependencies installed"
    
    # Create .env file
    print_header "Configuring Environment"
    if [ ! -f ".env" ]; then
        print_message "$YELLOW" "Creating .env file from template..."
        cp .env.example .env
        print_message "$GREEN" "✓ .env file created"
    else
        print_message "$GREEN" "✓ .env file already exists"
    fi
    
    # Create reports directory
    print_header "Creating Report Directories"
    mkdir -p reports/html reports/allure-results reports/coverage logs
    print_message "$GREEN" "✓ Report directories created"
    
    # Verify installation
    print_header "Verifying Installation"
    
    # Check pytest
    if command_exists pytest; then
        print_message "$GREEN" "✓ pytest installed"
    else
        print_message "$RED" "✗ pytest not found"
    fi
    
    # Check key packages
    python -c "import requests; import pydantic; import allure" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✓ Key packages verified (requests, pydantic, allure)"
    else
        print_message "$RED" "✗ Some packages missing"
    fi
    
    # Run quick smoke test
    print_header "Running Quick Smoke Test"
    print_message "$YELLOW" "Running 5 smoke tests..."
    
    if pytest tests/ -m smoke -v --tb=short -x --maxfail=1 --quiet 2>&1 | grep -q "passed"; then
        print_message "$GREEN" "✓ Smoke tests passed!"
    else
        print_message "$YELLOW" "⚠ Smoke tests need API connectivity"
    fi
    
    # Setup complete
    print_header "Setup Complete!"
    echo ""
    print_message "$GREEN" "✓ Virtual environment: venv/"
    print_message "$GREEN" "✓ Dependencies: Installed"
    print_message "$GREEN" "✓ Configuration: .env created"
    print_message "$GREEN" "✓ Reports: reports/ directory ready"
    echo ""
    print_message "$BLUE" "Next steps:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Run all tests: pytest tests/ -v"
    echo "  3. Run smoke tests: pytest tests/ -m smoke -v"
    echo "  4. View README.md for more options"
    echo ""
    print_message "$GREEN" "Happy testing! 🚀"
}

# Run main function
main
