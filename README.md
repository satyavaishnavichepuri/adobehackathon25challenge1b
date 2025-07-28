# Persona-Driven Document Intelligence System - CHALLENGE 1B

A lightweight, CPU-only document intelligence system that extracts and prioritizes relevant sections from PDF documents based on specific personas and their job-to-be-done requirements.

##  Overview

This system addresses the **Round 1B: Persona-Driven Document Intelligence** challenge by implementing a sophisticated yet lightweight document analysis engine. It processes 3-10 PDF documents and ranks their sections based on relevance to a specific persona profile and job objectives.

##  Features

- **Multi-Domain Support**: Handles academic papers, business reports, educational content, and more
- **Persona-Aware Analysis**: Adapts to different roles (researcher, student, analyst, etc.)
- **Intelligent Section Extraction**: Automatically identifies document structure and key sections
- **Relevance Ranking**: Uses TF-IDF and multi-factor scoring for accurate relevance assessment
- **Content Refinement**: Generates persona-focused summaries of top sections
- **Fast Processing**: Processes 3-5 documents in under 60 seconds
- **Resource Efficient**: CPU-only, < 1GB model size, no internet required

##  Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Document        │    │ Persona         │    │ Relevance       │    │ Output          │
│ Processor       ├───►│ Analyzer        ├───►│ Ranker          ├───►│ Formatter       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
       │                         │                         │                         │
   PDF Text                 Persona                  TF-IDF                     JSON
   Extraction               Profile               Scoring                    Output
```

### Core Components

1. **Document Processor** (`src/document_processor.py`)
   - PDF text extraction using PyMuPDF
   - Intelligent section identification
   - Fallback to page-based sections

2. **Persona Analyzer** (`src/persona_analyzer.py`)
   - Role and expertise extraction
   - Domain knowledge mapping
   - Technical level assessment

3. **Relevance Ranker** (`src/relevance_ranker.py`)
   - TF-IDF vectorization
   - Multi-factor relevance scoring
   - Content refinement

4. **Output Formatter** (`src/output_formatter.py`)
   - JSON output generation
   - Insight extraction
   - Quality metrics

##  Quick Start

### Prerequisites

- Python 3.9+ OR Docker
- PDF documents to analyze

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker
./run.sh docker

# Or manually:
docker build -t persona-doc-intelligence .
docker run -it --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  persona-doc-intelligence \
  python main.py \
  --documents /app/input \
  --persona "Your persona description" \
  --job "Your job-to-be-done" \
  --output /app/output/results.json
```

### Option 2: Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python main.py \
  --documents ./documents \
  --persona "PhD Researcher in Computational Biology" \
  --job "Prepare a comprehensive literature review focusing on methodologies" \
  --output results.json
```

### Option 3: Using the Run Script

```bash
# Show help
./run.sh help

# Run locally
./run.sh local --documents ./docs --persona "Student" --job "Study for exam"

# Run with Docker
./run.sh docker

# Run test case
./run.sh test
```

##  Sample Test Cases

### Test Case 1: Academic Research
```bash
python main.py \
  --documents ./research_papers \
  --persona "PhD Researcher in Computational Biology" \
  --job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks" \
  --output academic_results.json
```

### Test Case 2: Business Analysis
```bash
python main.py \
  --documents ./annual_reports \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends, R&D investments, and market positioning strategies" \
  --output business_results.json
```

### Test Case 3: Educational Content
```bash
python main.py \
  --documents ./textbook_chapters \
  --persona "Undergraduate Chemistry Student" \
  --job "Identify key concepts and mechanisms for exam preparation on reaction kinetics" \
  --output education_results.json
```

##  Output Format

The system generates a comprehensive JSON output with:

- **Metadata**: Document information, persona, job description, processing stats
- **Extracted Sections**: All sections ranked by relevance with detailed scores
- **Sub-section Analysis**: Refined content for top sections with insights
- **Summary**: Processing statistics and key metrics



## Command Line Options

```
python main.py [OPTIONS]

Options:
  --documents PATH     Directory containing PDF documents (required)
  --persona TEXT       Persona description (required)
  --job TEXT          Job-to-be-done description (required)
  --output PATH       Output JSON file path (default: output.json)
  --help              Show help message
```

## Performance Characteristics

- **Processing Speed**: < 60 seconds for 3-5 documents
- **Memory Usage**: < 512MB RAM
- **Model Size**: < 50MB (using lightweight TF-IDF)
- **CPU Only**: No GPU requirements
- **Offline Capable**: No internet connection needed

## Constraints Compliance

**CPU Only**: Pure Python implementation, no GPU dependencies  
**Model Size ≤ 1GB**: Uses rule-based methods and lightweight TF-IDF  
**Processing Time ≤ 60s**: Optimized for fast execution  
**No Internet**: Fully offline operation  
**Generic Solution**: Handles diverse domains and personas  

## Development

### Project Structure
```
├── src/
│   ├── document_processor.py    # PDF processing and section extraction
│   ├── persona_analyzer.py      # Persona profile analysis
│   ├── relevance_ranker.py      # TF-IDF and relevance scoring
│   └── output_formatter.py      # JSON output generation
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container definition
├── run.sh                       # Execution script
├── approach_explanation.md      # Technical methodology
└── output.json     # Sample output format
```

### Dependencies

- **pdfplumber** (0.10.3): PDF text extraction
- **NumPy** (1.24.3): Numerical operations

## Methodology

The system employs a multi-stage approach:

1. **Document Processing**: Extract and structure content from PDFs
2. **Persona Analysis**: Build profile from persona description and job requirements
3. **Relevance Scoring**: Combine TF-IDF similarity with domain-specific scoring
4. **Content Refinement**: Generate focused summaries for top sections
5. **Output Generation**: Format results according to specification

For detailed methodology, see [`approach_explanation.md`](approach_explanation.md). 

## Contributing

This system was built for the Adobe Hackathon 2025 challenge. The architecture is designed to be modular and extensible for future enhancements.

## License

Built for Adobe Hackathon 2025 - Round 1B: Persona-Driven Document Intelligence Challenge.
