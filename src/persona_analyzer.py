"""
Persona Analyzer for extracting key characteristics and expertise areas
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class PersonaProfile:
    """Represents analyzed persona characteristics"""
    role: str
    expertise_areas: List[str]
    focus_keywords: Set[str]
    domain_knowledge: List[str]
    job_objectives: List[str]
    technical_level: str  # beginner, intermediate, advanced, expert


class PersonaAnalyzer:
    """Analyzes persona descriptions to extract relevant characteristics"""
    
    def __init__(self):
        # Domain keyword mappings
        self.domain_keywords = {
            'academic': ['research', 'study', 'literature', 'methodology', 'analysis', 'academic', 'scholar', 'phd', 'thesis', 'publication'],
            'business': ['revenue', 'profit', 'market', 'strategy', 'investment', 'analysis', 'financial', 'business', 'commercial', 'corporate'],
            'technical': ['algorithm', 'implementation', 'system', 'performance', 'optimization', 'technical', 'engineering', 'development'],
            'educational': ['learning', 'student', 'exam', 'study', 'concept', 'understanding', 'knowledge', 'curriculum', 'course'],
            'medical': ['clinical', 'patient', 'treatment', 'diagnosis', 'medical', 'health', 'therapy', 'disease'],
            'legal': ['law', 'legal', 'regulation', 'compliance', 'policy', 'contract', 'litigation'],
            'scientific': ['experiment', 'hypothesis', 'data', 'observation', 'scientific', 'laboratory', 'research']
        }
        
        # Role patterns
        self.role_patterns = {
            'researcher': ['researcher', 'scientist', 'phd', 'academic', 'scholar'],
            'student': ['student', 'undergraduate', 'graduate', 'learner'],
            'analyst': ['analyst', 'analyzes', 'analysis'],
            'manager': ['manager', 'director', 'executive', 'lead'],
            'developer': ['developer', 'engineer', 'programmer', 'architect'],
            'consultant': ['consultant', 'advisor', 'specialist'],
            'journalist': ['journalist', 'reporter', 'writer', 'editor']
        }
        
        # Technical level indicators
        self.technical_levels = {
            'beginner': ['beginner', 'new', 'learning', 'basic', 'introductory', 'freshman'],
            'intermediate': ['intermediate', 'moderate', 'some experience', 'undergraduate'],
            'advanced': ['advanced', 'experienced', 'senior', 'graduate'],
            'expert': ['expert', 'phd', 'professor', 'specialist', 'authority', 'master']
        }
    
    def analyze_persona(self, persona_description: str, job_description: str) -> PersonaProfile:
        """Analyze persona and job descriptions to create a profile"""
        combined_text = f"{persona_description} {job_description}".lower()
        
        # Extract role
        role = self._extract_role(persona_description)
        
        # Extract expertise areas
        expertise_areas = self._extract_expertise_areas(combined_text)
        
        # Extract focus keywords
        focus_keywords = self._extract_focus_keywords(combined_text)
        
        # Determine domain knowledge
        domain_knowledge = self._determine_domain_knowledge(combined_text)
        
        # Extract job objectives
        job_objectives = self._extract_job_objectives(job_description)
        
        # Determine technical level
        technical_level = self._determine_technical_level(persona_description)
        
        return PersonaProfile(
            role=role,
            expertise_areas=expertise_areas,
            focus_keywords=focus_keywords,
            domain_knowledge=domain_knowledge,
            job_objectives=job_objectives,
            technical_level=technical_level
        )
    
    def _extract_role(self, persona_description: str) -> str:
        """Extract the primary role from persona description"""
        text = persona_description.lower()
        
        for role, patterns in self.role_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return role
        
        # Extract first meaningful noun if no pattern matches
        words = re.findall(r'\b[a-z]+\b', text)
        for word in words:
            if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will']:
                return word
        
        return "professional"
    
    def _extract_expertise_areas(self, text: str) -> List[str]:
        """Extract areas of expertise from the text"""
        expertise = []
        
        # Look for specific subject areas
        subjects = re.findall(r'\b(?:in|of|for)\s+([a-z\s]+?)(?:\s+(?:and|or|,|\.|$))', text)
        for subject in subjects:
            subject = subject.strip()
            if len(subject) > 2 and len(subject.split()) <= 4:
                expertise.append(subject)
        
        # Look for domain-specific terms
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                expertise.append(domain)
        
        return list(set(expertise))[:5]  # Limit to top 5
    
    def _extract_focus_keywords(self, text: str) -> Set[str]:
        """Extract important keywords that indicate focus areas"""
        keywords = set()
        
        # Extract nouns and adjectives
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter for meaningful terms
        stop_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'will', 'can', 'are', 'was', 'were'}
        
        for word in words:
            if word not in stop_words and len(word) >= 3:
                keywords.add(word)
        
        # Add compound terms
        compounds = re.findall(r'\b([a-z]+\s+[a-z]+)\b', text)
        for compound in compounds:
            if len(compound.split()) == 2:
                keywords.add(compound)
        
        return keywords
    
    def _determine_domain_knowledge(self, text: str) -> List[str]:
        """Determine the relevant domain knowledge areas"""
        domains = []
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score >= 2:  # Threshold for domain relevance
                domains.append(domain)
        
        return domains
    
    def _extract_job_objectives(self, job_description: str) -> List[str]:
        """Extract specific objectives from job description"""
        objectives = []
        text = job_description.lower()
        
        # Look for action verbs and objectives
        action_patterns = [
            r'(analyze|review|summarize|identify|prepare|create|develop|assess|evaluate)',
            r'(find|extract|determine|compare|study|research|investigate)',
            r'(focus on|looking for|need to|should|must|want to)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            objectives.extend(matches)
        
        # Extract phrases after action verbs
        objective_phrases = re.findall(r'(?:analyze|review|summarize|identify|prepare|create|develop|assess|evaluate|find|extract|determine|compare|study|research|investigate)\s+([^.!?]+)', text)
        objectives.extend([phrase.strip() for phrase in objective_phrases])
        
        return list(set(objectives))[:5]  # Limit to top 5
    
    def _determine_technical_level(self, persona_description: str) -> str:
        """Determine the technical proficiency level"""
        text = persona_description.lower()
        
        # Check for explicit level indicators
        for level, indicators in self.technical_levels.items():
            for indicator in indicators:
                if indicator in text:
                    return level
        
        # Default based on role
        if any(role in text for role in ['phd', 'professor', 'expert', 'senior']):
            return 'expert'
        elif any(role in text for role in ['graduate', 'experienced']):
            return 'advanced'
        elif any(role in text for role in ['undergraduate', 'junior']):
            return 'intermediate'
        else:
            return 'intermediate'  # Default assumption