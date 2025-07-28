#!/usr/bin/env python3
"""
Persona-Driven Document Intelligence System
Main entry point for processing documents based on persona and job-to-be-done
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.document_processor import DocumentProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.relevance_ranker import RelevanceRanker
from src.output_formatter import OutputFormatter


def main():
    parser = argparse.ArgumentParser(description="Persona-Driven Document Intelligence")
    parser.add_argument("--documents", type=str, required=True, help="Path to directory containing PDF documents")
    parser.add_argument("--persona", type=str, required=True, help="Persona description")
    parser.add_argument("--job", type=str, required=True, help="Job-to-be-done description")
    parser.add_argument("--output", type=str, default="output.json", help="Output JSON file path")
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Initialize components
    doc_processor = DocumentProcessor()
    persona_analyzer = PersonaAnalyzer()
    relevance_ranker = RelevanceRanker()
    output_formatter = OutputFormatter()
    
    print(f"Processing documents from: {args.documents}")
    print(f"Persona: {args.persona}")
    print(f"Job: {args.job}")
    
    # Process documents
    documents = doc_processor.load_documents(args.documents)
    extracted_sections = doc_processor.extract_sections(documents)
    
    print(f"Extracted {len(extracted_sections)} sections from {len(documents)} documents")
    
    # Analyze persona and job
    persona_profile = persona_analyzer.analyze_persona(args.persona, args.job)
    
    # Rank sections by relevance
    ranked_sections = relevance_ranker.rank_sections(
        extracted_sections, 
        persona_profile, 
        args.job
    )
    
    # Format output
    output_data = output_formatter.format_output(
        documents=documents,
        persona=args.persona,
        job=args.job,
        ranked_sections=ranked_sections,
        processing_time=time.time() - start_time
    )
    
    # Save output
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Output saved to: {args.output}")


if __name__ == "__main__":
    main()