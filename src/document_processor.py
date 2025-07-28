"""
Document Processor for PDF text extraction and section identification
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pdfplumber
from dataclasses import dataclass


@dataclass
class DocumentSection:
    """Represents a section extracted from a document"""
    document_name: str
    page_number: int
    section_title: str
    content: str
    start_position: int
    end_position: int


@dataclass
class Document:
    """Represents a processed document"""
    name: str
    path: str
    total_pages: int
    sections: List[DocumentSection]


class DocumentProcessor:
    """Handles PDF document processing and section extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Common section header patterns
        self.section_patterns = [
            r'^(\d+\.?\s+[A-Z][^.!?]*(?:[.!?]|$))',  # Numbered sections
            r'^([A-Z][A-Z\s]{2,}[^.!?]*(?:[.!?]|$))',  # ALL CAPS headers
            r'^(Abstract|Introduction|Methodology|Results|Discussion|Conclusion|References)',  # Common academic sections
            r'^(Executive Summary|Background|Analysis|Findings|Recommendations)',  # Business sections
            r'^(Chapter \d+|Section \d+|Part \d+)',  # Textbook sections
        ]
    
    def load_documents(self, documents_path: str) -> List[Document]:
        """Load all PDF documents from the specified directory"""
        documents = []
        doc_dir = Path(documents_path)
        
        if not doc_dir.exists():
            raise FileNotFoundError(f"Directory not found: {documents_path}")
        
        pdf_files = list(doc_dir.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in: {documents_path}")
        
        for pdf_file in pdf_files:
            try:
                doc = self._process_document(pdf_file)
                documents.append(doc)
                self.logger.info(f"Processed document: {pdf_file.name}")
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        return documents
    
    def _process_document(self, pdf_path: Path) -> Document:
        """Process a single PDF document"""
        sections = []
        
        full_text = ""
        page_texts = {}
        
        # Extract text from all pages using pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                page_texts[page_num] = text
                full_text += f"\n[PAGE {page_num + 1}]\n{text}"
        
        # Extract sections
        sections = self._extract_sections(full_text, page_texts, pdf_path.name)
        
        return Document(
            name=pdf_path.name,
            path=str(pdf_path),
            total_pages=len(page_texts),
            sections=sections
        )
    
    def _extract_sections(self, full_text: str, page_texts: Dict[int, str], doc_name: str) -> List[DocumentSection]:
        """Extract sections from document text"""
        sections = []
        lines = full_text.split('\n')
        
        current_section = None
        current_content = []
        current_page = 1
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for page markers
            page_match = re.match(r'\[PAGE (\d+)\]', line)
            if page_match:
                current_page = int(page_match.group(1))
                continue
            
            # Check if line is a section header
            is_header = self._is_section_header(line)
            
            if is_header and line:
                # Save previous section
                if current_section and current_content:
                    sections.append(DocumentSection(
                        document_name=doc_name,
                        page_number=current_section['page'],
                        section_title=current_section['title'],
                        content='\n'.join(current_content).strip(),
                        start_position=current_section['start'],
                        end_position=i
                    ))
                
                # Start new section
                current_section = {
                    'title': line,
                    'page': current_page,
                    'start': i
                }
                current_content = []
            elif line and current_section:
                current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections.append(DocumentSection(
                document_name=doc_name,
                page_number=current_section['page'],
                section_title=current_section['title'],
                content='\n'.join(current_content).strip(),
                start_position=current_section['start'],
                end_position=len(lines)
            ))
        
        # If no sections found, create page-based sections
        if not sections:
            sections = self._create_page_sections(page_texts, doc_name)
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is likely a section header"""
        if not line or len(line.strip()) < 3:
            return False
        
        # Check against patterns
        for pattern in self.section_patterns:
            if re.match(pattern, line.strip(), re.IGNORECASE):
                return True
        
        # Heuristic checks
        if (len(line) < 100 and  # Not too long
            line[0].isupper() and  # Starts with capital
            not line.endswith('.') and  # Doesn't end with period (usually)
            len(line.split()) < 15):  # Not too many words
            return True
        
        return False
    
    def _create_page_sections(self, page_texts: Dict[int, str], doc_name: str) -> List[DocumentSection]:
        """Create sections based on pages when no clear sections are found"""
        sections = []
        
        for page_num, text in page_texts.items():
            if text.strip():
                # Try to find a meaningful title from the first few lines
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                title = f"Page {page_num + 1}"
                
                if lines:
                    # Use first non-empty line as title if it's short enough
                    first_line = lines[0]
                    if len(first_line) < 80:
                        title = f"Page {page_num + 1}: {first_line[:50]}..."
                
                sections.append(DocumentSection(
                    document_name=doc_name,
                    page_number=page_num + 1,
                    section_title=title,
                    content=text.strip(),
                    start_position=0,
                    end_position=len(text)
                ))
        
        return sections
    
    def extract_sections(self, documents: List[Document]) -> List[DocumentSection]:
        """Extract all sections from all documents"""
        all_sections = []
        for doc in documents:
            all_sections.extend(doc.sections)
        return all_sections