import json
import time
import uuid
from openai import OpenAI
from typing import List, Dict, Any, Optional
from jsonschema import validate, ValidationError
from .config import Config
from .prompt_manager import PromptManager
from .observability import ObservabilityManager

class LLMClient:
    """Client for interacting with OpenAI's LLM API."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
        self.prompt_manager = PromptManager()
        self.observability = ObservabilityManager()
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def _make_llm_call(self, prompt: str, session_id: str = None) -> Dict[str, Any]:
        """
        Make an LLM API call with retry logic and observability.
        
        Args:
            prompt: The prompt to send to the LLM
            session_id: Optional session ID for tracking
            
        Returns:
            Parsed JSON response from the LLM
        """
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                # Calculate tokens and cost
                tokens_used = response.usage.total_tokens if response.usage else 0
                cost = self._calculate_cost(tokens_used)
                
                # Log the call
                if session_id:
                    self.observability.log_llm_call(session_id, self.model, tokens_used, cost)
                
                content = response.choices[0].message.content
                
                # Try to parse JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    if attempt < self.max_retries:
                        if session_id:
                            self.observability.log_retry_attempt(session_id, f"JSON parse error: {str(e)}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"Failed to parse JSON response after {self.max_retries} retries: {str(e)}")
                
            except Exception as e:
                if attempt < self.max_retries:
                    if session_id:
                        self.observability.log_retry_attempt(session_id, f"API error: {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f"LLM API call failed after {self.max_retries} retries: {str(e)}")
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate approximate cost based on token usage."""
        # Rough cost estimates for GPT-4 (as of 2024)
        if self.model.startswith("gpt-4"):
            return tokens * 0.00003  # $0.03 per 1K tokens
        elif self.model.startswith("gpt-3.5"):
            return tokens * 0.000002  # $0.002 per 1K tokens
        else:
            return 0.0
    
    def _validate_test_case_schema(self, test_case: Dict[str, Any], session_id: str = None) -> bool:
        """
        Validate a test case against the JSON schema.
        
        Args:
            test_case: The test case to validate
            session_id: Optional session ID for tracking
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Load schema
            with open(Config.SCHEMA_PATH, 'r') as f:
                schema = json.load(f)
            
            # Remove internal metadata fields before validation
            clean_test_case = {k: v for k, v in test_case.items() if not k.startswith('_')}
            
            # Validate against schema
            validate(instance=clean_test_case, schema=schema)
            return True
            
        except ValidationError as e:
            if session_id:
                self.observability.log_schema_validation_failure(session_id, str(e))
            return False
        except Exception as e:
            if session_id:
                self.observability.log_schema_validation_failure(session_id, f"Schema validation error: {str(e)}")
            return False
    
    def analyze_change_request(
        self, 
        change_request: str, 
        iw_overview: str, 
        existing_test_cases: List[Dict[str, Any]],
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyze a change request and determine which test cases are impacted.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            existing_test_cases: List of existing test cases
            session_id: Optional session ID for tracking
            
        Returns:
            Analysis result with impacted cases and required updates
        """
        # Use prompt template
        prompt = self.prompt_manager.load_prompt(
            "analyze_change_request",
            iw_overview=iw_overview,
            change_request=change_request,
            existing_test_cases=json.dumps(existing_test_cases, indent=2)
        )
        
        return self._make_llm_call(prompt, session_id)
    
    def generate_test_case(
        self, 
        change_request: str, 
        iw_overview: str, 
        test_case_type: str,
        title: str,
        priority: str,
        existing_test_cases: List[Dict[str, Any]],
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate a new test case based on the change request with schema validation and retry.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            test_case_type: Type of test case (positive, negative, edge)
            title: Test case title
            priority: Test case priority
            existing_test_cases: List of existing test cases for context
            session_id: Optional session ID for tracking
            
        Returns:
            Generated test case as a dictionary
        """
        # Use prompt template
        prompt = self.prompt_manager.load_prompt(
            "generate_test_case",
            iw_overview=iw_overview,
            change_request=change_request,
            test_case_type=test_case_type,
            title=title,
            priority=priority,
            existing_test_cases=json.dumps(existing_test_cases, indent=2)
        )
        
        # Generate with retry logic for schema validation
        for attempt in range(self.max_retries + 1):
            try:
                # Make LLM call
                test_case = self._make_llm_call(prompt, session_id)
                
                # Validate against schema
                if self._validate_test_case_schema(test_case, session_id):
                    return test_case
                else:
                    if attempt < self.max_retries:
                        if session_id:
                            self.observability.log_retry_attempt(session_id, "Schema validation failed")
                        # Add more specific instructions for retry
                        prompt += f"\n\nIMPORTANT: The previous response failed schema validation. Please ensure:\n"
                        prompt += f"- 'type' field is exactly one of: functional, integration, ui, api, performance, security, regression\n"
                        prompt += f"- 'priority' field is exactly one of: P1 - Critical, P2 - High, P3 - Medium, P4 - Low\n"
                        prompt += f"- All required fields are present and properly formatted\n"
                        prompt += f"- Steps array has at least 1 item with both 'step_text' and 'step_expected'\n"
                        continue
                    else:
                        raise Exception(f"Failed to generate valid test case after {self.max_retries} retries")
                        
            except Exception as e:
                if attempt < self.max_retries:
                    if session_id:
                        self.observability.log_retry_attempt(session_id, f"Generation error: {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Failed to generate test case after {self.max_retries} retries: {str(e)}")
    
    def update_existing_test_case(
        self, 
        change_request: str, 
        iw_overview: str, 
        original_test_case: Dict[str, Any],
        required_changes: List[str],
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing test case based on the change request with schema validation and retry.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            original_test_case: The original test case to update
            required_changes: List of changes needed
            session_id: Optional session ID for tracking
            
        Returns:
            Updated test case as a dictionary
        """
        # Use prompt template
        prompt = self.prompt_manager.load_prompt(
            "update_test_case",
            iw_overview=iw_overview,
            change_request=change_request,
            original_test_case=json.dumps(original_test_case, indent=2),
            required_changes=chr(10).join(f"- {change}" for change in required_changes)
        )
        
        # Update with retry logic for schema validation
        for attempt in range(self.max_retries + 1):
            try:
                # Make LLM call
                updated_test_case = self._make_llm_call(prompt, session_id)
                
                # Validate against schema
                if self._validate_test_case_schema(updated_test_case, session_id):
                    return updated_test_case
                else:
                    if attempt < self.max_retries:
                        if session_id:
                            self.observability.log_retry_attempt(session_id, "Schema validation failed")
                        # Add more specific instructions for retry
                        prompt += f"\n\nIMPORTANT: The previous response failed schema validation. Please ensure:\n"
                        prompt += f"- 'type' field is exactly one of: functional, integration, ui, api, performance, security, regression\n"
                        prompt += f"- 'priority' field is exactly one of: P1 - Critical, P2 - High, P3 - Medium, P4 - Low\n"
                        prompt += f"- All required fields are present and properly formatted\n"
                        prompt += f"- Steps array has at least 1 item with both 'step_text' and 'step_expected'\n"
                        continue
                    else:
                        raise Exception(f"Failed to generate valid updated test case after {self.max_retries} retries")
                        
            except Exception as e:
                if attempt < self.max_retries:
                    if session_id:
                        self.observability.log_retry_attempt(session_id, f"Update error: {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Failed to update test case after {self.max_retries} retries: {str(e)}")
