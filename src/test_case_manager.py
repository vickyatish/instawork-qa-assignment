import json
import os
import glob
from typing import List, Dict, Any, Optional
from jsonschema import validate, ValidationError
from .config import Config

class TestCaseManager:
    """Manages test case operations including reading, writing, and validation."""
    
    def __init__(self):
        """Initialize the test case manager."""
        self.test_cases_dir = Config.TEST_CASES_DIR
        self.schema_path = Config.SCHEMA_PATH
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the test case JSON schema."""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load schema from {self.schema_path}: {str(e)}")
    
    def load_all_test_cases(self) -> List[Dict[str, Any]]:
        """Load all existing test cases from the test_cases directory."""
        test_cases = []
        pattern = os.path.join(self.test_cases_dir, "*.json")
        
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    test_case = json.load(f)
                    # Add file path for reference
                    test_case['_file_path'] = file_path
                    test_case['_file_name'] = os.path.basename(file_path)
                    test_cases.append(test_case)
            except Exception as e:
                print(f"Warning: Failed to load test case from {file_path}: {str(e)}")
        
        return test_cases
    
    def load_test_case(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific test case by file name."""
        file_path = os.path.join(self.test_cases_dir, file_name)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                test_case = json.load(f)
                test_case['_file_path'] = file_path
                test_case['_file_name'] = file_name
                return test_case
        except Exception as e:
            raise Exception(f"Failed to load test case from {file_path}: {str(e)}")
    
    def validate_test_case(self, test_case: Dict[str, Any]) -> bool:
        """
        Validate a test case against the JSON schema.
        
        Args:
            test_case: The test case to validate
            
        Returns:
            True if valid, raises ValidationError if invalid
        """
        try:
            # Remove internal metadata fields before validation
            clean_test_case = {k: v for k, v in test_case.items() if not k.startswith('_')}
            validate(instance=clean_test_case, schema=self.schema)
            return True
        except ValidationError as e:
            raise ValidationError(f"Test case validation failed: {str(e)}")
    
    def save_test_case(self, test_case: Dict[str, Any], file_name: str) -> str:
        """
        Save a test case to a JSON file.
        
        Args:
            test_case: The test case to save
            file_name: The filename to save as
            
        Returns:
            The full path where the test case was saved
        """
        # Remove internal fields before saving
        clean_test_case = {k: v for k, v in test_case.items() if not k.startswith('_')}
        
        # Validate before saving
        self.validate_test_case(clean_test_case)
        
        file_path = os.path.join(self.test_cases_dir, file_name)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(clean_test_case, f, indent=2)
            return file_path
        except Exception as e:
            raise Exception(f"Failed to save test case to {file_path}: {str(e)}")
    
    def update_test_case(self, test_case_id: str, updated_test_case: Dict[str, Any]) -> str:
        """
        Update an existing test case.
        
        Args:
            test_case_id: The ID of the test case to update (e.g., "tc_001")
            updated_test_case: The updated test case data
            
        Returns:
            The full path where the test case was saved
        """
        # Find the existing test case file
        pattern = os.path.join(self.test_cases_dir, f"{test_case_id}.json")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            raise FileNotFoundError(f"No test case file found for ID: {test_case_id}")
        
        file_path = matching_files[0]
        file_name = os.path.basename(file_path)
        
        return self.save_test_case(updated_test_case, file_name)
    
    def create_new_test_case(self, test_case: Dict[str, Any], test_case_type: str) -> str:
        """
        Create a new test case file.
        
        Args:
            test_case: The test case to create
            test_case_type: Type of test case (positive, negative, edge)
            
        Returns:
            The full path where the test case was saved
        """
        # Generate a unique filename
        existing_files = glob.glob(os.path.join(self.test_cases_dir, "*.json"))
        max_number = 0
        
        for file_path in existing_files:
            file_name = os.path.basename(file_path)
            if file_name.startswith("tc_") and file_name.endswith(".json"):
                try:
                    number = int(file_name[3:-5])  # Extract number from "tc_XXX.json"
                    max_number = max(max_number, number)
                except ValueError:
                    continue
        
        new_number = max_number + 1
        file_name = f"tc_{new_number:03d}.json"
        
        return self.save_test_case(test_case, file_name)
    
    def backup_test_case(self, file_name: str) -> str:
        """
        Create a backup of an existing test case before modification.
        
        Args:
            file_name: The name of the test case file to backup
            
        Returns:
            The path to the backup file
        """
        original_path = os.path.join(self.test_cases_dir, file_name)
        backup_dir = os.path.join(self.test_cases_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_name = f"{os.path.splitext(file_name)[0]}_backup.json"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            with open(original_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            return backup_path
        except Exception as e:
            raise Exception(f"Failed to create backup of {file_name}: {str(e)}")
    
    def get_test_case_by_id(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a test case by its ID.
        
        Args:
            test_case_id: The ID of the test case (e.g., "tc_001")
            
        Returns:
            The test case data or None if not found
        """
        pattern = os.path.join(self.test_cases_dir, f"{test_case_id}.json")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            return None
        
        return self.load_test_case(os.path.basename(matching_files[0]))
    
    def list_test_cases(self) -> List[str]:
        """List all available test case files."""
        pattern = os.path.join(self.test_cases_dir, "*.json")
        files = glob.glob(pattern)
        return [os.path.basename(f) for f in files]
