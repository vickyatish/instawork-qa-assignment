import time
import os
import uuid
from typing import List, Dict, Any, Optional
from .config import Config
from .llm_client import LLMClient
from .test_case_manager import TestCaseManager
from .report_generator import ReportGenerator
from .semantic_retriever import SemanticRetriever
from .observability import ObservabilityManager

class AITestCopilot:
    """Main AI Test Case Copilot that orchestrates the entire process."""
    
    def __init__(self):
        """Initialize the AI Test Copilot."""
        self.config = Config()
        self.config.validate()
        
        self.llm_client = LLMClient()
        self.test_case_manager = TestCaseManager()
        self.report_generator = ReportGenerator()
        self.semantic_retriever = SemanticRetriever(k=5)  # Top 5 relevant test cases
        self.observability = ObservabilityManager()
    
    def process_change_request(self, change_request_path: str) -> str:
        """
        Process a change request and generate updated/new test cases.
        
        Args:
            change_request_path: Path to the change request file
            
        Returns:
            Path to the generated report
        """
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        # Start observability session
        self.observability.start_session(session_id, change_request_path)
        
        start_time = time.time()
        execution_summary = {
            'status': 'success',
            'errors': [],
            'total_analyzed': 0,
            'total_updated': 0,
            'total_created': 0
        }
        
        try:
            # Step 1: Load the change request
            change_request = self._load_change_request(change_request_path)
            
            # Step 2: Load context and existing test cases
            iw_overview = self._load_iw_overview()
            all_test_cases = self.test_case_manager.load_all_test_cases()
            
            # Step 3: Use semantic retrieval to get relevant test cases
            self.semantic_retriever.fit(all_test_cases)
            relevant_test_cases = self.semantic_retriever.retrieve_relevant(change_request)
            execution_summary['total_analyzed'] = len(relevant_test_cases)
            
            # Step 4: Analyze the change request with relevant test cases only
            analysis_result = self.llm_client.analyze_change_request(
                change_request, iw_overview, relevant_test_cases, session_id
            )
            
            # Step 5: Process impacted test cases
            updated_test_cases = self._process_impacted_test_cases(
                change_request, iw_overview, analysis_result, all_test_cases, session_id
            )
            execution_summary['total_updated'] = len(updated_test_cases)
            
            # Step 6: Generate new test cases
            new_test_cases = self._generate_new_test_cases(
                change_request, iw_overview, analysis_result, relevant_test_cases, session_id
            )
            execution_summary['total_created'] = len(new_test_cases)
            
            # Step 7: Generate report
            execution_time = time.time() - start_time
            execution_summary['execution_time'] = f"{execution_time:.2f} seconds"
            
            report_path = self.report_generator.generate_report(
                change_request, analysis_result, updated_test_cases, new_test_cases, execution_summary
            )
            
            # End session successfully
            self.observability.end_session(
                session_id, 
                "success",
                test_cases_generated=len(new_test_cases),
                test_cases_updated=len(updated_test_cases)
            )
            
            return report_path
            
        except Exception as e:
            execution_summary['status'] = 'error'
            execution_summary['errors'].append(str(e))
            execution_summary['execution_time'] = f"{time.time() - start_time:.2f} seconds"
            
            # End session with error
            self.observability.end_session(session_id, "error")
            
            # Generate error report
            error_report = self.report_generator.generate_report(
                "Error occurred during processing", 
                {"summary": f"Error: {str(e)}"}, 
                [], [], execution_summary
            )
            
            raise Exception(f"Failed to process change request: {str(e)}. Error report generated at: {error_report}")
    
    def _load_change_request(self, change_request_path: str) -> str:
        """Load the change request from file."""
        try:
            with open(change_request_path, 'r') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load change request from {change_request_path}: {str(e)}")
    
    def _load_iw_overview(self) -> str:
        """Load the Instawork overview document."""
        try:
            with open(self.config.IW_OVERVIEW_PATH, 'r') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load IW_OVERVIEW.md: {str(e)}")
    
    def _process_impacted_test_cases(
        self,
        change_request: str,
        iw_overview: str,
        analysis_result: Dict[str, Any],
        existing_test_cases: List[Dict[str, Any]],
        session_id: str = None
    ) -> List[Dict[str, Any]]:
        """Process and update impacted test cases."""
        updated_test_cases = []
        
        if 'impacted_test_cases' not in analysis_result:
            return updated_test_cases
        
        for impacted in analysis_result['impacted_test_cases']:
            test_case_id = impacted.get('test_case_id')
            if not test_case_id:
                continue
            
            # Find the existing test case
            existing_test_case = None
            for tc in existing_test_cases:
                if tc.get('_file_name', '').startswith(test_case_id):
                    existing_test_case = tc
                    break
            
            if not existing_test_case:
                continue
            
            try:
                # Create backup before updating
                self.test_case_manager.backup_test_case(existing_test_case['_file_name'])
                
                # Update the test case using LLM
                updated_test_case = self.llm_client.update_existing_test_case(
                    change_request, iw_overview, existing_test_case, 
                    impacted.get('required_changes', []), session_id
                )
                
                # Save the updated test case
                updated_file_path = self.test_case_manager.update_test_case(
                    test_case_id, updated_test_case
                )
                
                # Add metadata for reporting
                updated_test_case['_file_path'] = updated_file_path
                updated_test_case['_file_name'] = os.path.basename(updated_file_path)
                updated_test_case['_original_file'] = existing_test_case['_file_name']
                updated_test_case['_impact_level'] = impacted.get('impact_level', 'unknown')
                updated_test_case['_reasoning'] = impacted.get('reasoning', 'No reasoning provided')
                
                updated_test_cases.append(updated_test_case)
                
            except Exception as e:
                print(f"Warning: Failed to update test case {test_case_id}: {str(e)}")
                continue
        
        return updated_test_cases
    
    def _generate_new_test_cases(
        self,
        change_request: str,
        iw_overview: str,
        analysis_result: Dict[str, Any],
        existing_test_cases: List[Dict[str, Any]],
        session_id: str = None
    ) -> List[Dict[str, Any]]:
        """Generate new test cases based on the analysis."""
        new_test_cases = []
        
        if 'new_test_cases_needed' not in analysis_result:
            return new_test_cases
        
        for new_case_spec in analysis_result['new_test_cases_needed']:
            try:
                test_case_type = new_case_spec.get('test_case_type', 'positive')
                title = new_case_spec.get('title', f'New {test_case_type} test case')
                priority = new_case_spec.get('priority', 'P3 - Medium')
                
                # Generate the test case using LLM
                new_test_case = self.llm_client.generate_test_case(
                    change_request, iw_overview, test_case_type, title, priority, existing_test_cases, session_id
                )
                
                # Save the new test case
                file_path = self.test_case_manager.create_new_test_case(new_test_case, test_case_type)
                
                # Add metadata for reporting
                new_test_case['_file_path'] = file_path
                new_test_case['_file_name'] = os.path.basename(file_path)
                new_test_case['_test_case_type'] = test_case_type
                new_test_case['_generated_for'] = title
                
                new_test_cases.append(new_test_case)
                
            except Exception as e:
                print(f"Warning: Failed to generate new test case: {str(e)}")
                continue
        
        return new_test_cases
    
    def validate_all_test_cases(self) -> Dict[str, Any]:
        """Validate all test cases against the schema."""
        validation_results = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': [],
            'errors': []
        }
        
        try:
            test_case_files = self.test_case_manager.list_test_cases()
            validation_results['total_files'] = len(test_case_files)
            
            for file_name in test_case_files:
                try:
                    test_case = self.test_case_manager.load_test_case(file_name)
                    if test_case:
                        self.test_case_manager.validate_test_case(test_case)
                        validation_results['valid_files'] += 1
                except Exception as e:
                    validation_results['invalid_files'].append(file_name)
                    validation_results['errors'].append(f"{file_name}: {str(e)}")
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"Validation process failed: {str(e)}")
            return validation_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the system."""
        try:
            test_case_files = self.test_case_manager.list_test_cases()
            iw_overview_exists = os.path.exists(self.config.IW_OVERVIEW_PATH)
            schema_exists = os.path.exists(self.config.SCHEMA_PATH)
            
            return {
                'status': 'ready' if self.config.OPENAI_API_KEY else 'missing_api_key',
                'test_cases_count': len(test_case_files),
                'iw_overview_exists': iw_overview_exists,
                'schema_exists': schema_exists,
                'openai_configured': bool(self.config.OPENAI_API_KEY),
                'reports_directory': self.config.REPORTS_DIR
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get observability metrics."""
        return self.observability.get_metrics_summary()
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent processing sessions."""
        return self.observability.get_recent_sessions(limit)
