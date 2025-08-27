import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the AI Test Case Copilot."""
    
    # OpenAI API settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # File paths
    IW_OVERVIEW_PATH = "IW_OVERVIEW.md"
    TEST_CASES_DIR = "test_cases"
    SCHEMA_PATH = "schema/test_case.schema.json"
    REPORTS_DIR = "reports"
    
    # LLM settings
    MAX_TOKENS = 4000
    TEMPERATURE = 0.1
    
    # Test case generation settings
    MIN_NEW_TEST_CASES = 3  # positive, negative, edge
    MAX_EXISTING_CASES_TO_UPDATE = 10
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not os.path.exists(cls.IW_OVERVIEW_PATH):
            raise ValueError(f"IW_OVERVIEW.md not found at {cls.IW_OVERVIEW_PATH}")
        
        if not os.path.exists(cls.SCHEMA_PATH):
            raise ValueError(f"Schema file not found at {cls.SCHEMA_PATH}")
        
        if not os.path.exists(cls.TEST_CASES_DIR):
            raise ValueError(f"Test cases directory not found at {cls.TEST_CASES_DIR}")
        
        # Create reports directory if it doesn't exist
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
