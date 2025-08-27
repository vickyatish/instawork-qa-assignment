import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.test_case_manager import TestCaseManager

class TestTestCaseManager:
    """Test cases for the TestCaseManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_cases_dir = os.path.join(self.temp_dir, 'test_cases')
        self.schema_dir = os.path.join(self.temp_dir, 'schema')
        
        os.makedirs(self.test_cases_dir)
        os.makedirs(self.schema_dir)
        
        # Create a simple test schema
        self.schema = {
            "type": "object",
            "required": ["title", "type", "priority", "steps"],
            "properties": {
                "title": {"type": "string"},
                "type": {"type": "string"},
                "priority": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["step_text", "step_expected"],
                        "properties": {
                            "step_text": {"type": "string"},
                            "step_expected": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        self.schema_path = os.path.join(self.schema_dir, 'test_case.schema.json')
        with open(self.schema_path, 'w') as f:
            json.dump(self.schema, f)
        
        # Create sample test cases
        self.sample_test_case = {
            "title": "Test Case 1",
            "type": "functional",
            "priority": "P2 - High",
            "steps": [
                {
                    "step_text": "Step 1",
                    "step_expected": "Expected 1"
                }
            ]
        }
        
        self.test_case_path = os.path.join(self.test_cases_dir, 'tc_001.json')
        with open(self.test_case_path, 'w') as f:
            json.dump(self.sample_test_case, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.test_case_manager.Config')
    def test_initialization(self, mock_config):
        """Test that TestCaseManager initializes correctly."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        assert manager.test_cases_dir == self.test_cases_dir
        assert manager.schema_path == self.schema_path
        assert manager.schema == self.schema
    
    @patch('src.test_case_manager.Config')
    def test_load_all_test_cases(self, mock_config):
        """Test loading all test cases."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        test_cases = manager.load_all_test_cases()
        
        assert len(test_cases) == 1
        assert test_cases[0]['title'] == 'Test Case 1'
        assert test_cases[0]['_file_name'] == 'tc_001.json'
        assert test_cases[0]['_file_path'] == self.test_case_path
    
    @patch('src.test_case_manager.Config')
    def test_load_test_case(self, mock_config):
        """Test loading a specific test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        test_case = manager.load_test_case('tc_001.json')
        
        assert test_case is not None
        assert test_case['title'] == 'Test Case 1'
        assert test_case['_file_name'] == 'tc_001.json'
    
    @patch('src.test_case_manager.Config')
    def test_load_nonexistent_test_case(self, mock_config):
        """Test loading a non-existent test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        test_case = manager.load_test_case('nonexistent.json')
        
        assert test_case is None
    
    @patch('src.test_case_manager.Config')
    def test_validate_test_case(self, mock_config):
        """Test test case validation."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        # Valid test case should pass validation
        assert manager.validate_test_case(self.sample_test_case) is True
        
        # Invalid test case should fail validation
        invalid_test_case = {"title": "Invalid"}  # Missing required fields
        with pytest.raises(Exception):
            manager.validate_test_case(invalid_test_case)
    
    @patch('src.test_case_manager.Config')
    def test_save_test_case(self, mock_config):
        """Test saving a test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        new_test_case = {
            "title": "New Test Case",
            "type": "functional",
            "priority": "P3 - Medium",
            "steps": [
                {
                    "step_text": "New Step",
                    "step_expected": "New Expected"
                }
            ]
        }
        
        file_path = manager.save_test_case(new_test_case, 'tc_002.json')
        assert os.path.exists(file_path)
        
        # Verify the saved content
        with open(file_path, 'r') as f:
            saved_content = json.load(f)
        
        assert saved_content['title'] == 'New Test Case'
        assert '_file_path' not in saved_content  # Internal fields should be removed
    
    @patch('src.test_case_manager.Config')
    def test_update_test_case(self, mock_config):
        """Test updating an existing test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        updated_test_case = {
            "title": "Updated Test Case",
            "type": "functional",
            "priority": "P1 - Critical",
            "steps": [
                {
                    "step_text": "Updated Step",
                    "step_expected": "Updated Expected"
                }
            ]
        }
        
        file_path = manager.update_test_case('tc_001', updated_test_case)
        assert os.path.exists(file_path)
        
        # Verify the updated content
        with open(file_path, 'r') as f:
            saved_content = json.load(f)
        
        assert saved_content['title'] == 'Updated Test Case'
        assert saved_content['priority'] == 'P1 - Critical'
    
    @patch('src.test_case_manager.Config')
    def test_update_nonexistent_test_case(self, mock_config):
        """Test updating a non-existent test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        with pytest.raises(FileNotFoundError):
            manager.update_test_case('nonexistent', {})
    
    @patch('src.test_case_manager.Config')
    def test_create_new_test_case(self, mock_config):
        """Test creating a new test case with auto-generated filename."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        new_test_case = {
            "title": "Auto-generated Test Case",
            "type": "functional",
            "priority": "P3 - Medium",
            "steps": [
                {
                    "step_text": "Auto Step",
                    "step_expected": "Auto Expected"
                }
            ]
        }
        
        file_path = manager.create_new_test_case(new_test_case, 'positive')
        assert os.path.exists(file_path)
        
        # Should create tc_002.json since tc_001.json already exists
        assert 'tc_002.json' in file_path
    
    @patch('src.test_case_manager.Config')
    def test_backup_test_case(self, mock_config):
        """Test backing up a test case."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        backup_path = manager.backup_test_case('tc_001.json')
        assert os.path.exists(backup_path)
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = json.load(f)
        
        assert backup_content['title'] == 'Test Case 1'
    
    @patch('src.test_case_manager.Config')
    def test_get_test_case_by_id(self, mock_config):
        """Test getting a test case by ID."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        test_case = manager.get_test_case_by_id('tc_001')
        assert test_case is not None
        assert test_case['title'] == 'Test Case 1'
        
        # Non-existent ID should return None
        test_case = manager.get_test_case_by_id('nonexistent')
        assert test_case is None
    
    @patch('src.test_case_manager.Config')
    def test_list_test_cases(self, mock_config):
        """Test listing all test case files."""
        mock_config.TEST_CASES_DIR = self.test_cases_dir
        mock_config.SCHEMA_PATH = self.schema_path
        
        manager = TestCaseManager()
        
        test_cases = manager.list_test_cases()
        assert len(test_cases) == 1
        assert 'tc_001.json' in test_cases
