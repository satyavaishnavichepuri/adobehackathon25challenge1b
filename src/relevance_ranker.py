"""
Relevance Ranker for scoring and ranking document sections based on persona and job
"""

import re
import math
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass

from .document_processor import DocumentSection
from .persona_analyzer import PersonaProfile


@dataclass
class ScoredSection:
    """Represents a document section with relevance scores"""
    section: DocumentSection
    relevance_score: float
    importance_rank: int
    score_breakdown: Dict[str, float]
    refined_text: str


class RelevanceRanker:
    """Ranks document sections based on relevance to persona and job"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
    
    def rank_sections(self, sections: List[DocumentSection], persona_profile: PersonaProfile, job_description: str) -> List[ScoredSection]:
        """Rank sections by relevance to persona and job"""
        
        # Calculate TF-IDF vectors for all sections
        tf_idf_vectors = self._calculate_tf_idf(sections)
        
        # Create query vector from persona and job
        query_vector = self._create_query_vector(persona_profile, job_description, tf_idf_vectors['vocabulary'])
        
        scored_sections = []
        
        for i, section in enumerate(sections):
            # Calculate multiple relevance scores
            scores = self._calculate_relevance_scores(
                section, 
                persona_profile, 
                job_description, 
                tf_idf_vectors['sections'][i],
                query_vector,
                tf_idf_vectors['vocabulary']
            )
            
            # Calculate overall relevance score
            relevance_score = self._combine_scores(scores)
            
            # Generate refined text
            refined_text = self._refine_section_text(section, persona_profile, job_description)
            
            scored_sections.append(ScoredSection(
                section=section,
                relevance_score=relevance_score,
                importance_rank=0,  # Will be set after sorting
                score_breakdown=scores,
                refined_text=refined_text
            ))
        
        # Sort by relevance score and assign ranks
        scored_sections.sort(key=lambda x: x.relevance_score, reverse=True)
        for i, scored_section in enumerate(scored_sections):
            scored_section.importance_rank = i + 1
        
        return scored_sections
    
    def _calculate_tf_idf(self, sections: List[DocumentSection]) -> Dict:
        """Calculate TF-IDF vectors for all sections"""
        # Tokenize all sections
        section_tokens = []
        vocabulary = set()
        
        for section in sections:
            tokens = self._tokenize(section.content)
            section_tokens.append(tokens)
            vocabulary.update(tokens)
        
        vocabulary = sorted(list(vocabulary))
        vocab_index = {word: i for i, word in enumerate(vocabulary)}
        
        # Calculate TF for each section
        tf_vectors = []
        for tokens in section_tokens:
            token_count = Counter(tokens)
            total_tokens = len(tokens)
            tf_vector = [0] * len(vocabulary)
            
            for word, count in token_count.items():
                if word in vocab_index:
                    tf_vector[vocab_index[word]] = count / total_tokens
            
            tf_vectors.append(tf_vector)
        
        # Calculate IDF
        doc_count = len(sections)
        idf_vector = [0] * len(vocabulary)
        
        for i, word in enumerate(vocabulary):
            doc_freq = sum(1 for tokens in section_tokens if word in tokens)
            idf_vector[i] = math.log(doc_count / (doc_freq + 1))
        
        # Calculate TF-IDF
        tf_idf_vectors = []
        for tf_vector in tf_vectors:
            tf_idf_vector = [tf * idf for tf, idf in zip(tf_vector, idf_vector)]
            tf_idf_vectors.append(tf_idf_vector)
        
        return {
            'sections': tf_idf_vectors,
            'vocabulary': vocabulary,
            'vocab_index': vocab_index,
            'idf': idf_vector
        }
    
    def _create_query_vector(self, persona_profile: PersonaProfile, job_description: str, vocabulary: List[str]) -> List[float]:
        """Create query vector from persona and job description"""
        # Combine all persona information
        query_text = f"{persona_profile.role} {job_description}"
        if persona_profile.expertise_areas:
            query_text += " " + " ".join(persona_profile.expertise_areas)
        if persona_profile.domain_knowledge:
            query_text += " " + " ".join(persona_profile.domain_knowledge)
        if persona_profile.job_objectives:
            query_text += " " + " ".join(persona_profile.job_objectives)
        if persona_profile.focus_keywords:
            query_text += " " + " ".join(persona_profile.focus_keywords)
        
        query_tokens = self._tokenize(query_text)
        token_count = Counter(query_tokens)
        total_tokens = len(query_tokens)
        
        query_vector = [0] * len(vocabulary)
        for i, word in enumerate(vocabulary):
            if word in token_count:
                query_vector[i] = token_count[word] / total_tokens
        
        return query_vector
    
    def _calculate_relevance_scores(self, section: DocumentSection, persona_profile: PersonaProfile, 
                                  job_description: str, section_tf_idf: List[float], 
                                  query_vector: List[float], vocabulary: List[str]) -> Dict[str, float]:
        """Calculate multiple relevance scores for a section"""
        scores = {}
        
        # 1. Cosine similarity with query
        scores['cosine_similarity'] = self._cosine_similarity(section_tf_idf, query_vector)
        
        # 2. Keyword match score
        scores['keyword_match'] = self._keyword_match_score(section, persona_profile, job_description)
        
        # 3. Domain relevance score
        scores['domain_relevance'] = self._domain_relevance_score(section, persona_profile)
        
        # 4. Section importance score (based on title and position)
        scores['section_importance'] = self._section_importance_score(section)
        
        # 5. Technical level alignment
        scores['technical_alignment'] = self._technical_alignment_score(section, persona_profile)
        
        # 6. Job objective alignment
        scores['job_alignment'] = self._job_objective_alignment(section, persona_profile)
        
        return scores
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _keyword_match_score(self, section: DocumentSection, persona_profile: PersonaProfile, job_description: str) -> float:
        """Calculate score based on keyword matches"""
        section_text = (section.section_title + " " + section.content).lower()
        
        # Keywords from persona
        persona_keywords = set()
        persona_keywords.update(persona_profile.focus_keywords)
        if persona_profile.expertise_areas:
            for area in persona_profile.expertise_areas:
                persona_keywords.update(area.lower().split())
        
        # Keywords from job description
        job_keywords = set(self._tokenize(job_description.lower()))
        
        all_keywords = persona_keywords.union(job_keywords)
        
        matches = 0
        for keyword in all_keywords:
            if keyword in section_text:
                matches += 1
        
        return matches / max(len(all_keywords), 1)
    
    def _domain_relevance_score(self, section: DocumentSection, persona_profile: PersonaProfile) -> float:
        """Calculate domain relevance score"""
        if not persona_profile.domain_knowledge:
            return 0.5  # Neutral score
        
        section_text = (section.section_title + " " + section.content).lower()
        
        domain_indicators = {
            'academic': ['research', 'study', 'analysis', 'methodology', 'literature', 'findings', 'conclusion'],
            'business': ['revenue', 'profit', 'market', 'strategy', 'financial', 'investment', 'business'],
            'technical': ['algorithm', 'implementation', 'system', 'performance', 'technical', 'method'],
            'educational': ['learning', 'concept', 'understanding', 'knowledge', 'study', 'example'],
            'medical': ['clinical', 'patient', 'treatment', 'medical', 'health', 'therapy'],
            'legal': ['law', 'legal', 'regulation', 'policy', 'compliance'],
            'scientific': ['experiment', 'hypothesis', 'data', 'observation', 'scientific']
        }
        
        score = 0
        for domain in persona_profile.domain_knowledge:
            if domain in domain_indicators:
                indicators = domain_indicators[domain]
                matches = sum(1 for indicator in indicators if indicator in section_text)
                score += matches / len(indicators)
        
        return min(score / len(persona_profile.domain_knowledge), 1.0)
    
    def _section_importance_score(self, section: DocumentSection) -> float:
        """Calculate importance based on section characteristics"""
        title = section.section_title.lower()
        
        # Important section indicators
        important_sections = [
            'abstract', 'summary', 'introduction', 'conclusion', 'results', 'findings',
            'methodology', 'analysis', 'discussion', 'executive summary', 'overview'
        ]
        
        score = 0.5  # Base score
        
        # Check for important section keywords
        for important in important_sections:
            if important in title:
                score += 0.3
                break
        
        # Prefer earlier sections (introduction, etc.)
        if section.page_number <= 3:
            score += 0.1
        
        # Penalize very short sections
        if len(section.content) < 100:
            score -= 0.2
        
        # Bonus for substantial content
        if len(section.content) > 1000:
            score += 0.1
        
        return max(min(score, 1.0), 0.0)
    
    def _technical_alignment_score(self, section: DocumentSection, persona_profile: PersonaProfile) -> float:
        """Calculate alignment with technical level"""
        section_text = (section.section_title + " " + section.content).lower()
        
        technical_indicators = {
            'beginner': ['basic', 'introduction', 'overview', 'fundamentals', 'simple'],
            'intermediate': ['analysis', 'application', 'implementation', 'practical'],
            'advanced': ['complex', 'sophisticated', 'advanced', 'detailed', 'comprehensive'],
            'expert': ['novel', 'innovative', 'cutting-edge', 'state-of-the-art', 'breakthrough']
        }
        
        target_level = persona_profile.technical_level
        if target_level not in technical_indicators:
            return 0.5
        
        indicators = technical_indicators[target_level]
        matches = sum(1 for indicator in indicators if indicator in section_text)
        
        return min(matches / len(indicators), 1.0)
    
    def _job_objective_alignment(self, section: DocumentSection, persona_profile: PersonaProfile) -> float:
        """Calculate alignment with job objectives"""
        if not persona_profile.job_objectives:
            return 0.5
        
        section_text = (section.section_title + " " + section.content).lower()
        
        alignment_score = 0
        for objective in persona_profile.job_objectives:
            objective_words = self._tokenize(objective.lower())
            matches = sum(1 for word in objective_words if word in section_text)
            if objective_words:
                alignment_score += matches / len(objective_words)
        
        return min(alignment_score / len(persona_profile.job_objectives), 1.0)
    
    def _combine_scores(self, scores: Dict[str, float]) -> float:
        """Combine individual scores into overall relevance score"""
        # Weight different score components
        weights = {
            'cosine_similarity': 0.25,
            'keyword_match': 0.25,
            'domain_relevance': 0.20,
            'section_importance': 0.10,
            'technical_alignment': 0.10,
            'job_alignment': 0.10
        }
        
        total_score = 0
        for score_type, score_value in scores.items():
            if score_type in weights:
                total_score += weights[score_type] * score_value
        
        return total_score
    
    def _refine_section_text(self, section: DocumentSection, persona_profile: PersonaProfile, job_description: str) -> str:
        """Create refined text focused on persona needs"""
        content = section.content
        
        # Extract most relevant sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Score sentences based on keyword presence
        persona_keywords = set()
        persona_keywords.update(persona_profile.focus_keywords)
        job_keywords = set(self._tokenize(job_description.lower()))
        all_keywords = persona_keywords.union(job_keywords)
        
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Ignore very short sentences
                score = sum(1 for keyword in all_keywords if keyword.lower() in sentence.lower())
                scored_sentences.append((score, sentence))
        
        # Take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [sentence for score, sentence in scored_sentences[:5]]
        
        refined_text = '. '.join(top_sentences)
        
        # Ensure reasonable length
        if len(refined_text) > 1000:
            refined_text = refined_text[:1000] + "..."
        elif len(refined_text) < 100:
            refined_text = content[:500] + "..." if len(content) > 500 else content
        
        return refined_text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words, removing stop words and short words"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter stop words and short words
        filtered_words = [word for word in words 
                         if word not in self.stop_words and len(word) >= 3]
        
        return filtered_words