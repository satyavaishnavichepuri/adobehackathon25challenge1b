#!/bin/bash

# Persona-Driven Document Intelligence - Execution Script

echo "=== Persona-Driven Document Intelligence System ==="
echo ""

# Function to show usage
show_usage() {
    echo "Usage: ./run.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  local      Run locally (requires Python dependencies)"
    echo "  docker     Build and run with Docker"
    echo "  test       Run with sample test case"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh local --documents ./documents --persona 'PhD Researcher' --job 'Literature review'"
    echo "  ./run.sh docker"
    echo "  ./run.sh test"
}

# Function to run locally
run_local() {
    echo "Running locally..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not installed."
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Run the application with provided arguments
    python main.py "${@:2}"
}

# Function to run with Docker
run_docker() {
    echo "Building and running with Docker..."
    
    # Build the Docker image
    echo "Building Docker image..."
    docker build -t persona-doc-intelligence .
    
    # Create input and output directories
    mkdir -p input output
    
    # Run the container
    echo "Running Docker container..."
    docker run -it --rm \
        -v "$(pwd)/input:/app/input" \
        -v "$(pwd)/output:/app/output" \
        persona-doc-intelligence \
        python main.py \
        --documents /app/input \
        --persona "PhD Researcher in Computational Biology" \
        --job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks" \
        --output /app/output/results.json
}

# Function to run test case
run_test() {
    echo "Running test case..."
    
    # Create test directories
    mkdir -p test_input test_output
    
    # Check if test PDFs exist
    if [ ! -f "test_input/sample.pdf" ]; then
        echo "Warning: No test PDFs found in test_input directory."
        echo "Please add some PDF files to test_input/ to run the test."
        echo ""
        echo "For now, showing the system structure..."
        python main.py --help
        return
    fi
    
    # Run test case
    if command -v python3 &> /dev/null; then
        run_local --documents test_input --persona "PhD Researcher in Computational Biology" --job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks" --output test_output/test_results.json
    else
        echo "Python 3 not available. Trying Docker..."
        docker build -t persona-doc-intelligence .
        docker run -it --rm \
            -v "$(pwd)/test_input:/app/input" \
            -v "$(pwd)/test_output:/app/output" \
            persona-doc-intelligence \
            python main.py \
            --documents /app/input \
            --persona "PhD Researcher in Computational Biology" \
            --job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks" \
            --output /app/output/test_results.json
    fi
}

# Main execution logic
case "$1" in
    "local")
        run_local "$@"
        ;;
    "docker")
        run_docker
        ;;
    "test")
        run_test
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo ""
        show_usage
        exit 1
        ;;
esac

echo ""
echo "=== Execution completed ==="