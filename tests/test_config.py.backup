import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.config import Config

class TestConfig:
    """Test cases for the Config class."""
    
    def test_config_initialization(self):
        """Test that Config can be initialized."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            config = Config()
            assert config is not None
    
    def test_openai_api_key_from_env(self):
        """Test that OpenAI API key is loaded from environment."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}, clear=True):
                config = Config()
                assert config.OPENAI_API_KEY is not None
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            config = Config()
            assert config.OPENAI_MODEL == 'gpt-4'
            assert config.MAX_TOKENS == 4000
            assert config.TEMPERATURE == 0.1
            assert config.MIN_NEW_TEST_CASES == 3
    
    def test_custom_model_from_env(self):
        """Test that custom model exists."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-3.5-turbo'}, clear=True):
                config = Config()
                assert config.OPENAI_MODEL is not None
    
    def test_validate_missing_files(self):
        """Test that validation fails with missing required files."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Create a temporary config with non-existent paths
                    with patch.object(Config, 'IW_OVERVIEW_PATH', os.path.join(temp_dir, 'nonexistent.md')):
                        with patch.object(Config, 'SCHEMA_PATH', os.path.join(temp_dir, 'nonexistent.json')):
                            with patch.object(Config, 'TEST_CASES_DIR', os.path.join(temp_dir, 'nonexistent')):
                                config = Config()
                                with pytest.raises(ValueError):
                                    config.validate()
    
    def test_validate_success(self):
        """Test that validation succeeds with all required files."""
        with patch('src.config.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}, clear=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Create required files
                    iw_overview_path = os.path.join(temp_dir, 'IW_OVERVIEW.md')
                    schema_path = os.path.join(temp_dir, 'schema.json')
                    test_cases_dir = os.path.join(temp_dir, 'test_cases')
                    
                    os.makedirs(test_cases_dir)
                    
                    with open(iw_overview_path, 'w') as f:
                        f.write('# Test Overview')
                    
                    with open(schema_path, 'w') as f:
                        f.write('{"type": "object"}')
                    
                    # Patch config paths
                    with patch.object(Config, 'IW_OVERVIEW_PATH', iw_overview_path):
                        with patch.object(Config, 'TEST_CASES_DIR', test_cases_dir):
                            with patch.object(Config, 'SCHEMA_PATH', schema_path):
                                config = Config()
                                # Should not raise an exception
                                config.validate()
                                
                                # Check that reports directory was created
                                assert os.path.exists(config.REPORTS_DIR)
