"""
Output Formatter for generating the required JSON output format (limited to top 5 sections everywhere)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .document_processor import Document
from .relevance_ranker import ScoredSection


class OutputFormatter:
    """Formats the analysis results into the required JSON output format"""

    def format_output(
        self,
        documents: List[Document],
        persona: str,
        job: str,
        ranked_sections: List[ScoredSection],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Format the output to exactly match the challenge specification:
        - Only metadata keys requested
        - Only document names (no paths/pages) in input_documents
        - Only requested fields in extracted_sections and subsection_analysis
        - Limit both sections to top 5 (by importance_rank)
        """

        # Base output structure
        output = {
            "metadata": {
                "input_documents": [doc.name for doc in documents],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }

        # Sort sections by importance rank
        output_sections = sorted(ranked_sections, key=lambda x: x.importance_rank)

        # Only keep top 5 for extracted_sections
        top_extracted_sections = output_sections[:5]
        for scored_section in top_extracted_sections:
            section = scored_section.section
            output["extracted_sections"].append({
                "document": section.document_name,
                "section_title": section.section_title,
                "importance_rank": scored_section.importance_rank,
                "page_number": section.page_number
            })

        # Only keep top 5 for subsection_analysis as well
        top_subsections = output_sections[:5]
        for scored_section in top_subsections:
            section = scored_section.section
            output["subsection_analysis"].append({
                "document": section.document_name,
                "refined_text": scored_section.refined_text,
                "page_number": section.page_number
            })

        return output

    def save_output(self, output_data: Dict[str, Any], output_path: str) -> None:
        """Save the formatted output to a JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    def validate_output_format(self, output_data: Dict[str, Any]) -> bool:
        """Validate the stripped-down output format"""
        # Required top-level keys
        required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_keys:
            if key not in output_data:
                return False

        # Metadata required keys
        metadata = output_data["metadata"]
        for key in ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]:
            if key not in metadata:
                return False

        # Validate extracted_sections list
        if not isinstance(output_data["extracted_sections"], list):
            return False
        if output_data["extracted_sections"]:
            first = output_data["extracted_sections"][0]
            for key in ["document", "section_title", "importance_rank", "page_number"]:
                if key not in first:
                    return False

        # Validate subsection_analysis list
        if not isinstance(output_data["subsection_analysis"], list):
            return False
        if output_data["subsection_analysis"]:
            first = output_data["subsection_analysis"][0]
            for key in ["document", "refined_text", "page_number"]:
                if key not in first:
                    return False

        return True
