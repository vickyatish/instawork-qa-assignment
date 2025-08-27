import json
from openai import OpenAI
from typing import List, Dict, Any, Optional
from .config import Config

class LLMClient:
    """Client for interacting with OpenAI's LLM API."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
    
    def analyze_change_request(
        self, 
        change_request: str, 
        iw_overview: str, 
        existing_test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a change request and determine which test cases are impacted.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            existing_test_cases: List of existing test cases
            
        Returns:
            Analysis result with impacted cases and required updates
        """
        prompt = f"""
You are an expert QA engineer analyzing a change request for Instawork's platform. 

CONTEXT:
{iw_overview}

CHANGE REQUEST:
{change_request}

EXISTING TEST CASES:
{json.dumps(existing_test_cases, indent=2)}

TASK:
Analyze the change request and determine:
1. Which existing test cases (if any) are impacted by this change
2. What specific updates are needed for each impacted test case
3. Whether new test cases need to be created

For each impacted test case, provide:
- test_case_id: The ID of the test case (e.g., "tc_001")
- impact_level: "high", "medium", or "low"
- required_changes: List of specific changes needed
- reasoning: Why this test case is impacted

For new test cases needed, specify:
- test_case_type: "positive", "negative", or "edge"
- title: Suggested title
- priority: "P1 - Critical", "P2 - High", "P3 - Medium", or "P4 - Low"

RESPONSE FORMAT:
Return a JSON object with this structure:
{{
    "impacted_test_cases": [
        {{
            "test_case_id": "tc_001",
            "impact_level": "high",
            "required_changes": ["Update step 3", "Add new step"],
            "reasoning": "This test case covers the feature being modified"
        }}
    ],
    "new_test_cases_needed": [
        {{
            "test_case_type": "positive",
            "title": "Suggested title",
            "priority": "P2 - High"
        }}
    ],
    "summary": "Brief summary of the analysis"
}}

Analyze carefully and provide specific, actionable recommendations.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            raise Exception(f"Failed to analyze change request: {str(e)}")
    
    def generate_test_case(
        self, 
        change_request: str, 
        iw_overview: str, 
        test_case_type: str,
        title: str,
        priority: str,
        existing_test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a new test case based on the change request.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            test_case_type: Type of test case (positive, negative, edge)
            title: Test case title
            priority: Test case priority
            existing_test_cases: List of existing test cases for context
            
        Returns:
            Generated test case as a dictionary
        """
        prompt = f"""
You are an expert QA engineer creating a new test case for Instawork's platform.

CONTEXT:
{iw_overview}

CHANGE REQUEST:
{change_request}

TEST CASE REQUIREMENTS:
- Type: {test_case_type}
- Title: {title}
- Priority: {priority}

EXISTING TEST CASES (for reference and consistency):
{json.dumps(existing_test_cases, indent=2)}

TASK:
Create a comprehensive test case that follows the existing pattern and covers the new functionality.

REQUIREMENTS:
1. Follow the exact JSON schema structure
2. Make steps realistic and specific to Instawork's platform
3. Ensure the test case is executable and verifiable
4. Use consistent terminology with existing test cases
5. For {test_case_type} test cases:
   - Positive: Test the happy path and expected behavior
   - Negative: Test error conditions and edge cases
   - Edge: Test boundary conditions and unusual scenarios

RESPONSE FORMAT:
Return a valid JSON object that conforms to the test case schema:
{{
    "title": "Test case title",
    "type": "functional",
    "priority": "P2 - High",
    "preconditions": "Setup requirements",
    "steps": [
        {{
            "step_text": "Action to perform",
            "step_expected": "Expected outcome"
        }}
    ]
}}

Create a high-quality, realistic test case that a QA engineer can execute.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            raise Exception(f"Failed to generate test case: {str(e)}")
    
    def update_existing_test_case(
        self, 
        change_request: str, 
        iw_overview: str, 
        original_test_case: Dict[str, Any],
        required_changes: List[str]
    ) -> Dict[str, Any]:
        """
        Update an existing test case based on the change request.
        
        Args:
            change_request: The change request text
            iw_overview: Instawork overview context
            original_test_case: The original test case to update
            required_changes: List of changes needed
            
        Returns:
            Updated test case as a dictionary
        """
        prompt = f"""
You are an expert QA engineer updating an existing test case for Instawork's platform.

CONTEXT:
{iw_overview}

CHANGE REQUEST:
{change_request}

ORIGINAL TEST CASE:
{json.dumps(original_test_case, indent=2)}

REQUIRED CHANGES:
{chr(10).join(f"- {change}" for change in required_changes)}

TASK:
Update the test case to address the required changes while:
1. Maintaining the existing structure and quality
2. Ensuring all changes are properly integrated
3. Keeping the test case executable and verifiable
4. Preserving the original intent where possible

RESPONSE FORMAT:
Return the updated test case as a valid JSON object that conforms to the schema.
Only modify what's necessary to address the required changes.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            raise Exception(f"Failed to update test case: {str(e)}")
