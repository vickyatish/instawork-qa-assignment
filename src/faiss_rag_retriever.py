"""
FAISS RAG Retriever
A professional RAG implementation using Facebook's FAISS vector database.
"""

import os
import json
from typing import List, Dict, Any, Optional
from .faiss_vector_db import FAISSVectorDB
from .config import Config


class FAISSRAGRetriever:
    """FAISS-based RAG retriever for high-performance semantic search."""
    
    def __init__(self, k: int = 3, db_path: str = "faiss_db", dimension: int = 384):
        """
        Initialize the FAISS RAG retriever.
        
        Args:
            k: Number of top relevant test cases to retrieve
            db_path: Path to store the FAISS database
            dimension: Dimension of the embedding vectors
        """
        self.k = k
        self.vector_db = FAISSVectorDB(db_path, dimension)
        self.test_cases = []
        self._is_fitted = False
        
        print("✓ Using FAISS Vector Database for semantic retrieval")
    
    def fit(self, test_cases: List[Dict[str, Any]]) -> None:
        """
        Fit the retriever on a collection of test cases.
        
        Args:
            test_cases: List of test case dictionaries
        """
        self.test_cases = test_cases
        
        # Convert test cases to documents for vector database
        documents = []
        for i, tc in enumerate(test_cases):
            # Extract text content
            text_content = self._extract_text_content(tc)
            
            # Create document for vector database
            doc = {
                'text': text_content,
                'metadata': {
                    'file_name': tc.get('_file_name', f'tc_{i+1:03d}.json'),
                    'title': tc.get('title', ''),
                    'type': tc.get('type', ''),
                    'priority': tc.get('priority', ''),
                    'original_test_case': tc
                }
            }
            documents.append(doc)
        
        # Add to FAISS database
        self.vector_db.add_documents(documents)
        self._is_fitted = True
        
        print(f"✓ Fitted FAISS retriever with {len(test_cases)} test cases")
    
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
        
        # Search in FAISS database
        results = self.vector_db.search(query, top_k=self.k)
        
        # Convert back to test case format
        relevant_cases = []
        for result in results:
            test_case = result['metadata']['original_test_case'].copy()
            test_case['_relevance_score'] = result['similarity_score']
            test_case['_distance'] = result['distance']
            relevant_cases.append(test_case)
        
        return relevant_cases
    
    def _extract_text_content(self, test_case: Dict[str, Any]) -> str:
        """Extract all text content from a test case for vectorization."""
        text_parts = []
        
        if 'title' in test_case:
            text_parts.append(test_case['title'])
        
        if 'type' in test_case:
            text_parts.append(test_case['type'])
        
        if 'priority' in test_case:
            text_parts.append(test_case['priority'])
        
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
    
    def update_test_case(self, test_case_id: str, updated_test_case: Dict[str, Any]) -> bool:
        """
        Update a test case in the vector store.
        
        Args:
            test_case_id: ID of the test case to update
            updated_test_case: Updated test case data
            
        Returns:
            True if successful, False otherwise
        """
        # FAISS doesn't support direct updates, so we refit the entire collection
        print("Warning: FAISS doesn't support direct updates. Refitting entire collection...")
        self.fit(self.test_cases)
        return True
    
    def delete_test_case(self, test_case_id: str) -> bool:
        """
        Delete a test case from the vector store.
        
        Args:
            test_case_id: ID of the test case to delete
            
        Returns:
            True if successful, False otherwise
        """
        # FAISS doesn't support direct deletion, so we refit the entire collection
        print("Warning: FAISS doesn't support direct deletion. Refitting entire collection...")
        self.fit(self.test_cases)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the retriever.
        
        Returns:
            Dictionary with retriever statistics
        """
        stats = {
            'k': self.k,
            'is_fitted': self._is_fitted,
            'total_test_cases': len(self.test_cases),
            'retriever_type': 'FAISS'
        }
        
        # Add FAISS database stats
        db_stats = self.vector_db.get_stats()
        stats.update(db_stats)
        
        return stats
    
    def reset(self) -> bool:
        """
        Reset the retriever (clear all data).
        
        Returns:
            True if successful, False otherwise
        """
        self.vector_db.reset()
        self.test_cases = []
        self._is_fitted = False
        return True
    
    def search_by_keywords(self, keywords: List[str], test_cases: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for test cases using keyword matching.
        This uses the FAISS vector search with keyword-based query.
        
        Args:
            keywords: List of keywords to search for
            test_cases: List of test cases to search in (uses fitted data if None)
            
        Returns:
            List of matching test cases with match scores
        """
        if test_cases is None:
            test_cases = self.test_cases
        
        # Convert keywords to query string
        query = ' '.join(keywords)
        
        # Use the FAISS vector search
        return self.retrieve_relevant(query)
