import os
from typing import Dict, Any
from .config import Config

class PromptManager:
    """Manages prompt templates and loading."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.prompts_dir = "prompts"
    
    def load_prompt(self, template_name: str, **kwargs) -> str:
        """
        Load and format a prompt template.
        
        Args:
            template_name: Name of the template file (without .txt extension)
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        template_path = os.path.join(self.prompts_dir, f"{template_name}.txt")
        
        try:
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Format the template with provided variables
            return template.format(**kwargs)
            
        except FileNotFoundError:
            raise Exception(f"Prompt template not found: {template_path}")
        except Exception as e:
            raise Exception(f"Failed to load prompt template {template_name}: {str(e)}")
    
    def get_available_templates(self) -> list:
        """Get list of available prompt templates."""
        if not os.path.exists(self.prompts_dir):
            return []
        
        templates = []
        for file in os.listdir(self.prompts_dir):
            if file.endswith('.txt'):
                templates.append(file[:-4])  # Remove .txt extension
        
        return templates
