import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class SemanticRetriever:
    """Semantic retrieval system for finding relevant test cases using RAG."""
    
    def __init__(self, k: int = 5):
        """
        Initialize the semantic retriever.
        
        Args:
            k: Number of top relevant test cases to retrieve
        """
        self.k = k
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.test_case_vectors = None
        self.test_cases = []
        self._is_fitted = False
    
    def fit(self, test_cases: List[Dict[str, Any]]) -> None:
        """
        Fit the retriever on a collection of test cases.
        
        Args:
            test_cases: List of test case dictionaries
        """
        self.test_cases = test_cases
        
        # Extract text content from test cases for vectorization
        texts = []
        for tc in test_cases:
            # Combine title, type, and steps into a single text
            text_parts = []
            
            if 'title' in tc:
                text_parts.append(tc['title'])
            
            if 'type' in tc:
                text_parts.append(tc['type'])
            
            if 'steps' in tc and isinstance(tc['steps'], list):
                for step in tc['steps']:
                    if isinstance(step, dict):
                        if 'step_text' in step:
                            text_parts.append(step['step_text'])
                        if 'step_expected' in step:
                            text_parts.append(step['step_expected'])
            
            if 'preconditions' in tc and tc['preconditions']:
                text_parts.append(tc['preconditions'])
            
            # Join all text parts
            combined_text = ' '.join(text_parts)
            texts.append(combined_text)
        
        # Fit the vectorizer and transform the texts
        self.test_case_vectors = self.vectorizer.fit_transform(texts)
        self._is_fitted = True
    
    def retrieve_relevant(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant test cases for a given query.
        
        Args:
            query: Search query (e.g., change request text)
            
        Returns:
            List of most relevant test cases with relevance scores
        """
        if not self._is_fitted:
            raise Exception("Retriever must be fitted before retrieving")
        
        # Vectorize the query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.test_case_vectors).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:self.k]
        
        # Return test cases with scores
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include cases with some similarity
                result = self.test_cases[idx].copy()
                result['_relevance_score'] = float(similarities[idx])
                results.append(result)
        
        return results
    
    def retrieve_by_keywords(self, keywords: List[str], test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retrieve test cases based on keyword matching.
        
        Args:
            keywords: List of keywords to search for
            test_cases: List of test cases to search in
            
        Returns:
            List of matching test cases with match counts
        """
        results = []
        
        for tc in test_cases:
            match_count = 0
            text_content = self._extract_text_content(tc)
            
            for keyword in keywords:
                if keyword.lower() in text_content.lower():
                    match_count += 1
            
            if match_count > 0:
                result = tc.copy()
                result['_match_count'] = match_count
                result['_match_ratio'] = match_count / len(keywords)
                results.append(result)
        
        # Sort by match count (descending)
        results.sort(key=lambda x: x['_match_count'], reverse=True)
        
        return results[:self.k]
    
    def _extract_text_content(self, test_case: Dict[str, Any]) -> str:
        """Extract all text content from a test case for keyword matching."""
        text_parts = []
        
        if 'title' in test_case:
            text_parts.append(test_case['title'])
        
        if 'type' in test_case:
            text_parts.append(test_case['type'])
        
        if 'preconditions' in test_case and test_case['preconditions']:
            text_parts.append(test_case['preconditions'])
        
        if 'steps' in test_case and isinstance(test_case['steps'], list):
            for step in test_case['steps']:
                if isinstance(step, dict):
                    if 'step_text' in step:
                        text_parts.append(step['step_text'])
                    if 'step_expected' in step:
                        text_parts.append(step['step_expected'])
        
        return ' '.join(text_parts)
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text for better matching.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction - can be enhanced with NLP libraries
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if',
            'then', 'than', 'so', 'such', 'some', 'any', 'all', 'each', 'every',
            'no', 'not', 'only', 'also', 'just', 'now', 'here', 'there', 'when',
            'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
        }
        
        # Filter out stop words and get unique words
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
